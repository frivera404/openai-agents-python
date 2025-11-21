import random

import logging
from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("Echo Server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    logging.getLogger(__name__).debug("[debug-server] add(%s, %s)", a, b)
    return a + b


@mcp.tool()
def get_secret_word() -> str:
    logging.getLogger(__name__).debug("[debug-server] get_secret_word()")
    return random.choice(["apple", "banana", "cherry"])


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
