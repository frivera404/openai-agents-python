import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export interface MCPServerConfig {
    name: string;
    transport: 'stdio' | 'http' | 'websocket';
    command?: string;
    url?: string;
    args?: string[];
    env?: { [key: string]: string };
    scope: 'workspace' | 'global';
    auth?: AuthConfig;
}

export interface AuthToken {
    accessToken: string;
    refreshToken?: string;
    expiresAt?: number;
    tokenType?: string;
}

export interface AuthConfig {
    type: 'oauth2' | 'api_key' | 'basic';
    provider?: 'google' | 'github' | 'custom';
    clientId?: string;
    scopes?: string[];
    tokenUrl?: string;
    authUrl?: string;
}

export class MCPServerManager {
    private servers: Map<string, MCPServerConfig> = new Map();
    private authTokens: Map<string, AuthToken> = new Map();

    constructor(private context: vscode.ExtensionContext) {
        this.loadServers();
        this.loadAuthTokens();
    }

    async addServer(config: MCPServerConfig): Promise<void> {
        this.servers.set(config.name, config);
        await this.saveServers();
    }

    async removeServer(name: string): Promise<void> {
        this.servers.delete(name);
        await this.saveServers();
    }

    getServer(name: string): MCPServerConfig | undefined {
        return this.servers.get(name);
    }

    getAllServers(): MCPServerConfig[] {
        return Array.from(this.servers.values());
    }

    private async loadServers(): Promise<void> {
        try {
            // Load workspace servers
            const workspaceConfig = await this.loadWorkspaceConfig();
            if (workspaceConfig?.servers) {
                Object.entries(workspaceConfig.servers).forEach(([name, config]) => {
                    this.servers.set(name, { ...config as MCPServerConfig, scope: 'workspace' });
                });
            }

            // Load global servers
            const globalConfig = await this.loadGlobalConfig();
            if (globalConfig?.servers) {
                Object.entries(globalConfig.servers).forEach(([name, config]) => {
                    if (!this.servers.has(name)) { // Workspace takes precedence
                        this.servers.set(name, { ...config as MCPServerConfig, scope: 'global' });
                    }
                });
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load MCP servers: ${error}`);
        }
    }

    private loadAuthTokens(): void {
        try {
            const tokens = this.context.globalState.get('mcpAuthTokens', {});
            Object.entries(tokens).forEach(([serverName, token]) => {
                this.authTokens.set(serverName, token as AuthToken);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load auth tokens: ${error}`);
        }
    }

    private async saveServers(): Promise<void> {
        const workspaceServers: { [key: string]: any } = {};
        const globalServers: { [key: string]: any } = {};

        this.servers.forEach((config, name) => {
            const serverConfig: any = {
                command: config.command,
                args: config.args || [],
                env: config.env || {},
                type: config.transport
            };

            if (config.url) {
                serverConfig.url = config.url;
            }

            if (config.scope === 'workspace') {
                workspaceServers[name] = serverConfig;
            } else {
                globalServers[name] = serverConfig;
            }
        });

        // Save workspace config
        if (Object.keys(workspaceServers).length > 0) {
            await this.saveWorkspaceConfig({ servers: workspaceServers });
        }

        // Save global config
        if (Object.keys(globalServers).length > 0) {
            await this.saveGlobalConfig({ servers: globalServers });
        }
    }

    private async loadWorkspaceConfig(): Promise<any> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) return null;

        const configPath = path.join(workspaceFolder.uri.fsPath, '.vscode', 'mcp.json');
        return await this.readJsonFile(configPath);
    }

    private async loadGlobalConfig(): Promise<any> {
        const configPath = path.join(this.context.globalStorageUri.fsPath, 'mcp.json');
        return await this.readJsonFile(configPath);
    }

    private async saveWorkspaceConfig(config: any): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) return;

        const configDir = path.join(workspaceFolder.uri.fsPath, '.vscode');
        const configPath = path.join(configDir, 'mcp.json');

        await this.ensureDirectoryExists(configDir);
        await this.writeJsonFile(configPath, config);
    }

    private async saveGlobalConfig(config: any): Promise<void> {
        const configPath = path.join(this.context.globalStorageUri.fsPath, 'mcp.json');
        await this.ensureDirectoryExists(path.dirname(configPath));
        await this.writeJsonFile(configPath, config);
    }

    private async readJsonFile(filePath: string): Promise<any> {
        try {
            const content = await fs.promises.readFile(filePath, 'utf8');
            return JSON.parse(content);
        } catch {
            return null;
        }
    }

    private async writeJsonFile(filePath: string, data: any): Promise<void> {
        await fs.promises.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
    }

    private async ensureDirectoryExists(dirPath: string): Promise<void> {
        try {
            await fs.promises.access(dirPath);
        } catch {
            await fs.promises.mkdir(dirPath, { recursive: true });
        }
    }

    // Authentication methods
    async authenticateServer(serverName: string): Promise<boolean> {
        const server = this.servers.get(serverName);
        if (!server?.auth) {
            return false;
        }

        try {
            switch (server.auth.type) {
                case 'oauth2':
                    return await this.authenticateOAuth2(serverName, server.auth);
                case 'api_key':
                    return await this.authenticateApiKey(serverName, server.auth);
                case 'basic':
                    return await this.authenticateBasic(serverName, server.auth);
                default:
                    return false;
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Authentication failed for ${serverName}: ${error}`);
            return false;
        }
    }

    private async authenticateOAuth2(serverName: string, auth: AuthConfig): Promise<boolean> {
        if (!auth.provider || !auth.clientId) {
            return false;
        }

        // For now, use a simplified approach - prompt for access token
        const accessToken = await vscode.window.showInputBox({
            prompt: `Enter access token for ${serverName} (${auth.provider})`,
            password: true,
            placeHolder: 'Access token from OAuth provider'
        });

        if (accessToken) {
            this.authTokens.set(serverName, {
                accessToken: accessToken,
                tokenType: 'Bearer'
            });
            await this.saveAuthTokens();
            return true;
        }

        return false;
    }

    private async authenticateApiKey(serverName: string, auth: AuthConfig): Promise<boolean> {
        const apiKey = await vscode.window.showInputBox({
            prompt: `Enter API key for ${serverName}`,
            password: true
        });

        if (apiKey) {
            this.authTokens.set(serverName, {
                accessToken: apiKey,
                tokenType: 'Bearer'
            });
            await this.saveAuthTokens();
            return true;
        }

        return false;
    }

    private async authenticateBasic(serverName: string, auth: AuthConfig): Promise<boolean> {
        const username = await vscode.window.showInputBox({
            prompt: `Enter username for ${serverName}`
        });

        if (!username) return false;

        const password = await vscode.window.showInputBox({
            prompt: `Enter password for ${serverName}`,
            password: true
        });

        if (password) {
            const credentials = Buffer.from(`${username}:${password}`).toString('base64');
            this.authTokens.set(serverName, {
                accessToken: credentials,
                tokenType: 'Basic'
            });
            await this.saveAuthTokens();
            return true;
        }

        return false;
    }

    private getAuthUrl(provider: string): string | undefined {
        const urls: { [key: string]: string } = {
            google: 'https://accounts.google.com/o/oauth2/v2/auth',
            github: 'https://github.com/login/oauth/authorize'
        };
        return urls[provider];
    }

    private getTokenUrl(provider: string): string | undefined {
        const urls: { [key: string]: string } = {
            google: 'https://oauth2.googleapis.com/token',
            github: 'https://github.com/login/oauth/access_token'
        };
        return urls[provider];
    }

    private getDefaultScopes(provider: string): string[] {
        const scopes: { [key: string]: string[] } = {
            google: ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            github: ['user:email', 'read:user']
        };
        return scopes[provider] || [];
    }

    private async saveAuthTokens(): Promise<void> {
        const tokens: { [key: string]: AuthToken } = {};
        this.authTokens.forEach((token, serverName) => {
            tokens[serverName] = token;
        });
        await this.context.globalState.update('mcpAuthTokens', tokens);
    }

    getAuthToken(serverName: string): AuthToken | undefined {
        return this.authTokens.get(serverName);
    }
}