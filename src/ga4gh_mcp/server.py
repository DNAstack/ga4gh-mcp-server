"""MCP server setup — stdio, streamable-http, and sse transports."""

from __future__ import annotations

import contextlib
import json
import logging
import sys
from collections.abc import AsyncIterator

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from ga4gh_mcp.auth.api_key import ApiKeyValidator
from ga4gh_mcp.auth.session import SessionManager
from ga4gh_mcp.config.settings import Settings, load_settings
from ga4gh_mcp.tools.registry import ToolContext

logger = logging.getLogger(__name__)

_settings: Settings | None = None
_session_manager: SessionManager | None = None
_tool_handlers: dict = {}


def _register_tools(server: Server, settings: Settings) -> None:
    """Import and register all tool modules."""
    all_tools: dict = {}

    # Import tool modules — each exposes a register() -> dict[str, tuple[Tool, callable]]
    tool_modules = []
    for mod_name in [
        "ga4gh_mcp.tools.registry_tools",
        "ga4gh_mcp.tools.service_info_tools",
        "ga4gh_mcp.tools.service_registry_tools",
        "ga4gh_mcp.tools.drs_tools",
        "ga4gh_mcp.tools.wes_tools",
        "ga4gh_mcp.tools.tes_tools",
        "ga4gh_mcp.tools.trs_tools",
        "ga4gh_mcp.tools.beacon_tools",
        "ga4gh_mcp.tools.htsget_tools",
        "ga4gh_mcp.tools.refget_tools",
        "ga4gh_mcp.tools.data_connect_tools",
    ]:
        try:
            import importlib
            mod = importlib.import_module(mod_name)
            tool_modules.append(mod)
        except ImportError:
            logger.warning(f"Tool module {mod_name} not yet available, skipping")

    for mod in tool_modules:
        all_tools.update(mod.register())

    global _tool_handlers
    _tool_handlers = all_tools

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [tool_def for tool_def, _ in _tool_handlers.values()]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name not in _tool_handlers:
            error = {"error": {"code": "INTERNAL_ERROR", "message": f"Unknown tool: {name}"}}
            return [TextContent(type="text", text=json.dumps(error))]

        _, handler = _tool_handlers[name]
        session = _session_manager.get_or_create("default")
        ctx = ToolContext(session=session, settings=settings)

        try:
            result = await handler(ctx, **arguments)
            if isinstance(result, str):
                return [TextContent(type="text", text=result)]
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        except Exception as e:
            logger.exception(f"Tool {name} failed")
            error = {"error": {"code": "INTERNAL_ERROR", "message": str(e)}}
            return [TextContent(type="text", text=json.dumps(error))]


def _build_starlette_app(server: Server, settings: Settings) -> "Starlette":
    """Build a Starlette ASGI app for streamable-http or sse transport."""
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response
    from starlette.routing import Mount, Route

    transport = settings.server.transport

    if transport == "streamable-http":
        session_manager = StreamableHTTPSessionManager(
            app=server,
            stateless=True,  # stateless — auth handled at the tool layer
        )

        @contextlib.asynccontextmanager
        async def lifespan(app: Starlette) -> AsyncIterator[None]:
            async with session_manager.run():
                yield

        async def handle_mcp(scope, receive, send) -> None:
            # Optional API key check
            if settings.api_keys:
                request = Request(scope, receive)
                auth_header = request.headers.get("authorization", "")
                raw_key = auth_header.removeprefix("Bearer ").strip()
                validator = ApiKeyValidator([k.model_dump() for k in settings.api_keys])
                if not validator.validate(raw_key):
                    response = Response("Unauthorized", status_code=401)
                    await response(scope, receive, send)
                    return
            await session_manager.handle_request(scope, receive, send)

        async def healthz(request: Request) -> JSONResponse:
            return JSONResponse({"status": "ok", "tools": len(_tool_handlers)})

        return Starlette(
            lifespan=lifespan,
            routes=[
                Route("/health", healthz),
                Mount("/mcp", app=handle_mcp),
            ],
        )

    else:  # sse
        sse = SseServerTransport("/mcp/messages")

        async def handle_sse(request: Request) -> Response:
            if settings.api_keys:
                auth_header = request.headers.get("authorization", "")
                raw_key = auth_header.removeprefix("Bearer ").strip()
                validator = ApiKeyValidator([k.model_dump() for k in settings.api_keys])
                if not validator.validate(raw_key):
                    return Response("Unauthorized", status_code=401)
            async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
                await server.run(r, w, server.create_initialization_options())
            return Response()

        async def healthz(request: Request) -> JSONResponse:
            return JSONResponse({"status": "ok", "tools": len(_tool_handlers)})

        from starlette.applications import Starlette
        from starlette.routing import Route
        return Starlette(routes=[
            Route("/health", healthz),
            Route("/mcp/sse", handle_sse),
            Mount("/mcp/messages", app=sse.handle_post_message),
        ])


def main() -> None:
    """Run the MCP server — transport selected from config."""
    import asyncio

    global _settings, _session_manager
    _settings = load_settings()

    log_level = _settings.server.log_level.upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    logger.info(f"Starting GA4GH MCP Server, transport={_settings.server.transport}")

    _session_manager = SessionManager(
        ttl_minutes=_settings.server.session_ttl_minutes,
        max_sessions=_settings.server.max_sessions,
    )

    server = Server("ga4gh-mcp-server")
    _register_tools(server, _settings)
    logger.info(f"Registered {len(_tool_handlers)} tools")

    if _settings.server.transport == "stdio":
        async def run_stdio():
            async with stdio_server() as (read, write):
                await server.run(read, write, server.create_initialization_options())

        asyncio.run(run_stdio())

    else:
        import uvicorn
        app = _build_starlette_app(server, _settings)
        uvicorn.run(
            app,
            host=_settings.server.host,
            port=_settings.server.port,
            log_level=_settings.server.log_level.lower(),
        )
