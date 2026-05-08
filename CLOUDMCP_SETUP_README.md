# CloudMCP Integration Setup Guide

This guide will help you configure authentication for your CloudMCP server and integrate it with the OpenAI Agents SDK.

## 🚀 Quick Start

1. **Get your credentials from CloudMCP dashboard:**
   - Go to https://cloudmcp.run/dashboard
   - Sign in with Google (riveraf30@gmail.com)
   - Find your project and get the API key/token

2. **Set up authentication:**
   ```powershell
   # Run the setup helper
   python setup_cloudmcp.py

   # Or set environment variables manually
   $env:CLOUDMCP_API_KEY = "your_api_key_here"
   ```

3. **Test the connection:**
   ```powershell
   python test_cloudmcp_auth.py
   ```

4. **Use in your code:**
   ```python
   from mcp_config import agent, mcp_server
   # Your agent is ready with MCP tools!
   ```

## 📋 Prerequisites

- Python 3.8+
- OpenAI Agents SDK (already installed)
- CloudMCP account with an active project

## 🔐 Authentication Methods

CloudMCP supports multiple authentication methods. The setup automatically tries all common methods:

### Environment Variables

Set one of these environment variables based on your credential type:

```powershell
# For API Key (most common)
$env:CLOUDMCP_API_KEY = "your_api_key"

# For Auth Token
$env:CLOUDMCP_AUTH_TOKEN = "your_auth_token"

# For Bearer Token
$env:CLOUDMCP_BEARER_TOKEN = "your_bearer_token"

# For Basic Authentication
$env:CLOUDMCP_USERNAME = "your_username"
$env:CLOUDMCP_PASSWORD = "your_password"
```

### Headers Tested

The authentication tester tries these header combinations:

- `X-API-Key: <api_key>`
- `X-Auth-Token: <token>`
- `Authorization: Token <token>`
- `Authorization: Bearer <token>`
- `Authorization: Basic <base64_credentials>`

## 🛠️ Setup Scripts

### `setup_cloudmcp.py`

Interactive setup helper:

```powershell
# Interactive setup
python setup_cloudmcp.py

# Check current status
python setup_cloudmcp.py --status
```

### `test_cloudmcp_auth.py`

Comprehensive authentication testing:

```powershell
# Test all authentication methods
python test_cloudmcp_auth.py
```

This script will:
1. Check your environment variables
2. Test different header combinations
3. Verify basic HTTP authentication
4. Test full MCP protocol connection
5. Show which method works

## 📁 Configuration Files

### `mcp_config.py`

Automatic configuration that detects your credentials:

```python
from mcp_config import agent, mcp_server

# Agent with MCP tools
result = await Runner.run(
    agent,
    "Use MCP tools to help with this task"
)
```

The configuration automatically:
- Detects available credentials
- Tries different authentication methods
- Creates MCP server and agent instances
- Handles connection errors gracefully

## 🔧 Troubleshooting

### "Project archived" Error

If you get: `"The project you are requesting has been archived"`

1. Go to https://cloudmcp.run/dashboard
2. Find your project
3. Click "Unarchive" if available
4. If not visible, create a new project

### Authentication Failed

1. **Check credentials:**
   ```powershell
   python setup_cloudmcp.py --status
   ```

2. **Test different methods:**
   ```powershell
   python test_cloudmcp_auth.py
   ```

3. **Manual testing:**
   ```powershell
   # Test with curl
   curl -H "X-API-Key: your_key" https://18268932-0807663c6d1468.router.cloudmcp.run/mcp
   ```

### Connection Issues

- Verify your project is active in CloudMCP dashboard
- Check that the URL is correct: `https://18268932-0807663c6d1468.router.cloudmcp.run/mcp`
- Ensure your credentials haven't expired

## 🎯 Usage Examples

### Basic Agent with MCP Tools

```python
from mcp_config import agent

async def main():
    result = await Runner.run(
        agent,
        "List the files in the current directory"
    )
    print(result.final_output)

# Run the agent
asyncio.run(main())
```

### Custom MCP Server Configuration

```python
from agents.mcp import MCPServerStreamableHttp

# Manual configuration
config = {
    "url": "https://18268932-0807663c6d1468.router.cloudmcp.run/mcp",
    "headers": {"X-API-Key": "your_key"},
    "timeout": 30,
}

mcp_server = MCPServerStreamableHttp(
    params=config,
    name="MyMCPServer"
)

agent = Agent(
    name="CustomAgent",
    instructions="Use MCP tools",
    mcp_servers=[mcp_server]
)
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the authentication tester for detailed error messages
3. Verify your CloudMCP project status
4. Contact CloudMCP support if credentials are invalid

## 🔄 Next Steps

Once authentication works:

1. Your MCP server tools will be available to agents
2. Test with different tasks to see available tools
3. Integrate with your Temporal workflows
4. Build custom agents using MCP capabilities

The integration is complete when `test_cloudmcp_auth.py` shows successful MCP connection!