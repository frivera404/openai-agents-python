import type {
  PrimeGoalStatus,
  ActionResult,
  SupervisorAgent,
  SystemSettings,
  MemoryResponse,
  ToolDefinition,
  McpToolsMap,
  AgentQueryRequest,
  SupervisorQueryResponse,
} from './types';

const BASE_URL = import.meta.env.VITE_AGENT_API_BASE_URL ?? 'http://127.0.0.1:8001';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed ${res.status}: ${text}`);
  }

  return res.json() as Promise<T>;
}

export function getPrimeGoalStatus(): Promise<PrimeGoalStatus> {
  return request<PrimeGoalStatus>('/agent/prime-goal/status');
}

export function applyPrimeGoal(): Promise<ActionResult> {
  return request<ActionResult>('/agent/prime-goal/apply', { method: 'POST' });
}

export function resetPrimeGoal(): Promise<ActionResult> {
  return request<ActionResult>('/agent/prime-goal/reset', { method: 'POST' });
}

export function getSupervisors(): Promise<SupervisorAgent[]> {
  return request<SupervisorAgent[]>('/agent/supervisors');
}

export function getSystemSettings(): Promise<SystemSettings> {
  return request<SystemSettings>('/agent/system-settings');
}

export function getMemory(): Promise<MemoryResponse> {
  return request<MemoryResponse>('/agent/memory');
}

export function listTools(): Promise<ToolDefinition[]> {
  return request<ToolDefinition[]>('/agent/tools');
}

export function listMcpTools(): Promise<McpToolsMap> {
  return request<McpToolsMap>('/agent/mcp-tools');
}

export function runSupervisorQuery(body: AgentQueryRequest): Promise<SupervisorQueryResponse> {
  return request<SupervisorQueryResponse>('/agent/supervisor/query', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
