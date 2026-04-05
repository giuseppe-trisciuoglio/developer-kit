#!/bin/bash
# Wrapper for NotebookLM MCP server
# Checks if uvx is available before starting the server

set -e

# Check if uvx is installed
if ! command -v uvx &> /dev/null; then
    echo "[NotebookLM MCP] ERROR: uvx is not installed. NotebookLM MCP requires uvx (from uv)." >&2
    echo "[NotebookLM MCP] Please install uv: https://github.com/astral-sh/uv#installation" >&2
    echo "[NotebookLM MCP] Then install notebooklm-mcp-cli: uv tool install notebooklm-mcp-cli" >&2
    exit 1
fi

# Check if notebooklm-mcp-cli is available
if ! uvx --from notebooklm-mcp-cli notebooklm-mcp --help &> /dev/null 2>&1; then
    echo "[NotebookLM MCP] ERROR: notebooklm-mcp-cli is not installed." >&2
    echo "[NotebookLM MCP] Please install it: uv tool install notebooklm-mcp-cli" >&2
    exit 1
fi

# Run the actual MCP server
uvx --from notebooklm-mcp-cli notebooklm-mcp "$@"
