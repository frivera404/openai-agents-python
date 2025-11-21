import random
import logging

import requests
from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("Echo Server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    logger = logging.getLogger(__name__)
    logger.debug("[debug-server] add(%s, %s)", a, b)
    return a + b


@mcp.tool()
def get_secret_word() -> str:
    logger = logging.getLogger(__name__)
    logger.debug("[debug-server] get_secret_word()")
    return random.choice(["apple", "banana", "cherry"])


@mcp.tool()
def get_current_weather(city: str) -> str:
    logger = logging.getLogger(__name__)
    logger.debug("[debug-server] get_current_weather(%s)", city)

    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
