import * as vscode from 'vscode';
import { MCPServerManager, MCPServerConfig } from './serverManager';

export class MCPServerItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly config: MCPServerConfig,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        private serverManager?: MCPServerManager
    ) {
        super(label, collapsibleState);
        this.tooltip = `${config.transport}: ${config.command || config.url}`;
        this.description = config.transport;
        this.contextValue = 'server';

        // Check authentication status only if serverManager is provided
        if (serverManager) {
            const hasAuth = config.auth !== undefined;
            const isAuthenticated = hasAuth && serverManager.getAuthToken(label) !== undefined;

            if (hasAuth) {
                this.description = `${config.transport} ${isAuthenticated ? '✓' : '🔒'}`;
            }
        }

        // Set icon based on transport type
        switch (config.transport) {
            case 'stdio':
                this.iconPath = new vscode.ThemeIcon('terminal');
                break;
            case 'http':
                this.iconPath = new vscode.ThemeIcon('globe');
                break;
            case 'websocket':
                this.iconPath = new vscode.ThemeIcon('radio-tower');
                break;
        }
    }
}

export class MCPServerTreeProvider implements vscode.TreeDataProvider<MCPServerItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData: vscode.Event<void> = this._onDidChangeTreeData.event;

    constructor(private serverManager: MCPServerManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: MCPServerItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: MCPServerItem): Promise<MCPServerItem[]> {
        if (element) {
            // Return server details as children
            return this.getServerDetails(element);
        } else {
            // Return root servers
            const servers = this.serverManager.getAllServers();
            return servers.map((server: MCPServerConfig) => new MCPServerItem(
                server.name,
                server,
                vscode.TreeItemCollapsibleState.Collapsed,
                this.serverManager
            ));
        }
    }

    private getServerDetails(server: MCPServerItem): MCPServerItem[] {
        const details: MCPServerItem[] = [];

        // Transport
        details.push(new MCPServerItem(
            `Transport: ${server.config.transport}`,
            server.config,
            vscode.TreeItemCollapsibleState.None
        ));

        // Command/URL
        if (server.config.command) {
            details.push(new MCPServerItem(
                `Command: ${server.config.command}`,
                server.config,
                vscode.TreeItemCollapsibleState.None
            ));
        } else if (server.config.url) {
            details.push(new MCPServerItem(
                `URL: ${server.config.url}`,
                server.config,
                vscode.TreeItemCollapsibleState.None
            ));
        }

        // Arguments
        if (server.config.args && server.config.args.length > 0) {
            details.push(new MCPServerItem(
                `Args: ${server.config.args.join(' ')}`,
                server.config,
                vscode.TreeItemCollapsibleState.None
            ));
        }

        // Environment variables
        if (server.config.env && Object.keys(server.config.env).length > 0) {
            details.push(new MCPServerItem(
                `Environment: ${Object.keys(server.config.env).length} variables`,
                server.config,
                vscode.TreeItemCollapsibleState.None
            ));
        }

        // Scope
        details.push(new MCPServerItem(
            `Scope: ${server.config.scope}`,
            server.config,
            vscode.TreeItemCollapsibleState.None
        ));

        return details;
    }
}