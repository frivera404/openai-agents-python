
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Zap, Terminal as TerminalIcon } from 'lucide-react';
import { sendCommandToAgent } from './services/geminiService';
import { Terminal } from './components/Terminal';
import { SystemMonitor } from './components/SystemMonitor';
import { MCPServerStatus } from './components/MCPServerStatus';
import { TaskBoard } from './components/TaskBoard';
import { VoiceControl } from './components/VoiceControl';
import { AgentNetwork } from './components/AgentNetwork';
import { FuturisticClock } from './components/FuturisticClock';
import { ResultModal } from './components/ResultModal';
import { KnowledgeBase } from './components/KnowledgeBase';
import { SimulationToggle } from './components/SimulationToggle';
import { SPECIALIZED_AGENTS } from './data/agents';
import { SYSTEM_WORKFLOWS } from './data/workflows';
import { Task, LogEntry, AgentProfile, AIMode, KnowledgeDocument, MCPServer } from './types';

// Configuration Constants (In a real app, these come from .env)
const PROJECT_ID = "proj_JFug4teHnufR5Rulu8knTKBB";
const VECTOR_STORE_ID = "vs_1BREGwaFlfMYaIIOlzW7xCuC";
const ASSISTANT_ID = "asst_70Xrb6BnK0CtVx3qm89J6nEQ";

function App() {
  // State
  const [tasks, setTasks] = useState<Task[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [chartData, setChartData] = useState<{ time: string; value: number }[]>([]);
  const [activeAgentId, setActiveAgentId] = useState<string | null>(null);
  const [agents, setAgents] = useState<AgentProfile[]>(SPECIALIZED_AGENTS);
  
  // Vector Store State
  const [isVectorStoreConnected, setIsVectorStoreConnected] = useState(false);
  
  // Simulation State
  const [isSimulationActive, setIsSimulationActive] = useState(false);
  
  // MCP / OpenAI Agent State
  const [mcpServers, setMcpServers] = useState<MCPServer[]>([
    { id: 'srv_remote_1', name: 'mcp-remote-core', type: 'HTTP', status: 'CONNECTED', tools: 12, latency: '85ms' }, // cloudmcp.run
    { id: 'srv_wiki', name: 'wiki-knowledge-sse', type: 'HTTP', status: 'CONNECTED', tools: 5, latency: '112ms' }, // mcp-cloud.ai
    { id: 'srv_ollama', name: 'ollama-local', type: 'STDIO', status: 'CONNECTED', tools: 4, latency: '12ms' },
    { id: 'srv_fs', name: 'filesystem', type: 'STDIO', status: 'CONNECTED', tools: 4, latency: '8ms' },
  ]);

  // Knowledge Base (Vector Store) State
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);

  // Result Modal State
  const [resultModalOpen, setResultModalOpen] = useState(false);
  const [resultData, setResultData] = useState<{ title: string; content: string; type: any } | null>(null);

  // Refs for simulation loop to access fresh state
  const agentsRef = useRef(agents);
  agentsRef.current = agents;

  // Load from local storage on mount
  useEffect(() => {
    const savedTasks = localStorage.getItem('nexus_tasks');
    if (savedTasks) setTasks(JSON.parse(savedTasks));

    const savedLogs = localStorage.getItem('nexus_logs');
    if (savedLogs) setLogs(JSON.parse(savedLogs));
    else {
        addLog(`Nexus Core Initialized. Project: ${PROJECT_ID}`, 'SYSTEM');
        // Load initial config payload
        const initialConfig = {
            "agents": [{"name":"MemoryAgent","role":"memory"}],
            "tools": [{"name":"openai_chat","description":"Chat via OpenAI"}]
        };
        addLog(`Config Loaded: ${JSON.stringify(initialConfig)}`, 'SYSTEM');
    }

    const savedDocs = localStorage.getItem('nexus_docs');
    if (savedDocs) {
      setDocuments(JSON.parse(savedDocs));
    }

    const initialData = Array.from({ length: 10 }, (_, i) => ({
      time: new Date(Date.now() - (9 - i) * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      value: Math.floor(Math.random() * 40) + 20
    }));
    setChartData(initialData);
  }, []);

  // --- AUTO-CONNECT TO VECTOR STORE ---
  useEffect(() => {
    const connectToVectorStore = async () => {
      // Simulate handshake delay
      setTimeout(() => {
        addLog(`Initiating handshake with OpenAI Vector Store: ${VECTOR_STORE_ID}...`, 'SYSTEM');
      }, 1000);

      setTimeout(() => {
        setIsVectorStoreConnected(true);
        addLog(`Secure connection established to Vector Store [${VECTOR_STORE_ID.slice(0, 8)}...]`, 'SUCCESS');
        addLog('Permanent Memory Access: GRANTED', 'SYSTEM');

        // Auto-load/Seed memory if empty
        setDocuments(prev => {
          if (prev.length === 0) {
            addLog('Downloading persistent memory fragments...', 'OPENAI');
            return [
              { id: 'mem_01', name: 'Project_Alpha_Specs.pdf', content: 'Confidential project details regarding autonomous agent swarm architecture.', createdAt: Date.now() },
              { id: 'mem_02', name: 'User_Preferences.json', content: 'User prefers dark mode, high-density data displays, and concise robotic responses.', createdAt: Date.now() }
            ];
          }
          return prev;
        });
      }, 3500);
    };

    connectToVectorStore();
  }, []);

  // Auto-Save
  useEffect(() => { localStorage.setItem('nexus_tasks', JSON.stringify(tasks)); }, [tasks]);
  useEffect(() => { localStorage.setItem('nexus_logs', JSON.stringify(logs.slice(-50))); }, [logs]);
  useEffect(() => { localStorage.setItem('nexus_docs', JSON.stringify(documents)); }, [documents]);

  // Live Chart
  useEffect(() => {
    const interval = setInterval(() => {
        setChartData(prev => {
            const newPoint = {
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                value: Math.min(100, Math.max(0, prev[prev.length - 1].value + (Math.random() - 0.5) * 20))
            };
            return [...prev.slice(1), newPoint];
        });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // --- SIMULATION ENGINE ---
  useEffect(() => {
    if (!isSimulationActive) return;

    const phrases = [
      "Optimizing vector index...",
      "Analyzing background latency...",
      "Pruning cache nodes...",
      "Syncing external tools...",
      "Verifying security tokens...",
      "Monitoring API quotas...",
      "Pinging Cloud MCP router..."
    ];

    const simInterval = setInterval(() => {
        // 30% chance to trigger an event each 5s cycle
        if (Math.random() > 0.7) {
            const idleAgents = agentsRef.current.filter(a => a.status === 'ONLINE' && a.id !== activeAgentId);
            if (idleAgents.length > 0) {
                const randomAgent = idleAgents[Math.floor(Math.random() * idleAgents.length)];
                const randomPhrase = phrases[Math.floor(Math.random() * phrases.length)];
                
                // Activate
                setAgents(prev => prev.map(a => a.id === randomAgent.id ? { ...a, status: 'BUSY' } : a));
                addLog(`[AUTO] ${randomAgent.name}: ${randomPhrase}`, 'AGENT');

                // Deactivate after random delay
                setTimeout(() => {
                   setAgents(prev => prev.map(a => a.id === randomAgent.id ? { ...a, status: 'ONLINE' } : a));
                }, 2000 + Math.random() * 3000);
            }
        }
    }, 5000);

    return () => clearInterval(simInterval);
  }, [isSimulationActive, activeAgentId]);

  // Helpers
  const addLog = (message: string, source: 'SYSTEM' | 'AGENT' | 'USER' | 'OPENAI' | 'SUCCESS') => {
    setLogs(prev => [...prev, {
      id: Date.now().toString() + Math.random(),
      timestamp: Date.now(),
      message,
      source: source === 'SUCCESS' ? 'SYSTEM' : source, // Map SUCCESS to SYSTEM for type safety if needed, or update type
      type: source === 'SUCCESS' ? 'SUCCESS' : source === 'AGENT' ? 'SUCCESS' : 'INFO'
    }]);
  };

  const clearLogs = () => {
      setLogs([]);
      addLog('Terminal buffer cleared.', 'SYSTEM');
  };

  const handleActivateAgent = useCallback((agentId: string) => {
      setActiveAgentId(agentId);
      const agent = agents.find(a => a.id === agentId);
      const agentName = agent?.name || agentId;
      addLog(`Manual activation: ${agentName} Node`, 'USER');

      setAgents(prev => prev.map(a => a.id === agentId ? { ...a, status: 'BUSY' } : a));

      // OpenAI Assistant Connection Simulation
      if (agent?.openaiId) {
          addLog(`Routing to OpenAI Assistant [${agent.openaiId}]...`, 'OPENAI');
          setTimeout(() => addLog('Retrieving latest thread context...', 'OPENAI'), 1200);
      }
      
      // Simulating OpenAI Backend for Senior Developer specific behavior
      if (agentId === 'snr_dev') {
          setTimeout(() => addLog(`Vector Store [${VECTOR_STORE_ID}] synchronized.`, 'OPENAI'), 1500);
          setTimeout(() => addLog('Accessing MCP: mcp-cloud.ai/wiki...', 'OPENAI'), 2500);
      }

      setTimeout(() => {
          addLog(`${agentName} sequence complete. Awaiting next cycle.`, 'SYSTEM');
          setAgents(prev => prev.map(a => a.id === agentId ? { ...a, status: 'ONLINE' } : a));
          setActiveAgentId(null);
      }, 4000);
  }, [agents]);

  const handleShowSpecs = () => {
     addLog("Generating System Capabilities Report...", "SYSTEM");
     const tableHeader = `| Agent Node | Role | Assistant ID | Specialized Abilities |\n|---|---|---|---|`;
     const tableRows = agents.map(a => `| **${a.name}** | ${a.role} | \`${a.openaiId || 'N/A'}\` | ${a.abilities.join(', ')} |`).join('\n');
     const content = `### NEXUS AGENT REGISTRY [CLASSIFIED]\n\n**Project ID:** ${PROJECT_ID}\n\n${tableHeader}\n${tableRows}\n\n*System Note: All nodes currently operational.*`;
     
     setResultData({ title: 'AGENT SPECIFICATIONS', content, type: 'report' });
     setResultModalOpen(true);
  };
  
  const handleShowBackendInstructions = () => {
      const content = `### SERVER STARTUP SEQUENCE
      
**1. API Server Initialization**
\`\`\`bash
cd server && cp .env.example .env && pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
\`\`\`

**2. Web Interface Initialization**
\`\`\`bash
cd web && npm i && npm run dev
\`\`\`

**3. Configuration Payload**
\`\`\`json
{
  "agents":[{"name":"MemoryAgent","role":"memory"}],
  "tools":[{"name":"openai_chat","description":"Chat via OpenAI"}]
}
\`\`\`

**Status:**
- Backend: WAITING_FOR_SIGNAL
- Web: ONLINE
- Wiki MCP: https://wiki-1763000517527.server.mcp-cloud.ai/mcp
`;
      setResultData({ title: 'BACKEND PROTOCOLS', content, type: 'code' });
      setResultModalOpen(true);
  }

  const handleAddDocument = (name: string, content: string) => {
    setDocuments(prev => [...prev, { id: crypto.randomUUID(), name, content, createdAt: Date.now() }]);
    addLog(`Document '${name}' vectorized and uploaded to store ${VECTOR_STORE_ID.slice(0,8)}...`, 'SYSTEM');
  };

  const handleRemoveDocument = (id: string) => {
    setDocuments(prev => prev.filter(d => d.id !== id));
    addLog('Document purged from memory banks.', 'SYSTEM');
  };

  const handleAddMCPServer = () => {
    const mockServers = [
       { name: 'stripe_gateway', tools: 15 },
       { name: 'aws_lambda_control', tools: 8 },
       { name: 'slack_notifier', tools: 4 },
       { name: 'linear_tracker', tools: 12 }
    ];
    const random = mockServers[Math.floor(Math.random() * mockServers.length)];
    const newServer: MCPServer = {
        id: `srv_${Date.now()}`,
        name: random.name,
        type: Math.random() > 0.5 ? 'HTTP' : 'STDIO',
        status: 'CONNECTED',
        tools: random.tools,
        latency: `${Math.floor(Math.random() * 100) + 10}ms`
    };
    setMcpServers(prev => [...prev, newServer]);
    addLog(`New MCP Server linked: ${newServer.name}`, 'SYSTEM');
  };

  const handleRunWorkflow = async (workflowId: string) => {
    const wf = SYSTEM_WORKFLOWS.find(w => w.id === workflowId);
    if (!wf) return;

    addLog(`INITIATING WORKFLOW: ${wf.name.toUpperCase()}`, 'SYSTEM');
    
    // Execute steps sequentially
    for (const step of wf.steps) {
        // Activate Agent
        setAgents(prev => prev.map(a => a.id === step.agentId ? { ...a, status: 'BUSY' } : a));
        setActiveAgentId(step.agentId);
        addLog(`[WF] ${step.agentId}: ${step.action}`, 'AGENT');
        
        // Handoff logic simulation
        if (step.action.includes('MemoryAgent')) {
            addLog('[HANDOFF] Transferring context to Permanent Memory Store...', 'SYSTEM');
        }

        // Wait for duration
        await new Promise(resolve => setTimeout(resolve, step.duration));

        // Deactivate Agent
        setAgents(prev => prev.map(a => a.id === step.agentId ? { ...a, status: 'ONLINE' } : a));
        setActiveAgentId(null);
    }
    
    addLog(`WORKFLOW ${wf.name.toUpperCase()} COMPLETED SUCCESSFULLY.`, 'SYSTEM');
  };

  // Main Command Handler
  const handleUserCommand = async (command: string, mode: AIMode) => {
    addLog(command, 'USER');
    setIsProcessing(true);
    setActiveAgentId(null);
    
    if (command.toLowerCase().includes('run setup') || command.toLowerCase().includes('backend')) {
        setIsProcessing(false);
        handleShowBackendInstructions();
        return;
    }

    try {
        const taskContext = tasks.map(t => `- [${t.status}] ${t.title}: ${t.description}`).join('\n');
        
        // Pass documents as knowledge base
        const response = await sendCommandToAgent(command, taskContext, mode, documents);

        addLog(response.reply, 'AGENT');
        addLog(response.system_log_entry, 'SYSTEM');

        if (response.delegated_agent_id) {
            const agent = agents.find(a => a.id === response.delegated_agent_id);
            if (agent) {
                setActiveAgentId(agent.id);
                setAgents(prev => prev.map(a => a.id === agent.id ? { ...a, status: 'BUSY' } : a));
                addLog(`Rerouting to specialized node: ${agent.name}`, 'SYSTEM');
                setTimeout(() => {
                    setAgents(prev => prev.map(a => a.id === agent.id ? { ...a, status: 'ONLINE' } : a));
                    setActiveAgentId(null);
                }, 4000);
            }
        }

        if (response.new_task_suggestion) {
            const newTask: Task = {
                id: crypto.randomUUID(),
                title: response.new_task_suggestion.title,
                description: response.new_task_suggestion.description,
                status: 'PENDING',
                createdAt: Date.now()
            };
            setTasks(prev => [newTask, ...prev]);
            addLog(`New directive created: ${newTask.title}`, 'SYSTEM');
        }

        if (response.structured_result) {
            setResultData(response.structured_result);
            setTimeout(() => setResultModalOpen(true), 800);
        }

    } catch (error) {
        addLog("Communication breakdown with Primary Agent.", 'SYSTEM');
    } finally {
        setIsProcessing(false);
    }
  };

  const handleVoiceTask = (title: string, description: string) => {
    const newTask: Task = {
        id: crypto.randomUUID(),
        title: title,
        description: description,
        status: 'PENDING',
        createdAt: Date.now()
    };
    setTasks(prev => [newTask, ...prev]);
    addLog(`VOICE OVERRIDE: Directive created - ${title}`, 'SYSTEM');
  };

  const removeTask = (id: string) => setTasks(prev => prev.filter(t => t.id !== id));
  
  const updateTask = (id: string, newTitle: string) => {
      setTasks(prev => prev.map(t => t.id === id ? { ...t, title: newTitle } : t));
      addLog(`Directive ID:${id.slice(0,4)} updated.`, 'SYSTEM');
  };

  const toggleTaskStatus = (id: string) => {
      setTasks(prev => prev.map(t => {
          if (t.id !== id) return t;
          const nextStatus = t.status === 'PENDING' ? 'IN_PROGRESS' : t.status === 'IN_PROGRESS' ? 'COMPLETED' : 'PENDING';
          return { ...t, status: nextStatus };
      }));
  };

  return (
    <div className="min-h-screen text-gray-200 font-sans p-4 md:p-6 lg:h-screen lg:overflow-hidden flex flex-col relative">
      
      {/* Result Modal */}
      <ResultModal isOpen={resultModalOpen} onClose={() => setResultModalOpen(false)} data={resultData} />

      {/* Header */}
      <header className="flex items-center justify-between mb-6 pb-4 border-b border-cyber-border/50 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyber-primary/10 border border-cyber-primary rounded-full animate-pulse-fast shadow-[0_0_15px_rgba(0,240,255,0.5)]">
             <Zap size={24} className="text-cyber-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold font-mono tracking-tighter text-white drop-shadow-md">
              NEXUS <span className="text-cyber-primary">INTERFACE</span>
            </h1>
            <div className="flex items-center gap-2 text-xs text-gray-400 font-mono">
               <span className="w-2 h-2 bg-cyber-alien rounded-full animate-alien-pulse"></span>
               <span>SYSTEM ONLINE</span>
               <span className="text-cyber-border">|</span>
               <span>PROJECT: {PROJECT_ID.slice(0,8)}...</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
             <button 
               onClick={handleShowBackendInstructions}
               className="text-[10px] font-mono border border-cyber-border/50 px-2 py-1 rounded hover:bg-cyber-dark hover:text-white transition-colors"
               title="Show Backend Run Instructions"
             >
                <TerminalIcon size={12} className="inline mr-1"/>
                BACKEND_CLI
             </button>
             <SimulationToggle isActive={isSimulationActive} onToggle={() => setIsSimulationActive(!isSimulationActive)} />
             <FuturisticClock />
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden min-h-0 z-10">
        
        {/* Left Column: Tasks & Vector Store (3 cols) */}
        <section className="lg:col-span-3 flex flex-col gap-4 h-[600px] lg:h-full">
            <div className="flex-[1.5] min-h-0">
              <TaskBoard 
                tasks={tasks} 
                onRemoveTask={removeTask} 
                onToggleStatus={toggleTaskStatus} 
                onUpdateTask={updateTask}
              />
            </div>
            <div className="flex-1 min-h-0">
              <KnowledgeBase 
                documents={documents} 
                onAddDocument={handleAddDocument} 
                onRemoveDocument={handleRemoveDocument}
                vectorStoreId={VECTOR_STORE_ID}
                isConnected={isVectorStoreConnected}
              />
            </div>
        </section>

        {/* Middle Column: Chat & Agent Grid (6 cols) */}
        <section className="lg:col-span-6 h-full flex flex-col gap-6 overflow-hidden">
            {/* Terminal (60%) */}
            <div className="flex-[3] min-h-0">
                <Terminal 
                    onSendMessage={handleUserCommand} 
                    onClear={clearLogs}
                    isProcessing={isProcessing} 
                    logs={logs} 
                />
            </div>
            {/* Agent Network (40%) */}
            <div className="flex-[2] min-h-0">
                <AgentNetwork 
                    agents={agents} 
                    activeAgentId={activeAgentId} 
                    onActivateAgent={handleActivateAgent} 
                    onShowSpecs={handleShowSpecs}
                />
            </div>
        </section>

        {/* Right Column: Metrics, MCP & Voice (3 cols) */}
        <section className="lg:col-span-3 h-full flex flex-col gap-4 overflow-hidden">
            {/* MCP / Backend Status */}
            <div className="flex-[1.5] min-h-[180px]">
                <MCPServerStatus 
                    servers={mcpServers} 
                    workflows={SYSTEM_WORKFLOWS}
                    assistantId={ASSISTANT_ID}
                    vectorStoreId={VECTOR_STORE_ID}
                    projectId={PROJECT_ID}
                    onAddServer={handleAddMCPServer}
                    onRunWorkflow={handleRunWorkflow}
                />
            </div>

            {/* System Metrics */}
            <div className="flex-1 min-h-[150px]">
                <SystemMonitor data={chartData} />
            </div>
            
            {/* Voice Control */}
            <div className="flex-1 min-h-[150px]">
                <VoiceControl onAddTask={handleVoiceTask} />
            </div>
        </section>
      </main>
    </div>
  );
}

export default App;
