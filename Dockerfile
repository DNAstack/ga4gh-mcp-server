FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies (no dev extras)
RUN uv sync --no-dev --locked

# Config directory — mount secrets here at runtime
RUN mkdir -p /app/config

# Default transport is streamable-http; override via GA4GH_MCP_TRANSPORT env var
ENV GA4GH_MCP_CONFIG_DIR=/app/config
ENV GA4GH_MCP_HOST=0.0.0.0
ENV GA4GH_MCP_PORT=8080
ENV GA4GH_MCP_TRANSPORT=streamable-http

EXPOSE 8080

CMD ["uv", "run", "ga4gh-mcp"]
