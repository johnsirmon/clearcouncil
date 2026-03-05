"""
ClearCouncil MCP Server entry point.

Run this script to start the ClearCouncil Model Context Protocol server.
The server exposes ClearCouncil's capabilities as MCP tools that AI
assistants (e.g. Claude Desktop) can call directly.

Usage:
    python clearcouncil_mcp.py

See MCP_SERVER_GUIDE.md for full setup and usage instructions.
"""

from src.clearcouncil.mcp.server import run

if __name__ == "__main__":
    run()
