# MCP Client - Production Application

A production-ready MCP (Model Context Protocol) client application built with the OpenAI Agents SDK. This application provides a robust, scalable solution for integrating multiple MCP servers with AI agents.

## 🚀 Features

- **Multi-Server Support**: Connect to multiple MCP servers simultaneously (HTTP Streamable, Stdio)
- **Authentication Management**: Secure token-based authentication for MCP servers
- **Error Handling**: Comprehensive error recovery and logging
- **CLI Interface**: User-friendly command-line interface
- **Configuration Management**: Flexible JSON-based configuration
- **Production Ready**: Logging, timeouts, and resource management
- **Extensible**: Easy to add new MCP servers and tools

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- MCP server credentials (tokens/keys)
- Node.js and npm (for stdio MCP servers using npx)

## 🛠️ Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd openai-agents-python
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # OR using uv (recommended)
   uv pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and tokens
   ```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MCP Server Authentication
CLOUDMCP_TOKEN=your_cloudmcp_token_here
WIKIPEDIA_TOKEN=your_wikipedia_token_here
```

### MCP Server Configuration (mcp_config.json)

```json
{
  "servers": {
    "cloudmcp-server-6837335c7e6338": {
      "url": "https://18268932-6837335c7e6338.router.cloudmcp.run/mcp",
      "headers": {"Authorization": "Bearer ${CLOUDMCP_TOKEN}"},
      "type": "http",
      "timeout": 30
    },
    "wikipedia-mcp": {
      "command": "npx",
      "args": ["mcp-remote", "--header", "Authorization:Bearer ${WIKIPEDIA_TOKEN}", "https://wiki-1763000517527.server.mcp-cloud.ai/sse"],
      "env": {"WIKIPEDIA_TOKEN": "${WIKIPEDIA_TOKEN}"},
      "type": "stdio"
    }
  }
}
```

## 🎯 Usage

### Basic Workflow

1. **List available servers**:
   ```bash
   python mcp_client.py list-servers
   ```

2. **Initialize MCP servers**:
   ```bash
   python mcp_client.py init
   ```

3. **Create an agent**:
   ```bash
   python mcp_client.py create-agent --model gpt-4o
   ```

4. **Run queries**:
   ```bash
   python mcp_client.py query "What tools are available?"
   python mcp_client.py query "Search for information about artificial intelligence"
   ```

5. **List available tools**:
   ```bash
   python mcp_client.py tools
   ```

6. **Clean up**:
   ```bash
   python mcp_client.py cleanup
   ```

### Advanced Usage

**Initialize specific servers only**:
```bash
python mcp_client.py init --servers cloudmcp-server-6837335c7e6338
```

**Use verbose logging**:
```bash
python mcp_client.py --verbose query "Your question here"
```

**Custom configuration file**:
```bash
python mcp_client.py --config custom_config.json init
```

**Query with custom timeout**:
```bash
python mcp_client.py query --timeout 600 "Complex analysis request"
```

## 🏗️ Architecture

### Core Components

- **MCPClientConfig**: Configuration management and loading
- **MCPClient**: Main client class handling server connections and agent creation
- **CLI Interface**: Click-based command-line interface
- **Error Handling**: Comprehensive logging and error recovery
- **Authentication**: Secure token management via environment variables

### Supported MCP Server Types

1. **HTTP Streamable**: Direct HTTP connections with authentication
2. **Stdio**: Command-line based servers (npx, docker, etc.)

## 🔧 Development

### Adding New MCP Servers

1. Add server configuration to `mcp_config.json`
2. Set required environment variables in `.env`
3. Test with: `python mcp_client.py init --servers your-server-name`

### Extending Functionality

The application is designed to be extensible:

- Add new CLI commands in the `cli` group
- Extend `MCPClient` class for new server types
- Add custom authentication methods
- Implement additional error handling patterns

## 📊 Logging

Logs are written to both console and `mcp_client.log`:

- **INFO**: General operations and status
- **WARNING**: Non-critical issues
- **ERROR**: Failures and exceptions
- **DEBUG**: Detailed debugging information (use `--verbose`)

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "mcp_client.py", "init"]
```

### Production Checklist

- [ ] Set production OpenAI API key
- [ ] Configure MCP server tokens
- [ ] Set appropriate timeouts
- [ ] Configure logging for production
- [ ] Set up monitoring and alerts
- [ ] Test with production load

## 🐛 Troubleshooting

### Common Issues

**"Failed to initialize MCP servers"**
- Check network connectivity
- Verify authentication tokens
- Ensure MCP servers are running

**"OpenAI API key not configured"**
- Set `OPENAI_API_KEY` in `.env`
- Verify API key is valid

**"Command not found: npx"**
- Install Node.js and npm
- Ensure npx is in PATH

### Debug Mode

Enable verbose logging for detailed troubleshooting:
```bash
python mcp_client.py --verbose [command]
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the logs in `mcp_client.log`
- Review the troubleshooting section
- Open an issue on GitHub

---

**Happy MCP-ing! 🚀**