# MCP Server Integration Guide

## Server Status
**URL**: `https://18268932-0807663c6d1468.router.cloudmcp.run/mcp`  # Updated URL
**Status**: ✅ Server is responding and requires authentication (not Bearer tokens)

## Alternative Authentication Methods

Since CloudMCP doesn't use Bearer tokens, here are the alternative authentication methods you can try:

### 1. API Key in Custom Headers
Most common alternative to Bearer tokens:

```python
# Set environment variable
export MCP_API_KEY="your_actual_api_key"

# Or use in headers directly
headers = {"X-API-Key": "your_actual_api_key"}
```

### 2. Alternative Header Names
Try these different header names:

```python
# Option A: X-Auth-Token
headers = {"X-Auth-Token": "your_token"}

# Option B: X-API-Token
headers = {"X-API-Token": "your_token"}

# Option C: Custom MCP header
headers = {"X-MCP-Key": "your_key"}
```

### 3. Token Authentication (Non-Bearer)
Some services use "Token" instead of "Bearer":

```python
headers = {"Authorization": "Token your_actual_token"}
```

### 4. Query Parameter Authentication
Some APIs accept keys as URL parameters:

```python
# Add to URL
url = "https://18268932-0807663c6d1468.router.cloudmcp.run/mcp?api_key=your_key"
```

### 5. Basic Authentication
If the service requires username/password:

```python
import base64

username = "your_username"
password = "your_password"
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

headers = {"Authorization": f"Basic {credentials}"}
```

## Testing Authentication

Run the comprehensive test script to find the correct authentication method:

```bash
python test_user_mcp_server.py
```

This script will test multiple authentication methods and tell you which one works.

## Configuration Examples

### Option 1: API Key Header (Most Likely)
```python
from agents.mcp import MCPServerStreamableHttp

MCP_SERVER_CONFIG = {
    "url": "https://18268932-0807663c6d1468.router.cloudmcp.run/mcp",
    "headers": {
        "X-API-Key": "YOUR_ACTUAL_API_KEY",  # Replace with real key
    },
    "timeout": 30,
}

mcp_server = MCPServerStreamableHttp(
    params=MCP_SERVER_CONFIG,
    name="CloudMCPServer",
    cache_tools_list=True,
)
```

### Option 2: Custom Token Header
```python
MCP_SERVER_CONFIG = {
    "url": "https://18268932-0807663c6d1468.router.cloudmcp.run/mcp",
    "headers": {
        "X-Auth-Token": "YOUR_ACTUAL_TOKEN",  # Replace with real token
    },
    "timeout": 30,
}
```

### Option 3: Query Parameter
```python
MCP_SERVER_CONFIG = {
    "url": "https://18268932-0807663c6d1468.router.cloudmcp.run/mcp?api_key=YOUR_ACTUAL_KEY",
    "headers": {},
    "timeout": 30,
}
```

## Next Steps

1. **Get your authentication credentials** from your CloudMCP account/dashboard
2. **Test with the script**: `python test_user_mcp_server.py`
3. **Update configuration** in `mcp_config.py` with the working method
4. **Test integration** with your OpenAI Agents workflow

## Troubleshooting

- **401 Unauthorized**: Wrong authentication credentials
- **403 Forbidden**: Authentication works but you don't have permission
- **503 Service Unavailable**: Server is temporarily down
- **All methods fail**: Check if server is accessible or contact CloudMCP support

## Environment Variables

Set these environment variables for easy configuration:

```bash
export MCP_API_KEY="your_api_key"
export MCP_AUTH_TOKEN="your_auth_token"
export MCP_TOKEN="your_token"
export MCP_API_TOKEN="your_api_token"
export MCP_KEY="your_custom_key"
```

The test script will use these environment variables when testing different methods.
    name="MCPIntegratedAgent",
    instructions="""
    You are an AI assistant with access to external tools via MCP.
    Use the available tools to help users with their requests.
    Be helpful and provide detailed responses.
    """,
    model="gpt-4",  # or your preferred model
    mcp_servers=[mcp_server],  # Include your MCP server
)
```

### Running the Agent

```python
from agents import Runner

# Run synchronously
result = Runner.run_sync(
    agent,
    "Use the available MCP tools to help me analyze this data"
)
print(result.final_output)

# Or run asynchronously
result = await Runner.run(
    agent,
    "Use MCP tools for my request"
)
```

## Testing Files

### Connectivity Test

```bash
# Test basic server connectivity
uv run python test_user_mcp_server.py
```

**Expected Output**: HTTP 401 with "no bearer token" message (confirms server is working)

### Integration Example

```bash
# View integration setup (requires token)
uv run python mcp_integration_example.py
```

## Configuration Options

### MCPServerStreamableHttp Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `url` | Your MCP server endpoint | Required |
| `headers` | HTTP headers (include Authorization) | `{}` |
| `timeout` | HTTP request timeout (seconds) | `5` |
| `sse_read_timeout` | SSE connection timeout (seconds) | `300` |
| `terminate_on_close` | Terminate connection on close | `True` |

### Agent Parameters

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| `cache_tools_list` | Cache tool list for performance | `True` |
| `tool_filter` | Filter available tools | `None` |
| `use_structured_content` | Use structured tool results | `False` |

## Next Steps

1. **Get Authentication Token**: Obtain the Bearer token for your MCP server
2. **Test with Token**: Update the example code with your real token
3. **Explore Tools**: Once authenticated, list and test available tools
4. **Build Applications**: Integrate into your workflows and applications

## Troubleshooting

### Common Issues

**401 Unauthorized**
- Check your Bearer token is correct
- Ensure token format: `Bearer YOUR_TOKEN`
- Verify token hasn't expired

**Connection Timeout**
- Increase `timeout` and `sse_read_timeout` values
- Check network connectivity
- Verify server URL is correct

**Import Errors**
- Ensure you're in the correct virtual environment
- Check that all dependencies are installed: `uv sync`

### Debug Steps

1. Test basic connectivity: `uv run python test_user_mcp_server.py`
2. Check token format and validity
3. Try with increased timeouts
4. Check server logs if accessible

## Files Created

- `test_user_mcp_server.py`: Basic connectivity test
- `mcp_integration_example.py`: Full integration example
- `MCP_INTEGRATION_README.md`: This documentation