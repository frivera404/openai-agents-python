
import React, { useState } from 'react';
import AgentCard from '../components/AgentCard';
import type { Agent } from '../types';

interface AgentCatalogProps {
    agents: Agent[];
    onSelectAgent: (agent: Agent) => void;
    onLaunch: (agent: Agent) => void;
    launchingAgentId: string | null;
}

const AgentCatalog: React.FC<AgentCatalogProps> = ({ agents, onSelectAgent, onLaunch, launchingAgentId }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [languageFilter, setLanguageFilter] = useState('All');
    const [selectedAgentForPrompt, setSelectedAgentForPrompt] = useState<Agent | null>(null);
    const [prompt, setPrompt] = useState('');
    const [result, setResult] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const filteredAgents = agents.filter(agent => {
        const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              agent.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesLang = languageFilter === 'All' || agent.language === languageFilter;
        return matchesSearch && matchesLang;
    });

    const handlePromptSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedAgentForPrompt || !prompt.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/agent/launch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agentId: selectedAgentForPrompt.id,
                    prompt: prompt.trim(),
                    model: 'gpt-4.1',
                    temperature: 0.7,
                }),
            });
            const data = await response.json();
            if (response.ok) {
                setResult(data.text);
            } else {
                setResult(`Error: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            setResult(`Error: ${error instanceof Error ? error.message : 'Network error'}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6 md:p-8">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agents</h1>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                    Browse, configure, and launch your AI agents. Each agent is designed for a specific task and can be customized to fit your needs.
                </p>
                <div className="mt-6 flex flex-col sm:flex-row gap-4">
                    <div className="relative flex-grow">
                        <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                            <svg className="w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none">
                                <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                            </svg>
                        </span>
                        <input
                            type="text"
                            placeholder="Search agents..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <select
                        value={languageFilter}
                        onChange={(e) => setLanguageFilter(e.target.value)}
                        className="border rounded-md px-4 py-2 dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option>All</option>
                        <option>Python</option>
                        <option>Java</option>
                    </select>
                </div>
            </div>

            <div className="grid gap-6 md:gap-8 grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 mt-8">
                {filteredAgents.map(agent => (
                    <AgentCard
                        key={agent.id}
                        agent={agent}
                        onSelect={() => onSelectAgent(agent)}
                        onLaunch={() => onLaunch(agent)}
                        isLaunching={launchingAgentId === agent.id}
                    />
                ))}
            </div>

            {/* Prompting and Results Section */}
            <div className="mt-12 bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Test Agents</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Select an agent, enter a prompt, and see the results in real-time.
                </p>
                <form onSubmit={handlePromptSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Select Agent
                        </label>
                        <select
                            value={selectedAgentForPrompt?.id || ''}
                            onChange={(e) => {
                                const agent = agents.find(a => a.id === e.target.value);
                                setSelectedAgentForPrompt(agent || null);
                            }}
                            className="w-full border rounded-md px-3 py-2 dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        >
                            <option value="">Choose an agent...</option>
                            {agents.map(agent => (
                                <option key={agent.id} value={agent.id}>{agent.name}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Prompt
                        </label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="Enter your prompt here..."
                            rows={4}
                            className="w-full border rounded-md px-3 py-2 dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={isLoading || !selectedAgentForPrompt || !prompt.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? 'Processing...' : 'Submit Prompt'}
                    </button>
                </form>
                {result && (
                    <div className="mt-6">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Result</h3>
                        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-md border">
                            <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-200">{result}</pre>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AgentCatalog;
