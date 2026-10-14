"""Compatibility entry point for deployments using the former MCP command."""

from .odoo.mcp_server import main


if __name__ == "__main__":
    main()
