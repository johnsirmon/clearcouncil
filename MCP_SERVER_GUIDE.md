# ClearCouncil MCP Server Guide

The ClearCouncil **Model Context Protocol (MCP) server** exposes
local-government transparency data as structured tools that any MCP-compatible
AI assistant (Claude Desktop, Cursor, Continue, …) can call directly —
no CLI knowledge required.

---

## What is MCP?

[Model Context Protocol](https://modelcontextprotocol.io/) is an open standard
that lets AI assistants connect to external data sources and tools through a
well-defined interface.  Once the ClearCouncil MCP server is running, an AI
can call tools like `lookup_sc_representative` or `explain_terms` and get
structured JSON back.

---

## Installation

```bash
# 1. Clone / navigate to the repo
cd clearcouncil

# 2. Install base requirements
pip install -r requirements.txt

# 3. Install MCP extra
pip install -r requirements-mcp.txt
# or: pip install -e ".[mcp]"
```

---

## Starting the Server

### stdio transport (default — works with Claude Desktop and most MCP clients)

```bash
python clearcouncil_mcp.py
```

Or after a `pip install -e .`:

```bash
clearcouncil-mcp
```

The server communicates over **stdin/stdout** (the MCP stdio transport), so it
is intended to be launched by an MCP client rather than run interactively.

### Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Optional¹ | Required only for `search_documents` and `analyze_voting` |
| `CLEARCOUNCIL_LOG_LEVEL` | No | `DEBUG` / `INFO` / `WARNING` / `ERROR` (default: `WARNING`) |

¹ Tools that *don't* need an API key: `list_councils`, `explain_terms`,
`lookup_sc_representative`, `list_sc_representatives`,
`lookup_nc_representative`, `list_nc_representatives`, `discover_data_sources`.

---

## Claude Desktop Configuration

Add the server to `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "clearcouncil": {
      "command": "python",
      "args": ["/absolute/path/to/clearcouncil/clearcouncil_mcp.py"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

After saving, restart Claude Desktop.  You should see "clearcouncil" listed
under **MCP Servers** in the app settings.

---

## Available Tools

### `list_councils`

List all configured council identifiers.

```
list_councils()
→ [{"id": "york_county_sc", "name": "York County, SC Council"}, …]
```

---

### `explain_terms`

Look up municipal government terminology.

```
explain_terms(terms=["movant", "rezoning"])
explain_terms(terms=["all"])              # overview of all categories
explain_terms(terms=[], category="voting")  # all terms in a category
```

---

### `lookup_sc_representative`

Find South Carolina representatives by name, district, or county.

```
lookup_sc_representative(query="Smith")
lookup_sc_representative(query="42")                        # district number
lookup_sc_representative(query="York", county="York")       # county roster
lookup_sc_representative(query="Smith", chamber="senate")
```

---

### `list_sc_representatives`

List SC representatives with optional filters.

```
list_sc_representatives()                            # summary stats
list_sc_representatives(chamber="county_council")
list_sc_representatives(county="Richland")
list_sc_representatives(chamber="house", refresh=True)
```

---

### `lookup_nc_representative`

Find North Carolina representatives by name, district, or county.

```
lookup_nc_representative(query="Johnson")
lookup_nc_representative(query="37")               # district number
lookup_nc_representative(query="", county="Wake")  # county roster
```

---

### `list_nc_representatives`

List NC representatives with optional filters.

```
list_nc_representatives()                        # summary stats
list_nc_representatives(chamber="senate")
list_nc_representatives(county="Mecklenburg")
```

---

### `discover_data_sources`

Browse the SC / NC public data-source catalog.

```
discover_data_sources()
discover_data_sources(state="SC")
discover_data_sources(blocked_only=True)
discover_data_sources(api_only=True)
discover_data_sources(include_municipalities=True)
```

Returns details on portal type, URLs, known access blockers, and
legally-permissible workarounds for each county.

---

### `search_documents` *(requires OPENAI_API_KEY + processed documents)*

Semantic / keyword search over processed council meeting minutes.

```
search_documents(council_id="york_county_sc", query="rezoning Main Street", limit=5)
```

Documents must first be processed with `clearcouncil process-pdfs <council_id>`.

---

### `analyze_voting` *(requires OPENAI_API_KEY + processed documents)*

Analyse representative voting patterns for a time range.

```
analyze_voting(
    council_id="york_county_sc",
    representative="District 2",
    time_range="last year",
)
analyze_voting(
    council_id="york_county_sc",
    representative="John Smith",
    time_range="2023-01-01 to 2024-01-01",
    compare_with=["Jane Doe", "Bob Jones"],
)
```

---

## Example Conversation (Claude Desktop)

> **You:** Who are the county council members for York County, SC?
>
> **Claude:** *[calls `lookup_sc_representative(query="York", county="York", chamber="county_council")`]*
>
> Here are the York County, SC Council members: …

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `ImportError: No module named 'mcp'` | Run `pip install -r requirements-mcp.txt` |
| `OPENAI_API_KEY environment variable is required` | Set the key in `.env` or the Claude Desktop config |
| Server starts but Claude can't find it | Verify the absolute path in `claude_desktop_config.json` |
| No documents found for `search_documents` | Run `clearcouncil process-pdfs <council_id>` first |
