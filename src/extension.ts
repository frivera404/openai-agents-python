import * as vscode from 'vscode';
import { MCPServerTreeProvider, MCPServerItem } from './treeProvider';
import { MCPServerManager } from './serverManager';

let treeProvider: MCPServerTreeProvider;
let serverManager: MCPServerManager;

export function activate(context: vscode.ExtensionContext) {
    serverManager = new MCPServerManager(context);
    treeProvider = new MCPServerTreeProvider(serverManager);

    // Register tree view
    vscode.window.registerTreeDataProvider('mcpServers', treeProvider);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('mcpServers.addServer', async () => {
            await addServer();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('mcpServers.refresh', () => {
            treeProvider.refresh();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('mcpServers.removeServer', async (server: MCPServerItem) => {
            if (server) {
                await removeServer(server);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('mcpServers.editServer', async (server: MCPServerItem) => {
            if (server) {
                await editServer(server);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('mcpServers.authenticateServer', async (server: MCPServerItem) => {
            if (server) {
                await authenticateServer(server);
            }
        })
    );
}

export function deactivate() {}

async function addServer() {
    try {
        // Get server name
        const name = await vscode.window.showInputBox({
            prompt: 'Enter server name',
            placeHolder: 'my-mcp-server',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Server name is required';
                }
                if (serverManager.getServer(value)) {
                    return 'Server name already exists';
                }
                return null;
            }
        });

        if (!name) return;

        // Get transport type
        const transport = await vscode.window.showQuickPick(
            ['stdio', 'http', 'websocket'],
            {
                placeHolder: 'Select transport type',
                canPickMany: false
            }
        );

        if (!transport) return;

        let commandOrUrl: string | undefined;
        let args: string[] = [];

        if (transport === 'stdio') {
            // Get command
            commandOrUrl = await vscode.window.showInputBox({
                prompt: 'Enter command to run the MCP server',
                placeHolder: 'npx my-mcp-server'
            });

            if (!commandOrUrl) return;

            // Get arguments (optional)
            const argsInput = await vscode.window.showInputBox({
                prompt: 'Enter command arguments (optional, space-separated)',
                placeHolder: '--port 3000'
            });

            if (argsInput) {
                args = argsInput.split(' ').filter(arg => arg.trim().length > 0);
            }
        } else {
            // Get URL for http/websocket
            commandOrUrl = await vscode.window.showInputBox({
                prompt: `Enter ${transport} URL`,
                placeHolder: transport === 'http' ? 'http://localhost:3000' : 'ws://localhost:3000'
            });

            if (!commandOrUrl) return;
        }

        // Get scope
        const scope = await vscode.window.showQuickPick(
            ['workspace', 'global'],
            {
                placeHolder: 'Select configuration scope',
                canPickMany: false
            }
        );

        if (!scope) return;

        // Trust confirmation
        const trustUnknownServers = vscode.workspace.getConfiguration('mcpServers').get('trustUnknownServers', false);
        if (!trustUnknownServers) {
            const trust = await vscode.window.showWarningMessage(
                `Do you trust this MCP server: ${name}?`,
                { modal: true },
                'Trust',
                'Cancel'
            );

            if (trust !== 'Trust') return;
        }

        // Handle secrets (placeholders for now)
        const envVars: { [key: string]: string } = {};
        const addEnvVar = await vscode.window.showQuickPick(
            ['Yes', 'No'],
            {
                placeHolder: 'Add environment variables?'
            }
        );

        if (addEnvVar === 'Yes') {
            // For now, just show a placeholder message
            vscode.window.showInformationMessage('Environment variable management will be implemented in a future update');
        }

        // Add server
        await serverManager.addServer({
            name,
            transport: transport as 'stdio' | 'http' | 'websocket',
            command: transport === 'stdio' ? commandOrUrl : undefined,
            url: transport !== 'stdio' ? commandOrUrl : undefined,
            args,
            env: envVars,
            scope: scope as 'workspace' | 'global'
        });

        treeProvider.refresh();
        vscode.window.showInformationMessage(`MCP server "${name}" added successfully`);

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to add MCP server: ${error}`);
    }
}

async function removeServer(server: MCPServerItem) {
    const confirm = await vscode.window.showWarningMessage(
        `Remove MCP server "${server.label}"?`,
        { modal: true },
        'Remove',
        'Cancel'
    );

    if (confirm === 'Remove') {
        try {
            await serverManager.removeServer(server.label);
            treeProvider.refresh();
            vscode.window.showInformationMessage(`MCP server "${server.label}" removed`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to remove server: ${error}`);
        }
    }
}

async function editServer(server: MCPServerItem) {
    vscode.window.showInformationMessage('Edit server functionality will be implemented in a future update');
}

async function authenticateServer(server: MCPServerItem) {
    try {
        const success = await serverManager.authenticateServer(server.label);
        if (success) {
            vscode.window.showInformationMessage(`Successfully authenticated "${server.label}"`);
        } else {
            vscode.window.showErrorMessage(`Authentication failed for "${server.label}"`);
        }
    } catch (error) {
        vscode.window.showErrorMessage(`Authentication error: ${error}`);
    }
}