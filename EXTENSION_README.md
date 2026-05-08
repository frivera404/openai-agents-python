# MCP Servers

A VS Code extension for managing Model Context Protocol (MCP) servers through an intuitive tree view interface.

## Features

- **Tree View**: Visual representation of all configured MCP servers
- **Add Servers**: Easy-to-use interface for adding new MCP servers
- **Multiple Transports**: Support for stdio, HTTP, and WebSocket transports
- **Scope Management**: Configure servers for workspace or global scope
- **Trust Confirmation**: Security prompts for unknown servers
- **Environment Variables**: Support for server environment configuration

## Usage

### Adding a Server

1. Open the MCP Servers view in the Explorer panel
2. Click the "+" button or use the "MCP: Add Server" command
3. Fill in the server details:
   - **Name**: Unique identifier for the server
   - **Transport**: stdio, http, or websocket
   - **Command/URL**: Command to run (stdio) or URL (http/websocket)
   - **Arguments**: Command-line arguments (stdio only)
   - **Scope**: Workspace or global configuration

### Server Details

Click on any server in the tree view to see detailed information:
- Transport type
- Command or URL
- Arguments
- Environment variables
- Configuration scope

### Managing Servers

- **Edit**: Right-click on a server and select "Edit Server"
- **Remove**: Right-click on a server and select "Remove Server"
- **Refresh**: Click the refresh button to reload server configurations

### Authentication

For servers that require authentication, you can configure OAuth2, API key, or basic authentication:

1. When adding a server, specify authentication details in the configuration
2. Right-click on an authenticated server and select "Authenticate Server"
3. Follow the prompts to enter credentials or tokens

Supported authentication methods:
- **OAuth2**: For Google, GitHub, and custom OAuth providers
- **API Key**: Direct token entry for API authentication
- **Basic Auth**: Username/password authentication

## Configuration

### Extension Settings

- `mcpServers.trustUnknownServers`: Automatically trust unknown servers (default: false)
- `mcpServers.defaultScope`: Default scope for new servers (default: workspace)

### Configuration Files

Server configurations are stored in:
- **Workspace**: `.vscode/mcp.json`
- **Global**: Extension storage directory

## Security

The extension includes trust confirmation for unknown servers to prevent unauthorized access to external services. Environment variables containing sensitive information should be managed through VS Code's SecretStorage API (planned for future release).

## Development

### Building

```bash
npm install
npm run compile
```

### Testing

```bash
npm run test
```

### Packaging

```bash
vsce package
```

## Contributing

Contributions are welcome! Please ensure that:
- Code follows TypeScript best practices
- New features include appropriate tests
- Documentation is updated for user-facing changes

## License

This extension is licensed under the MIT License.