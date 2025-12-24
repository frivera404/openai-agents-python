export interface PrimeGoalStatus {
  prime_goal_active: boolean;
  supervisor_agents_configured: number;
  total_supervisor_agents: number;
  system_optimizations_active: boolean;
  configuration_integrity: boolean;
}

export interface ActionResult {
  success: boolean;
  detail: string;
  status?: PrimeGoalStatus;
}

export interface SupervisorAgent {
  id: string;
  name: string;
  role: string;
  optimization_level: string;
}

export interface SystemSettings {
  global_optimizations: Record<string, unknown>;
  mcp_integration: Record<string, unknown>;
}

export interface MemoryStats {
  total_conversations: number;
  memory_file_size: number;
  last_updated: string | null;
  auto_save_enabled: boolean;
  settings_count: number;
}

export interface MemoryResponse {
  memory: Record<string, unknown>;
  stats: MemoryStats;
}

export interface CommandResult {
  id: string;
  supervisorId: string;
  supervisorName: string;
  content: string;
  createdAt: string;
}

export interface ToolDefinition {
  name: string;
  description?: string;
  provider?: string;
  type?: string;
  usage?: string;
}

export type McpToolsMap = Record<string, string[]>;

// Agent query + supervisor types mirror the FastAPI models.

export interface AgentQueryRequest {
  query: string;
  thread_id?: string | null;
}

export interface AgentQueryResponse {
  query: string;
  response: string;
  thread_id?: string | null;
  timestamp: number;
}

export interface SupervisorPlan {
  selected_sub_agent_id: string;
  selected_sub_agent_name: string;
  selected_sub_agent_role: string;
  selected_sub_agent_description: string;
}

export interface SupervisorQueryResponse {
  plan: SupervisorPlan;
  result: AgentQueryResponse;
}

