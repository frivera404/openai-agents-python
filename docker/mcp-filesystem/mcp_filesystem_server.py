#!/usr/bin/env python3
"""
Simple MCP Filesystem Server
============================

A standalone MCP server that provides filesystem access via HTTP (streamable) or stdio.
"""

import argparse
import json
import os
from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("Filesystem Server")


@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List contents of a directory."""
    try:
        if not os.path.exists(path):
            return f"Directory '{path}' does not exist"

        items = os.listdir(path)
        result = []
        for item in items:
            full_path = os.path.join(path, item)
            item_type = "directory" if os.path.isdir(full_path) else "file"
            result.append(f"{item} ({item_type})")

        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file."""
    try:
        if not os.path.exists(path):
            return f"File '{path}' does not exist"

        if os.path.isdir(path):
            return f"'{path}' is a directory, not a file"

        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return f"File '{path}' is not a text file"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def get_file_info(path: str) -> str:
    """Get information about a file or directory."""
    try:
        if not os.path.exists(path):
            return f"Path '{path}' does not exist"

        stat = os.stat(path)
        info = {
            "path": path,
            "type": "directory" if os.path.isdir(path) else "file",
            "size": stat.st_size,
            "modified": stat.st_mtime,
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error getting file info: {str(e)}"


def main() -> None:
    """Parse CLI args and launch the MCP server."""
    parser = argparse.ArgumentParser(description="MCP Filesystem Server")
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument(
        "--http",
        action="store_true",
        help="Serve the tools via the Streamable HTTP transport (default).",
    )
    transport_group.add_argument(
        "--stdio",
        action="store_true",
        help="Serve the tools via the stdio transport.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (HTTP only).")
    parser.add_argument(
        "--port", type=int, default=3000, help="Port to bind (HTTP only)."
    )
    args = parser.parse_args()

    if args.stdio:
        print("Starting MCP Filesystem Server using stdio transport.")
        mcp.run(transport="stdio")
        return

    host = args.host
    port = args.port
    print(f"Starting MCP Filesystem Server on http://{host}:{port}")
    mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
