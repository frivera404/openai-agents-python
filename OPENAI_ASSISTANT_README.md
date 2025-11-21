# OpenAI Assistant Integration

This document describes the OpenAI Assistant integration with vector store and MCP (Model Context Protocol) capabilities added to the OpenAI Agents SDK.

## Overview

The OpenAI Assistant Agent combines the power of OpenAI Assistants with external service access through MCP, providing a comprehensive AI solution for complex tasks.

### Key Features

- **🤖 OpenAI Assistant**: Pre-configured assistant with custom instructions
- **📚 Vector Store**: Knowledge base with file search and retrieval
- **🔗 MCP Integration**: Access to external services and APIs
- **💬 Conversation Continuity**: Persistent threads for multi-turn conversations
- **🛠️ Tool Execution**: Automated calling of external tools and APIs
- **📁 File Processing**: Document analysis and knowledge extraction

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ OpenAI Assistant│────│  Vector Store    │    │  MCP Servers    │
│   (asst_70X...) │    │  (vs_1BREGw...)  │    │ • External APIs │
│                 │    │                  │    │ • File Systems  │
│ • GPT-4o Model │    │ • File Search     │    │ • Commands      │
│ • Custom Tools  │    │ • Knowledge Base │    │ • Databases     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Configuration

### Assistant Credentials

The agent is pre-configured with the following credentials:

```json
{
  "assistant_id": "asst_70Xrb6BnK0CtVx3qm89J6nEQ",
  "vector_store_id": "vs_1BREGwaFlfMYaIIOlzW7xCuC",
  "api_key": "sk-proj-...",
  "model": "gpt-4o"
}
```

### MCP Servers

Default MCP server configuration:

```json
{
  "cloudmcp-router": {
    "command": "npx",
    "args": ["mcp-remote", "https://18268932-48e7550c72e668.router.cloudmcp.run/mcp"],
    "type": "stdio"
  }
}
```

## Quick Start

### 1. Initialize the Agent

```bash
python openai_assistant_cli.py init
```

This will:
- Connect to the OpenAI Assistant
- Initialize the vector store
- Set up MCP server connections
- Display available tools

### 2. Run Queries

```bash
# Simple query
python openai_assistant_cli.py query "What external services are available?"

# Query with output file
python openai_assistant_cli.py query "Analyze this document" --output-file response.json

# Use specific thread for conversation continuity
python openai_assistant_cli.py query "Follow up on the previous analysis" --thread-id thread_123
```

### 3. Explore Capabilities

```bash
# List all available tools
python openai_assistant_cli.py tools

# Show agent information
python openai_assistant_cli.py info

# Run interactive demo
python openai_assistant_cli.py demo
```

## CLI Commands

### `init`
Initialize the OpenAI Assistant Agent with MCP servers.

```bash
python openai_assistant_cli.py init [--servers SERVER1 SERVER2]
```

Options:
- `--servers`: Specify which MCP servers to initialize (default: all)

### `query`
Run a query using the assistant.

```bash
python openai_assistant_cli.py query "Your question here" [OPTIONS]
```

Options:
- `--thread-id`: OpenAI thread ID for conversation continuity
- `--output-file`: Save response to JSON file

### `tools`
List available tools from connected MCP servers.

```bash
python openai_assistant_cli.py tools
```

### `info`
Display information about the assistant and connections.

```bash
python openai_assistant_cli.py info
```

### `demo`
Run an interactive demonstration.

```bash
python openai_assistant_cli.py demo
```

### `cleanup`
Clean up MCP server connections.

```bash
python openai_assistant_cli.py cleanup
```

## Python API

### Basic Usage

```python
from openai_assistant_agent import OpenAIAssistantAgent
import asyncio

async def main():
    # Initialize agent
    agent = OpenAIAssistantAgent()

    # Setup MCP servers
    await agent.initialize_mcp_servers()

    # Create agent
    agent.create_agent()

    # Run queries
    result = await agent.run_query("What services are available?")
    print(result['response'])

asyncio.run(main())
```

### Advanced Usage

```python
# With specific MCP servers
await agent.initialize_mcp_servers(['cloudmcp-router'])

# With conversation threads
result1 = await agent.run_query("Analyze this data", "thread_123")
result2 = await agent.run_query("What are the key insights?", "thread_123")

# List available tools
tools = await agent.list_available_tools()
print(f"Available tools: {tools}")
```

## MCP Integration

The agent integrates with external services through the Model Context Protocol:

### Available Services

- **E-commerce**: Product management, orders, payments
- **File Systems**: Read/write operations, directory management
- **System Commands**: Shell execution, environment access
- **LLM Utilities**: Text processing, knowledge retrieval
- **APIs**: External service integration

### Service Discovery

```bash
python openai_assistant_cli.py tools
```

This will show all available tools from connected MCP servers.

## Vector Store Features

### File Search
The assistant can search through uploaded documents and knowledge base files.

### Knowledge Retrieval
Access stored information and context for enhanced responses.

### Document Analysis
Process and analyze various file types for insights.

## Best Practices

### Query Optimization

1. **Be Specific**: Provide clear, detailed questions
2. **Use Context**: Reference previous conversations with thread IDs
3. **Leverage Tools**: Ask the assistant to use specific external services

### Resource Management

1. **Cleanup**: Always run cleanup when done
2. **Connection Limits**: Monitor MCP server connections
3. **Rate Limits**: Be aware of API rate limits

### Error Handling

```python
try:
    result = await agent.run_query(query)
    if result:
        print(result['response'])
    else:
        print("Query failed - check agent initialization")
except Exception as e:
    print(f"Error: {e}")
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check OpenAI API key validity
   - Verify assistant and vector store IDs
   - Ensure network connectivity

2. **MCP Server Issues**
   - Run `npx --version` to check Node.js
   - Verify MCP router URL accessibility
   - Check server logs for errors

3. **Tool Execution Errors**
   - Some tools may require specific permissions
   - Check MCP server configuration
   - Verify external service credentials

### Debug Mode

Enable verbose logging:

```bash
python openai_assistant_cli.py --verbose init
```

## Configuration Files

- `openai_assistant_config.json`: Assistant and MCP server configuration
- `mcp_services_config.json`: Additional MCP service definitions

## Security Considerations

- API keys are stored in configuration files
- Use environment variables for sensitive credentials
- MCP connections may expose external service access
- Monitor tool usage for security compliance

## Examples

### Document Analysis

```bash
python openai_assistant_cli.py query "Analyze the attached PDF and summarize key findings"
```

### External API Integration

```bash
python openai_assistant_cli.py query "Fetch data from the external API and generate a report"
```

### Multi-turn Conversation

```bash
# First query
python openai_assistant_cli.py query "Start analyzing this dataset" --thread-id my-thread

# Follow-up
python openai_assistant_cli.py query "What are the trends in the data?" --thread-id my-thread
```

## Contributing

When extending the OpenAI Assistant integration:

1. Update configuration files for new credentials
2. Add MCP server definitions for new services
3. Test with both CLI and Python API
4. Update documentation for new features

## Support

For issues related to:
- **OpenAI Assistant**: Check OpenAI platform documentation
- **MCP Integration**: Refer to Model Context Protocol specs
- **Agents SDK**: See main project documentation

## License

This integration follows the same license as the OpenAI Agents SDK.</content>
<parameter name="filePath">c:\Users\frive\MCP Servers\client\openai-agents-python-main\OPENAI_ASSISTANT_README.md