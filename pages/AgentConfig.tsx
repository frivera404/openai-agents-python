
import React, { useState, useEffect } from 'react';
import type { Agent } from '../types';
import { launchAgent, addTool, getTools, deleteTool } from '../services/openaiService';

interface AgentConfigProps {
    agent: Agent;
    onBack: () => void;
}

const TabButton: React.FC<{ active: boolean; onClick: () => void; children: React.ReactNode }> = ({ active, onClick, children }) => (
    <button
        onClick={onClick}
        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            active
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
        }`}
    >
        {children}
    </button>
);

const ConfigSection: React.FC<{ title: string; description: string; children: React.ReactNode }> = ({ title, description, children }) => (
    <div className="mt-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{description}</p>
        <div className="mt-6 p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            {children}
        </div>
    </div>
);

const AgentConfig: React.FC<AgentConfigProps> = ({ agent, onBack }) => {
    const [activeTab, setActiveTab] = useState('Model');
    
    // State for model configuration
    const [model, setModel] = useState('gpt-4.1');
    const [temperature, setTemperature] = useState(0.9);
    const [systemInstruction, setSystemInstruction] = useState('');
    
    // State for deployment/testing
    const [userPrompt, setUserPrompt] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [apiResponse, setApiResponse] = useState('');
    const [apiError, setApiError] = useState('');
    
    // State for tools
    const [tools, setTools] = useState<any[]>([]);
    const [filteredTools, setFilteredTools] = useState<any[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedTools, setSelectedTools] = useState<Set<string>>(new Set());
    const [isCreatingTool, setIsCreatingTool] = useState(false);
    const [toolName, setToolName] = useState('');
    const [toolDescription, setToolDescription] = useState('');
    const [toolCategory, setToolCategory] = useState('General');
    const [toolParameters, setToolParameters] = useState('');
    const [toolStatus, setToolStatus] = useState<{ message: string; variant: 'success' | 'error' } | null>(null);
    const [isToolLoading, setIsToolLoading] = useState(false);
    const [isLoadingTools, setIsLoadingTools] = useState(false);

    // Fetch tools on component mount
    useEffect(() => {
        const fetchTools = async () => {
            setIsLoadingTools(true);
            try {
                const fetchedTools = await getTools();
                setTools(fetchedTools);
                setFilteredTools(fetchedTools);
            } catch (err) {
                console.error('Failed to fetch tools:', err);
            } finally {
                setIsLoadingTools(false);
            }
        };
        
        fetchTools();
    }, []);

    // Filter tools based on search query
    useEffect(() => {
        if (!searchQuery.trim()) {
            setFilteredTools(tools);
        } else {
            const filtered = tools.filter(tool =>
                tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                tool.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (tool.category && tool.category.toLowerCase().includes(searchQuery.toLowerCase()))
            );
            setFilteredTools(filtered);
        }
    }, [tools, searchQuery]);

    const handleStartCreatingTool = () => {
        setIsCreatingTool(true);
        setToolStatus(null);
    };

    const handleCancelToolCreation = () => {
        setIsCreatingTool(false);
        setToolName('');
        setToolDescription('');
        setToolStatus(null);
    };

    const handleCreateTool = async () => {
        if (!toolName.trim() || !toolDescription.trim()) {
            setToolStatus({ message: 'Name and description are required.', variant: 'error' });
            return;
        }
        setIsToolLoading(true);
        setToolStatus(null);
        try {
            const toolData = {
                name: toolName.trim(),
                description: toolDescription.trim(),
                category: toolCategory,
                parameters: toolParameters.trim() || undefined
            };
            const result = await addTool(toolData);
            setToolStatus({ message: result.message || 'Tool created successfully.', variant: 'success' });
            setToolName('');
            setToolDescription('');
            setToolCategory('General');
            setToolParameters('');
            setIsCreatingTool(false);
            
            // Refresh tools list
            const fetchedTools = await getTools();
            setTools(fetchedTools);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'An unknown error occurred while creating the tool.';
            setToolStatus({ message, variant: 'error' });
        } finally {
            setIsToolLoading(false);
        }
    };

    const handleDeleteTool = async (toolId: string) => {
        try {
            await deleteTool(toolId);
            // Remove from local state
            const updatedTools = tools.filter(tool => tool.id !== toolId);
            setTools(updatedTools);
            // Remove from selected tools if it was selected
            const newSelected = new Set(selectedTools);
            newSelected.delete(toolId);
            setSelectedTools(newSelected);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'An unknown error occurred while deleting the tool.';
            setToolStatus({ message, variant: 'error' });
        }
    };

    const handleToolSelection = (toolId: string) => {
        const newSelected = new Set(selectedTools);
        if (newSelected.has(toolId)) {
            newSelected.delete(toolId);
        } else {
            newSelected.add(toolId);
        }
        setSelectedTools(newSelected);
    };

    const handleSelectAllTools = () => {
        if (selectedTools.size === filteredTools.length) {
            setSelectedTools(new Set());
        } else {
            setSelectedTools(new Set(filteredTools.map(tool => tool.id)));
        }
    };

    const handleLaunch = async () => {
        if (!userPrompt) {
            setApiError('Please enter a prompt to test the agent.');
            return;
        }
        setIsLoading(true);
        setApiResponse('');
        setApiError('');
        try {
            const selectedToolObjects = tools.filter(tool => selectedTools.has(tool.id));
            const result = await launchAgent({
                agentId: agent.id,
                model,
                temperature,
                systemInstruction,
                prompt: userPrompt,
                tools: selectedToolObjects
            });
            setApiResponse(result);
        } catch (err) {
            setApiError(err instanceof Error ? err.message : 'An unknown error occurred.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6 md:p-8 max-w-7xl mx-auto">
            <button onClick={onBack} className="flex items-center text-sm text-blue-600 dark:text-blue-400 hover:underline mb-6">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Agents
            </button>

            <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">{agent.icon}</div>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{agent.name}</h1>
                    <p className="text-gray-600 dark:text-gray-400">{agent.description}</p>
                </div>
            </div>

            <div className="mt-8 border-b border-gray-200 dark:border-gray-700">
                <div className="flex space-x-4">
                    <TabButton active={activeTab === 'General'} onClick={() => setActiveTab('General')}>General</TabButton>
                    <TabButton active={activeTab === 'Model'} onClick={() => setActiveTab('Model')}>Model</TabButton>
                    <TabButton active={activeTab === 'Tools'} onClick={() => setActiveTab('Tools')}>Tools & Functions</TabButton>
                    <TabButton active={activeTab === 'Deployment'} onClick={() => setActiveTab('Deployment')}>Deployment & Testing</TabButton>
                </div>
            </div>

            {activeTab === 'General' && (
                <ConfigSection title="General Settings" description="Basic information about your agent.">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Agent Name</label>
                            <input type="text" defaultValue={agent.name} className="mt-1 block w-full border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                            <textarea rows={3} defaultValue={agent.description} className="mt-1 block w-full border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"></textarea>
                        </div>
                    </div>
                </ConfigSection>
            )}

            {activeTab === 'Model' && (
                <ConfigSection title="Model Configuration" description="Define the generative model and its parameters.">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label htmlFor="model-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Model</label>
                            <select id="model-select" value={model} onChange={(e) => setModel(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                                <option value="gpt-4.1">gpt-4.1</option>
                                <option value="gpt-4o">gpt-4o</option>
                                <option value="gpt-4.1b">gpt-4.1b</option>
                                <option value="gpt-4o-mini">gpt-4o-mini</option>
                                <option value="gpt-4o-mini-instruct">gpt-4o-mini-instruct</option>
                            </select>
                        </div>
                        <div>
                            <label htmlFor="temperature-range" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Temperature: {temperature}</label>
                            <input id="temperature-range" type="range" min="0" max="1" step="0.1" value={temperature} onChange={(e) => setTemperature(parseFloat(e.target.value))} className="mt-1 block w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600" />
                        </div>
                        <div className="md:col-span-2">
                            <label htmlFor="system-instruction" className="block text-sm font-medium text-gray-700 dark:text-gray-300">System Instruction</label>
                            <textarea id="system-instruction" placeholder="e.g. You are a helpful assistant." rows={4} value={systemInstruction} onChange={(e) => setSystemInstruction(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"></textarea>
                        </div>
                    </div>
                </ConfigSection>
            )}

            {activeTab === 'Tools' && (
                <ConfigSection title="Tools & Functions" description="Extend agent capabilities by adding tools like search or database access.">
                    {isLoadingTools ? (
                        <div className="text-center py-8">
                            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading tools...</p>
                        </div>
                    ) : (
                        <>
                            {/* Display existing tools */}
                            {tools.length > 0 && (
                                <div className="mb-6">
                                    <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-4">Existing Tools</h4>
                                    <div className="space-y-3">
                                        {tools.map((tool) => (
                                            <div key={tool.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                                                <div className="flex-1">
                                                    <h5 className="font-medium text-gray-900 dark:text-white">{tool.name}</h5>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{tool.description}</p>
                                                    {tool.category && (
                                                        <span className="inline-block mt-2 px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                                                            {tool.category}
                                                        </span>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={() => handleDeleteTool(tool.id)}
                                                    className="ml-4 p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                                                    title="Delete tool"
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                    </svg>
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {!isCreatingTool ? (
                                <button
                                    onClick={handleStartCreatingTool}
                                    className="flex items-center justify-center w-full px-4 py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 dark:text-gray-400 hover:border-blue-500 hover:text-blue-500 dark:hover:border-blue-400 dark:hover:text-blue-400 transition"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                    </svg>
                                    Add Tool or Function
                                </button>
                            ) : (
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Tool Name</label>
                                        <input
                                            type="text"
                                            value={toolName}
                                            onChange={(e) => setToolName(e.target.value)}
                                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                                        <textarea
                                            rows={3}
                                            value={toolDescription}
                                            onChange={(e) => setToolDescription(e.target.value)}
                                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                        />
                                    </div>
                                    <div className="flex flex-wrap gap-3">
                                        <button
                                            onClick={handleCreateTool}
                                            disabled={isToolLoading}
                                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:cursor-wait disabled:opacity-70"
                                        >
                                            {isToolLoading ? 'Creating...' : 'Create Tool'}
                                        </button>
                                        <button
                                            onClick={handleCancelToolCreation}
                                            className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            )}
                            {!isCreatingTool && tools.length === 0 && (
                                <div className="mt-4 text-sm text-center text-gray-500 dark:text-gray-400">
                                    No tools have been added yet.
                                </div>
                            )}
                            {toolStatus && (
                                <div className={`text-sm ${toolStatus.variant === 'success' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'} pt-4 text-center`}>
                                    {toolStatus.message}
                                </div>
                            )}
                        </>
                    )}
                </ConfigSection>
            )}

            {activeTab === 'Deployment' && (
                <ConfigSection title="Deployment & Testing" description="Test your agent with a prompt before deploying it.">
                     <div className="space-y-6">
                        <div>
                            <label htmlFor="user-prompt" className="block text-sm font-medium text-gray-700 dark:text-gray-300">User Prompt</label>
                            <textarea id="user-prompt" placeholder="Enter a prompt to test your agent..." rows={5} value={userPrompt} onChange={(e) => setUserPrompt(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"></textarea>
                        </div>
                        <button 
                            onClick={handleLaunch}
                            disabled={isLoading}
                            className="inline-flex items-center px-6 py-3 font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed"
                        >
                            {isLoading && (
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            )}
                            {isLoading ? 'Processing...' : 'Test Agent'}
                        </button>

                        {(apiResponse || apiError) && (
                            <div className="mt-6">
                                <h4 className="text-md font-semibold text-gray-800 dark:text-gray-200 mb-2">Agent Response:</h4>
                                {apiError && (
                                     <div className="p-4 bg-red-100 dark:bg-red-900/40 border border-red-300 dark:border-red-700 rounded-md">
                                        <p className="text-sm text-red-700 dark:text-red-300">{apiError}</p>
                                    </div>
                                )}
                                {apiResponse && (
                                     <div className="p-4 bg-gray-100 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-md">
                                        <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-sans">{apiResponse}</pre>
                                    </div>
                                )}
                            </div>
                        )}
                     </div>
                </ConfigSection>
            )}

        </div>
    );
};

export default AgentConfig;
