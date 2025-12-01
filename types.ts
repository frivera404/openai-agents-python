
export enum AgentStatus {
  IDLE = 'IDLE',
  THINKING = 'THINKING',
  EXECUTING = 'EXECUTING',
  ERROR = 'ERROR'
}

export type AIMode = 'standard' | 'thinking' | 'search';

export interface KnowledgeDocument {
  id: string;
  name: string;
  content: string;
  createdAt: number;
  memoryUsage?: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  createdAt: number;
}

export interface LogEntry {
  id: string;
  timestamp: number;
  message: string;
  source: 'SYSTEM' | 'AGENT' | 'USER' | 'OPENAI';
  type: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
}

export interface AgentResponseSchema {
  reply: string;
  agent_status: string; // "IDLE" | "PROCESSING" | "COMPLETED"
  system_log_entry: string;
  new_task_suggestion?: {
    title: string;
    description: string;
  };
  delegated_agent_id?: string; // ID of a specialized agent to activate
  structured_result?: {
    title: string;
    content: string;
    type: 'report' | 'code' | 'analysis';
  };
  grounding_urls?: { title: string; uri: string }[]; // For Search results
}

export interface SystemMetric {
  name: string;
  value: number;
  unit: string;
  history: { time: number; value: number }[];
}

export interface AgentProfile {
  id: string;
  name: string;
  role: string;
  description: string;
  abilities: string[];
  icon: string; // Lucide icon name
  status: 'ONLINE' | 'BUSY' | 'OFFLINE';
  color: string;
  openaiId?: string; // Optional OpenAI Assistant ID
}

export interface MCPServer {
  id: string;
  name: string;
  type: 'STDIO' | 'HTTP';
  status: 'CONNECTED' | 'DISCONNECTED' | 'ERROR';
  tools: number;
  latency: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: {
    agentId: string;
    action: string;
    duration: number;
  }[];
}

export type BackendConnectionStatus = 'DISCONNECTED' | 'CONNECTING' | 'CONNECTED' | 'ERROR';

export type SimulationStep = {
    message: string;
    delay: number;
};
