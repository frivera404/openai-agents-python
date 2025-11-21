// This service now communicates with the backend server instead of Google's API directly.

interface LaunchAgentConfig {
    agentId: string;
    model: string;
    systemInstruction: string;
    prompt: string;
    temperature: number;
}

export interface ToolDefinition {
    name: string;
    description: string;
    category?: string;
}

export interface ToolCreationResponse {
    message: string;
    tool?: ToolDefinition & { createdAt: string };
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/g, '');
const buildApiUrl = (path: string) => (API_BASE_URL ? `${API_BASE_URL}${path}` : path);

const handleResponse = async (response: Response) => {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({} as Record<string, string>));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
};

export const launchAgent = async (config: LaunchAgentConfig): Promise<string> => {
    try {
        const response = await fetch(buildApiUrl('/api/agent/launch'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config),
        });

        const data = await handleResponse(response);
        return data.text;
    } catch (error) {
        console.error('Error launching agent:', error);
        if (error instanceof Error) {
            throw new Error(`Failed to launch agent: ${error.message}`);
        }
        throw new Error('An unknown error occurred while launching the agent.');
    }
};

export const getDeployedAgents = async () => {
    const response = await fetch(buildApiUrl('/api/agents/deployed'));
    const data = await handleResponse(response);
    return data.agents as Record<string, string>;
};

export const sendAgentCommand = async ({ assistantId, prompt, model, temperature, systemInstruction }:
    { assistantId: string; prompt: string; model?: string; temperature?: number; systemInstruction?: string }) => {
    const response = await fetch(buildApiUrl('/api/agent/command'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assistantId, prompt, model, temperature, systemInstruction }),
    });

    return handleResponse(response);
};

export const addTool = async (tool: ToolDefinition): Promise<ToolCreationResponse> => {
    const response = await fetch(buildApiUrl('/api/tools'), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tool),
    });

    const data = await handleResponse(response);
    return data;
};

// Placeholder for future API calls
export const getAgentStatus = async (agentId: string) => {
    console.log(`Checking status for agent ${agentId}`);
    return Promise.resolve({ status: 'running', endpoint: `https://api.example.com/agents/${agentId}` });
};
