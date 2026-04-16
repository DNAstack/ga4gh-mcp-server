# GA4GH MCP Server — Design Spec
**Date:** 2026-04-16  
**Status:** Approved

---

## Overview

A Model Context Protocol (MCP) server that exposes the full GA4GH ecosystem to AI clients (Claude Code, Claude Desktop, Vertex AI, Amazon Bedrock). It enables two tiers of capability:

- **Tier 1 — Registry discovery:** Browse and search the GA4GH Implementation Registry (registry.ga4gh.org) to find standards, services, implementations, and organizations.
- **Tier 2 — Standard interaction:** Talk directly to GA4GH-compliant services (DRS, WES, TES, TRS, Beacon, htsget, refget, Data Connect, Service Registry/Info) using their published OpenAPI-specified endpoints.

The server is a structural mirror of the `omics-ai-mcp-server`, using the same Python/MCP SDK/uvicorn/httpx/pydantic stack, the same config system, and the same deployment targets (GCP Cloud Run, AWS ECS Fargate, local stdio).

---

## Project Location

```
~/Development/ga4gh-mcp-server/
```

---

## Architecture

### Transport

Three transport modes in a single codebase, selected via config:

| Mode | Use case | Auth |
|------|----------|------|
| `stdio` | Local dev, Claude Code subprocess | None (single-user) |
| `streamable-http` | Remote deployment, multi-user | API key in `Authorization: Bearer` header |
| `sse` | Legacy HTTP streaming | API key |

### Project Structure

```
ga4gh-mcp-server/
├── src/ga4gh_mcp/
│   ├── __main__.py              # Entry point: `ga4gh-mcp [--transport ...]`, generate-key
│   ├── server.py                # MCP server setup, tool registration, health endpoint
│   ├── auth/
│   │   ├── api_key.py           # SHA-256 hashed key validation (timing-safe HMAC)
│   │   └── session.py           # Per-user session (TTL 480min, LRU max 1000)
│   ├── clients/
│   │   ├── base.py              # BaseClient: httpx, retry (3x, exponential), pagination
│   │   ├── registry.py          # GA4GH Implementation Registry client
│   │   ├── service_info.py      # GA4GH Service Info client
│   │   ├── service_registry.py  # GA4GH Service Registry client
│   │   ├── drs.py               # Data Repository Service v1.4 client
│   │   ├── wes.py               # Workflow Execution Service v1.1 client
│   │   ├── tes.py               # Task Execution Service v1.1 client
│   │   ├── trs.py               # Tool Registry Service v2 client
│   │   ├── beacon.py            # Beacon v2 client
│   │   ├── htsget.py            # htsget v1.3 client
│   │   ├── refget.py            # refget v2 client
│   │   └── data_connect.py      # Data Connect (Tables + Query) client
│   ├── tools/
│   │   ├── registry.py          # ToolContext, error helpers, tool dispatch
│   │   ├── registry_tools.py    # 12 tools: GA4GH Implementation Registry
│   │   ├── service_info_tools.py     # 1 tool
│   │   ├── service_registry_tools.py # 3 tools
│   │   ├── drs_tools.py         # 3 tools
│   │   ├── wes_tools.py         # 6 tools
│   │   ├── tes_tools.py         # 5 tools
│   │   ├── trs_tools.py         # 8 tools
│   │   ├── beacon_tools.py      # 7 tools
│   │   ├── htsget_tools.py      # 4 tools
│   │   ├── refget_tools.py      # 3 tools
│   │   └── data_connect_tools.py # 5 tools
│   └── config/
│       └── settings.py          # Pydantic settings models
├── config/
│   ├── server.yaml
│   ├── server.example.yaml
│   ├── api-keys.yaml
│   └── api-keys.example.yaml
├── deploy/
│   ├── gcp/
│   │   ├── cloudrun.yaml
│   │   ├── cloudbuild.yaml
│   │   └── terraform/
│   └── aws/
│       ├── ecs-task-def.json
│       └── terraform/
├── docs/
│   ├── connecting-claude-code.md
│   ├── deployment-gcp.md
│   └── deployment-aws.md
├── tests/
│   ├── test_registry_tools.py
│   ├── test_drs_tools.py
│   └── ... (one test file per tool module)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Tool Inventory (~57 tools)

### GA4GH Implementation Registry (`registry_tools.py`) — 12 tools

| Tool | Description |
|------|-------------|
| `list_standards` | List all GA4GH standards with optional filters (category, status) |
| `search_standards` | Free-text search across standards |
| `get_standard` | Get full details for a standard by ID |
| `list_services` | List services in the registry (filterable by standard, organization) |
| `search_services` | Search services by keyword |
| `get_service` | Get full details for a registered service by ID |
| `list_implementations` | List software implementations (filterable by standard) |
| `search_implementations` | Search implementations by keyword |
| `get_implementation` | Get full details for an implementation by ID |
| `list_organizations` | List organizations registered in the GA4GH registry |
| `search_organizations` | Search organizations by keyword |
| `get_organization` | Get full details for an organization by ID |

### Service Info (`service_info_tools.py`) — 1 tool

| Tool | Description |
|------|-------------|
| `get_service_info` | GET `{service_url}/service-info` on any GA4GH-compliant service |

### Service Registry (`service_registry_tools.py`) — 3 tools

| Tool | Description |
|------|-------------|
| `list_registered_services` | List all services in a Service Registry instance |
| `get_registered_service` | Get a specific service by ID from a Service Registry |
| `get_service_registry_info` | Get service-info for a Service Registry endpoint |

### DRS — Data Repository Service (`drs_tools.py`) — 3 tools

| Tool | Description |
|------|-------------|
| `get_drs_object` | Retrieve DRS object metadata (checksums, size, access methods) |
| `get_drs_access_url` | Get a signed/presigned access URL for a DRS object |
| `get_drs_service_info` | Get service-info for a DRS endpoint |

### WES — Workflow Execution Service (`wes_tools.py`) — 6 tools

| Tool | Description |
|------|-------------|
| `get_wes_service_info` | Get service-info and supported workflow types |
| `list_wes_runs` | List workflow runs (filterable by state) |
| `get_wes_run` | Get status and details for a specific run |
| `submit_wes_run` | Submit a new workflow run (CWL, WDL, Nextflow, etc.) |
| `cancel_wes_run` | Cancel a running workflow |
| `get_wes_run_log` | Retrieve task logs for a completed/running run |

### TES — Task Execution Service (`tes_tools.py`) — 5 tools

| Tool | Description |
|------|-------------|
| `get_tes_service_info` | Get service-info for a TES endpoint |
| `list_tes_tasks` | List tasks with optional name/state filters |
| `get_tes_task` | Get full details for a task (with view: MINIMAL, BASIC, FULL) |
| `create_tes_task` | Create and submit a new computational task |
| `cancel_tes_task` | Cancel a running task |

### TRS — Tool Registry Service (`trs_tools.py`) — 8 tools

| Tool | Description |
|------|-------------|
| `get_trs_service_info` | Get service-info for a TRS endpoint |
| `list_trs_tools` | List tools/workflows (filterable by name, toolClass, descriptorType) |
| `get_trs_tool` | Get metadata for a specific tool by ID |
| `list_trs_tool_versions` | List all versions of a tool |
| `get_trs_tool_version` | Get metadata for a specific tool version |
| `get_trs_descriptor` | Get the workflow descriptor (CWL, WDL, Nextflow, Galaxy) |
| `get_trs_files` | List all files for a tool version |
| `list_trs_tool_classes` | List all tool classes (Workflow, CommandLineTool, etc.) |

### Beacon v2 (`beacon_tools.py`) — 7 tools

| Tool | Description |
|------|-------------|
| `get_beacon_info` | Get Beacon metadata and capabilities |
| `get_beacon_configuration` | Get Beacon configuration and entry types |
| `get_beacon_map` | Get map of implemented Beacon endpoints |
| `list_beacon_entry_types` | List all entry types (variants, individuals, biosamples, etc.) |
| `get_beacon_filtering_terms` | Get accepted filtering terms for queries |
| `query_beacon_variants` | Query for genomic variants by position/allele/gene |
| `query_beacon_individuals` | Query for individuals matching phenotypic/clinical criteria |

### htsget (`htsget_tools.py`) — 4 tools

| Tool | Description |
|------|-------------|
| `get_htsget_reads` | Retrieve reads for a genomic region (BAM/CRAM) |
| `get_htsget_variants` | Retrieve variants for a genomic region (VCF/BCF) |
| `get_htsget_reads_post` | POST-based reads retrieval (multiple ranges) |
| `get_htsget_variants_post` | POST-based variants retrieval (multiple ranges) |

### refget (`refget_tools.py`) — 3 tools

| Tool | Description |
|------|-------------|
| `get_refget_service_info` | Get service-info for a refget endpoint |
| `get_refget_metadata` | Get metadata for a reference sequence by ID |
| `get_refget_sequence` | Retrieve a reference sequence or subsequence by ID and range |

### Data Connect (`data_connect_tools.py`) — 5 tools

| Tool | Description |
|------|-------------|
| `get_data_connect_service_info` | Get service-info for a Data Connect endpoint |
| `list_data_connect_tables` | List all tables available at a Data Connect endpoint |
| `get_data_connect_table_info` | Get schema and metadata for a specific table |
| `get_data_connect_table_data` | Retrieve paginated rows from a table |
| `query_data_connect` | Execute a SQL query against a Data Connect endpoint |

---

## Data Flow

### Typical session
```
1. User: "Find all WES services in the GA4GH registry"
   → list_services(standard="WES")
   → GET https://registry.ga4gh.org/v1/services?standard=WES
   ← list of services with base_urls

2. User: "What workflows are available on the EBI TRS at https://wwwdev.ebi.ac.uk/mi/impc/dev/trs"
   → list_trs_tools(service_url="https://wwwdev.ebi.ac.uk/mi/impc/dev/trs")
   → GET {service_url}/ga4gh/trs/v2/tools
   ← tool list

3. User: "Get the WDL descriptor for tool biocontainers/samtools version 1.15"
   → get_trs_descriptor(service_url="...", id="biocontainers/samtools", version_id="1.15", type="WDL")
   → GET {service_url}/ga4gh/trs/v2/tools/biocontainers%2Fsamtools/versions/1.15/WDL/descriptor
   ← WDL source

4. User: "Submit that WDL to WES at https://wes.emu.ebi.ac.uk"
   → submit_wes_run(service_url="https://wes.emu.ebi.ac.uk", workflow_url="...", ...)
   → POST {service_url}/ga4gh/wes/v1/runs
   ← run_id
```

### Key design decisions

- **`service_url` as first parameter on all Tier 2 tools** — no pre-configured networks; users discover URLs via registry tools then call service tools directly.
- **`registry_base_url` in `server.yaml`** — defaults to `https://registry.ga4gh.org/v1`, overridable for private/mirror registries.
- **No OAuth in v1** — all tools use public endpoints. `base.py` accepts an optional `bearer_token` kwarg threaded through from tool parameters for services that require it, but no device-code flow or session token storage is implemented.
- **Pagination** — all list tools expose `page_size` (default 100) and `page_token`; BaseClient handles both cursor-based and offset-based pagination.

---

## Configuration

### `server.yaml`
```yaml
server:
  host: 0.0.0.0
  port: 8080
  transport: streamable-http   # stdio | streamable-http | sse
  log_level: info

security:
  api_keys_file: /app/config/api-keys.yaml

registry:
  base_url: https://registry.ga4gh.org/v1
```

### `api-keys.yaml`
```yaml
keys:
  - user_id: alice
    key_hash: "sha256:<64-char-hex>"
    description: "Alice's Claude Code key"
    created_at: "2026-04-16"
```

API keys are generated with: `ga4gh-mcp generate-key --user alice --description "..."`  
Format: `gam_<64-char-hex>` (32 cryptographically random bytes, hex-encoded)  
Stored as SHA-256 hash only. Validated with `hmac.compare_digest`.

---

## Error Handling

All errors return a structured dict, never raw exceptions:

```json
{"error": {"code": "NOT_FOUND", "message": "DRS object drs://example.org/abc123 not found"}}
```

| HTTP status | Error code | Notes |
|-------------|-----------|-------|
| 400 | `INVALID_REQUEST` | Upstream error message forwarded |
| 401/403 | `AUTH_REQUIRED` | Hint: supply bearer_token parameter |
| 404 | `NOT_FOUND` | Resource identifier included |
| 429 | auto-retry | 3 attempts, exponential backoff, then `RATE_LIMITED` |
| 500-504 | auto-retry | 3 attempts, then `SERVICE_ERROR` |
| Network error | `CONNECTION_ERROR` | Service URL included |

---

## Deployment

### Local stdio (Claude Code)
```bash
claude mcp add ga4gh \
  --transport stdio \
  -- uv run --directory ~/Development/ga4gh-mcp-server ga4gh-mcp --transport stdio
```

### GCP Cloud Run
- Container: built via `deploy/gcp/cloudbuild.yaml` → Artifact Registry
- Service: `deploy/gcp/cloudrun.yaml` — 2 CPU, 1 GB RAM, 1–10 replicas
- Config: mounted as Cloud Run secrets
- Connect: `claude mcp add ga4gh --transport http --url https://<service>.run.app/mcp --header "Authorization: Bearer <key>"`

### AWS ECS Fargate
- Task definition: `deploy/aws/ecs-task-def.json` — 1 vCPU, 2 GB RAM
- Config: injected from AWS Secrets Manager
- ALB fronts the service on port 443

### Docker Compose (local HTTP)
```bash
docker compose up
claude mcp add ga4gh --transport http --url http://localhost:8080/mcp --header "Authorization: Bearer <key>"
```

---

## Testing

- One test file per tool module in `tests/`
- `pytest-httpx` / `respx` for mocking HTTP responses
- Each tool tested for: happy path, 404, 400, network error, pagination
- `pytest-asyncio` for async tool handlers
- Coverage target: 80%+

---

## Dependencies

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]>=1.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0",
    "uvicorn>=0.30.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-httpx>=0.30.0",
    "respx>=0.21.1",
    "ruff>=0.4.0",
    "coverage>=7.0.0",
]
```

---

## Out of Scope (v1)

- OAuth device-code flow / per-service authentication (planned for v2)
- GA4GH Passport / Visa support
- Write operations on the GA4GH Registry (POST/PUT/DELETE)
- VRS / Phenopackets (schema standards, no REST API surface)
- WebSocket transports
