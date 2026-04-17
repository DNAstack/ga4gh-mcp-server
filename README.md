# GA4GH MCP Server

An [MCP](https://modelcontextprotocol.io) server that exposes the [GA4GH](https://www.ga4gh.org) ecosystem to AI clients such as Claude Desktop and Claude Code.

**Live endpoint:** `https://ga4gh-mcp.fly.dev/mcp/`

## Tools (57 total)

| GA4GH Service | Tools |
|---|---|
| Registry | 12 tools — search organizations, standards, services |
| WES (Workflow Execution Service) | 6 tools — list, submit, cancel, monitor runs |
| TES (Task Execution Service) | 5 tools — create and manage compute tasks |
| TRS (Tool Registry Service) | 8 tools — search tools, versions, descriptors |
| Beacon v2 | 7 tools — query genomic variants and biosamples |
| DRS (Data Repository Service) | 3 tools — resolve data objects |
| htsget | 4 tools — stream genomic reads and variants |
| refget | 3 tools — retrieve reference sequences |
| Data Connect | 5 tools — SQL queries over genomic tables |
| Service Info / Registry | 4 tools — discover service metadata |

## Connect via the Hosted Instance

The hosted instance at `https://ga4gh-mcp.fly.dev` requires an API key. Contact the maintainers to request one, or [self-host](#self-hosting) and generate your own.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "ga4gh": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://ga4gh-mcp.fly.dev/mcp/"],
      "env": {
        "MCP_REMOTE_HEADER_AUTHORIZATION": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

### Claude Code (CLI)

```bash
claude mcp add --transport http ga4gh https://ga4gh-mcp.fly.dev/mcp/ \
  --header "Authorization: Bearer YOUR_API_KEY"
```

Verify with:

```bash
claude mcp list
```

### Other MCP Clients

Use transport `streamable-http`, URL `https://ga4gh-mcp.fly.dev/mcp/`, and pass the API key as `Authorization: Bearer YOUR_API_KEY`.

---

## Self-Hosting

### Option 1 — Fly.io (free tier)

**1. Clone and install Fly CLI**

```bash
git clone https://github.com/DNAstack/ga4gh-mcp-server.git
cd ga4gh-mcp-server
brew install flyctl   # or: curl -L https://fly.io/install.sh | sh
fly auth login
```

**2. Create your app**

```bash
fly launch --no-deploy   # accept defaults, note your app name
```

**3. Generate an API key**

```bash
uv run ga4gh-mcp generate-key --user admin --description "my key"
```

Copy the `key_hash` value from the output.

**4. Set the secret and deploy**

```bash
fly secrets set GA4GH_MCP_API_KEY_HASH="sha256:<your_hash>"
fly deploy
```

**5. Verify**

```bash
curl https://<your-app>.fly.dev/health
```

Expected: `{"status":"ok","tools":57}`

**6. Connect Claude Desktop or Claude Code** using your app URL and raw API key (the `gam_...` string, not the hash).

### Option 2 — Docker (local or any cloud)

```bash
docker build -t ga4gh-mcp .

# Generate a key
docker run --rm ga4gh-mcp uv run ga4gh-mcp generate-key --user admin

# Run with the hash from the previous step
docker run -p 8080:8080 \
  -e GA4GH_MCP_API_KEY_HASH="sha256:<your_hash>" \
  ga4gh-mcp
```

Then use `http://localhost:8080/mcp/` as the endpoint.

### Option 3 — stdio (no auth, local only)

Install directly with `uv`:

```bash
uv tool install ga4gh-mcp-server
```

Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "ga4gh": {
      "command": "ga4gh-mcp",
      "env": {
        "GA4GH_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Or with `uvx` (no install step):

```json
{
  "mcpServers": {
    "ga4gh": {
      "command": "uvx",
      "args": ["ga4gh-mcp-server"],
      "env": {
        "GA4GH_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## Configuration Reference

| Environment Variable | Default | Description |
|---|---|---|
| `GA4GH_MCP_TRANSPORT` | `streamable-http` | Transport: `stdio`, `streamable-http`, or `sse` |
| `GA4GH_MCP_HOST` | `0.0.0.0` | Bind address (HTTP transports) |
| `GA4GH_MCP_PORT` | `8080` | Port (HTTP transports) |
| `GA4GH_MCP_LOG_LEVEL` | `info` | Log level |
| `GA4GH_MCP_API_KEY_HASH` | _(unset)_ | SHA-256 hash of an API key; disables open access when set |
| `GA4GH_MCP_CONFIG_DIR` | `./config` | Directory for `server.yaml` and `api-keys.yaml` |

### server.yaml (optional)

```yaml
server:
  transport: streamable-http
  port: 8080
  log_level: info

registry:
  base_url: https://registry.ga4gh.org/v1
```

### api-keys.yaml (optional, multi-key deployments)

```yaml
keys:
  - user_id: alice
    key_hash: "sha256:..."
    description: "Alice's key"
```

Generate key hashes with:

```bash
ga4gh-mcp generate-key --user alice --description "Alice's key"
```

---

## License

Apache 2.0
