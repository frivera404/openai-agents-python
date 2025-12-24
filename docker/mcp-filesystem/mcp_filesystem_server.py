#!/usr/bin/env python3
"""
Simple MCP Filesystem Server
============================

A standalone MCP server that provides filesystem access via HTTP (streamable) or stdio.
"""

import argparse
import json
import os
from typing import Any, Dict, List
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


@mcp.tool()
def search_files(path: str = ".", query: str = "", max_results: int = 20) -> str:
    """Search for a text query in files under a directory.

    Returns a JSON array of matches: {"path": str, "line": int, "text": str}
    """

    if not query:
        return json.dumps([], indent=2)

    if not os.path.exists(path):
        return f"Path '{path}' does not exist"

    root = path if os.path.isdir(path) else os.path.dirname(path) or "."
    query_lower = query.lower()

    matches: List[Dict[str, Any]] = []
    max_bytes = 2 * 1024 * 1024  # 2MB safety cap per file
    skip_ext = {
        ".exe",
        ".dll",
        ".pyd",
        ".so",
        ".dylib",
        ".bin",
        ".dat",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".rar",
        ".mp3",
        ".mp4",
        ".mov",
        ".avi",
        ".wav",
        ".flac",
    }

    try:
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext in skip_ext:
                    continue
                try:
                    if os.path.getsize(full_path) > max_bytes:
                        continue
                except Exception:
                    continue

                # Quick binary sniff: skip files that contain NUL bytes.
                try:
                    with open(full_path, "rb") as bf:
                        if b"\x00" in bf.read(2048):
                            continue
                except Exception:
                    continue

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, line in enumerate(f, start=1):
                            if query_lower in line.lower():
                                matches.append(
                                    {
                                        "path": full_path,
                                        "line": idx,
                                        "text": line.strip()[:400],
                                    }
                                )
                                if len(matches) >= max_results:
                                    return json.dumps(matches, indent=2)
                except Exception:
                    continue

        return json.dumps(matches, indent=2)
    except Exception as e:
        return f"Error searching files: {str(e)}"


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

    # HTTP transport; host/port options are currently unused with this FastMCP version.
    print("Starting MCP Filesystem Server using HTTP (streamable) transport.")
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
