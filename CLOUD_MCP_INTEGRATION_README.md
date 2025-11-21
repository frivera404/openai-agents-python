# Cloud MCP Router Integration

This guide demonstrates how to integrate with external services using the **Cloud MCP Router** and the OpenAI Agents SDK.

## Overview

The **Model Context Protocol (MCP)** enables AI assistants to securely access external services and APIs. The **Cloud MCP Router** provides a centralized gateway for connecting to multiple external services through a single endpoint.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Agent      │────│  Cloud MCP       │────│ External        │
│                 │    │  Router          │    │ Services        │
│ • OpenAI Agents │    │                  │    │ • Google APIs   │
│ • MCP Client    │    │ • Authentication  │    │ • GitHub        │
│ • Tool Access   │    │ • Load Balancing │    │ • Web Search    │
└─────────────────┘    │ • Service Proxy   │    │ • Databases     │
                       └──────────────────┘    │ • Custom APIs    │
                                               └─────────────────┘
```

## Current Setup

Your MCP client is configured to connect to:
- **Cloud MCP Router**: `https://18268932-48e7550c72e668.router.cloudmcp.run/mcp`
- **Connection Type**: STDIO via `npx mcp-remote`
- **Status**: Active and ready for integration

## Quick Start

### 1. Run the Integration Example

```bash
python cloud_mcp_integration.py
```

This will:
- Connect to the cloud MCP router
- Create an agent with external service access
- Demonstrate tool usage with example queries

### 2. Use the MCP Client CLI

```bash
# List available servers
python mcp_client.py list-servers

# Initialize MCP servers
python mcp_client.py init

# Create an agent
python mcp_client.py create-agent

# Query with external services
python mcp_client.py query "What services are available?"
```

## Integration Patterns

### 1. **Direct MCP Server Connection**
```python
from agents import Agent, MCPServerStdio, MCPServerStdioParams

mcp_server = MCPServerStdio(
    params=MCPServerStdioParams(
        command="npx",
        args=["mcp-remote", "https://your-router-url/mcp"],
        env={},
    ),
    name="external-services"
)

agent = Agent(
    name="External Service Agent",
    mcp_servers=[mcp_server],
    instructions="Use external services to help users..."
)
```

### 2. **Hosted MCP Tools**
```python
from agents import Agent, HostedMCPTool

agent = Agent(
    name="Hosted Services Agent",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "google_calendar",
                "connector_id": "connector_googlecalendar",
                "authorization": "your-oauth-token",
                "require_approval": "never",
            }
        )
    ]
)
```

### 3. **Multiple Service Integration**
```python
# Combine multiple MCP servers
mcp_servers = [
    MCPServerStdio(...),  # Cloud router
    HostedMCPTool(...),   # Google Calendar
    HostedMCPTool(...),   # GitHub
]

agent = Agent(
    name="Multi-Service Agent",
    mcp_servers=mcp_servers,
    instructions="Access multiple external services..."
)
```

## Available Services

Based on your configuration, you can access:

### Cloud MCP Router Services
- **Primary Gateway**: Access to any service connected to the router
- **Authentication**: Token-based via `CLOUDMCP_TOKEN`
- **Transport**: HTTP Streamable with STDIO proxy

### Hosted MCP Services (Examples)
- **Google Calendar**: Schedule management and events
- **GitHub**: Repository operations and code access
- **Web Search**: Current information retrieval
- **Custom APIs**: Any service with MCP server implementation

## Configuration

### Environment Variables
```bash
# Required for cloud router
export CLOUDMCP_TOKEN="your-token-here"

# Optional for hosted services
export GOOGLE_CALENDAR_AUTHORIZATION="ya29.oauth-token"
export WEB_SEARCH_API_KEY="your-api-key"
```

### MCP Config File
See `mcp_services_config.json` for detailed server configurations.

## Best Practices

### 1. **Error Handling**
```python
try:
    result = await Runner.run(agent, query)
    print(result.final_output)
except Exception as e:
    print(f"Service error: {e}")
```

### 2. **Resource Management**
```python
# Always clean up connections
await mcp_server.disconnect()
```

### 3. **Security**
- Use approval requirements for sensitive operations
- Validate input data before sending to external services
- Monitor API usage and rate limits

### 4. **Performance**
- Cache frequently accessed data
- Use streaming for large responses
- Implement timeouts for long-running operations

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check if `npx mcp-remote` is available
   - Verify the router URL is accessible
   - Check authentication tokens

2. **No Tools Available**
   - The remote server may not have tools configured
   - Check server logs for errors
   - Verify MCP server implementation

3. **Unicode Errors**
   - Windows console encoding issues
   - Use `chcp 65001` to set UTF-8 encoding

### Debug Mode
```bash
# Enable verbose logging
python mcp_client.py --verbose init
```

## Next Steps

1. **Explore Available Tools**: Run `python mcp_client.py tools`
2. **Test Queries**: Try different types of requests
3. **Add More Services**: Extend `mcp_services_config.json`
4. **Custom Integrations**: Build your own MCP servers

## Resources

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [MCP Server Examples](https://github.com/modelcontextprotocol/examples)</content>
<parameter name="filePath">c:\Users\frive\MCP Servers\client\openai-agents-python-main\CLOUD_MCP_INTEGRATION_README.md