# MCP Server Configurations

This document outlines different ways to configure MCP servers with the OpenAI Agents SDK.

## Available MCP Server Types

### 1. HTTP Streamable MCP
```python
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

params: MCPServerStreamableHttpParams = {
    "url": "https://your-mcp-server.com/mcp",
    "headers": {"Authorization": "Bearer your-token"},
    "timeout": 30,
}
mcp = MCPServerStreamableHttp(params=params, name="cloud-mcp")
```

### 2. Stdio MCP with Docker Gateway
```python
from agents.mcp import MCPServerStdio, MCPServerStdioParams

params: MCPServerStdioParams = {
    "command": "docker",
    "args": ["mcp", "gateway", "run"],
    "env": {},
}
mcp = MCPServerStdio(params=params, name="docker-mcp-gateway")
```

### 3. Stdio MCP with Local Filesystem Server
```python
from agents.mcp import MCPServerStdio, MCPServerStdioParams

params: MCPServerStdioParams = {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-filesystem", "/path/to/directory"],
    "env": {},
}
mcp = MCPServerStdio(params=params, name="local-filesystem")
```

## Configuration JSON Format

For external configuration, you can use JSON format:

```json
{
  "servers": {
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"],
      "type": "stdio"
    },
    "CLOUD_MCP": {
      "url": "https://your-mcp-server.com/mcp",
      "headers": {"Authorization": "Bearer your-token"},
      "type": "http"
    },
    "mcp-cloud.ai - wikipedia-mcp": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "--header",
        "Authorization:${AUTH_HEADER}",
        "https://wiki-1763000517527.server.mcp-cloud.ai/sse"
      ],
      "env": {
        "AUTH_HEADER": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NDZhNDM3NS01OTM1LTQyZDQtOGNiNC03NWU0NjNlZmRhNDciLCJlbWFpbCI6InJpdmVyYWYzMEBnbWFpbC5jb20iLCJuYW1lIjoiRmVybmFuZG8g4oCcRGFkZHlHcHTigJ0gUml2ZXJhIiwidGllciI6IkZyZWUgVGllciIsImp0aSI6IjdkZThhOThhODkzOWRhYzRkYTFkZDRjYzIxZTM0N2ExIiwiaWF0IjoxNzYzMDAwMTM1fQ.YiWT_ZpAYcAcvQOuQ8lWM0oduoSNikh7UJ6MCCrqvwo"
      }
    }
  }
}
```

## Usage in Agent

```python
agent = Agent(
    name="MCP Agent",
    instructions="You have access to MCP tools.",
    mcp_servers=[mcp_server],
    model=FakeModel(),  # Or your preferred model
)
```

## Prerequisites

- For Docker MCP: Docker installed with MCP gateway image
- For HTTP MCP: Valid server URL and authentication
- For Stdio MCP: Appropriate CLI tools installed (npx, etc.)

## Testing

Run the examples:
- `python docker_mcp_example.py` - Docker gateway
- `python local_stdio_mcp_example.py` - Local stdio (may require roots configuration)