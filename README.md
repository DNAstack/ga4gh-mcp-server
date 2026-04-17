# GA4GH MCP Server

An [MCP](https://modelcontextprotocol.io) server that exposes the [GA4GH](https://www.ga4gh.org) ecosystem to AI clients such as Claude Desktop and Claude Code.

**Live endpoint:** `https://ga4gh-mcp-662019113068.us-central1.run.app/mcp/`

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

The hosted instance requires an API key. Contact the maintainers to request one, or [self-host](#self-hosting) and generate your own.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "ga4gh": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://ga4gh-mcp-662019113068.us-central1.run.app/mcp/"],
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
claude mcp add --transport http ga4gh https://ga4gh-mcp-662019113068.us-central1.run.app/mcp/ \
  --header "Authorization: Bearer YOUR_API_KEY"
```

Verify with:

```bash
claude mcp list
```

### Other MCP Clients

Use transport `streamable-http`, URL `https://ga4gh-mcp-662019113068.us-central1.run.app/mcp/`, and pass the API key as `Authorization: Bearer YOUR_API_KEY`.

---

## Self-Hosting

### Option 1 — Google Cloud Run (generous free tier)

Requires a Google Cloud project with billing enabled (2M requests/month and 360K GB-seconds free).

**1. Clone and install gcloud CLI**

```bash
git clone https://github.com/DNAstack/ga4gh-mcp-server.git
cd ga4gh-mcp-server
# Install gcloud: https://cloud.google.com/sdk/docs/install
gcloud auth login
```

**2. Generate an API key**

```bash
uv run ga4gh-mcp generate-key --user admin --description "my key"
```

Copy the `key_hash` value from the output.

**3. Deploy**

```bash
gcloud run deploy ga4gh-mcp \
  --source . \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GA4GH_MCP_API_KEY_HASH=sha256:<your_hash>,GA4GH_MCP_HOST=0.0.0.0,GA4GH_MCP_PORT=8080,GA4GH_MCP_TRANSPORT=streamable-http" \
  --port 8080
```

**4. Verify**

```bash
curl https://<your-service-url>/health
```

Expected: `{"status":"ok","tools":57}`

**5. Connect Claude Desktop or Claude Code** using your service URL and raw API key (the `gam_...` string, not the hash).

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
