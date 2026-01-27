import React, { useEffect, useState } from 'react';
import { getDeployedAgents, sendAgentCommand } from '../services/openaiService';

const MODEL_OPTIONS = [
    { value: 'gpt-4.1', label: 'gpt-4.1 (default)' },
    { value: 'gpt-4o-mini', label: 'gpt-4o-mini (cheaper)' },
    { value: 'gpt-5.1', label: 'gpt-5.1' },
];

const CommunicationCenter: React.FC = () => {
    const [agents, setAgents] = useState<{ agentId: string; assistantId: string }[]>([]);
    const [selected, setSelected] = useState<string>('');
    const [prompt, setPrompt] = useState('');
    const [result, setResult] = useState<string | null>(null);
    const [history, setHistory] = useState<Array<{ assistantId: string; text: string }>>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [modelByAgent, setModelByAgent] = useState<Record<string, string>>({});

    useEffect(() => {
        const load = async () => {
            try {
                const deployed = await getDeployedAgents();
                const list = Object.keys(deployed).map((k) => ({
                    agentId: k,
                    assistantId: deployed[k],
                }));
                setAgents(list);
            } catch (err) {
                console.error('Failed to load deployed agents', err);
                // Fallback: include a small set of known local demo assistants so the
                // UI remains usable even when the backend /api/agents/deployed
                // endpoint cannot be reached in local development.
                const FALLBACK_AGENTS: { [k: string]: string } = {
                    supervisor: 'asst_aoU291xGQgwlqgoQsxoWYfbQ',
                    'layer-manager': 'asst_gWX3gVfbHwVn9y7wm0FZml22',
                    'affiliate-manager': 'asst_XZqf46Wxz4XL9pI7VHraZQEi',
                    coder: 'asst_Tswpu395P3VGnEuMwcOga1l6',
                };
                const list = Object.keys(FALLBACK_AGENTS).map((k) => ({
                    agentId: k,
                    assistantId: FALLBACK_AGENTS[k],
                }));
                setAgents(list);
            }
        };
        load();
    }, []);

    const currentModel = selected ? modelByAgent[selected] ?? MODEL_OPTIONS[0].value : MODEL_OPTIONS[0].value;

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selected || !prompt.trim()) return;
        setIsLoading(true);
        try {
            const resp = await sendAgentCommand({
                assistantId: selected,
                prompt,
                model: currentModel,
                temperature: 0.7,
            });
            // response might contain a `text` property and metadata
            const text =
                resp.text || (typeof resp === 'string' ? resp : JSON.stringify(resp, null, 2));
            setResult(text);
            setHistory((h) => [{ assistantId: selected, text }, ...h]);
            setPrompt('');
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Network error';
            setResult(`Error: ${message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6 md:p-8">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Communication Center
                </h1>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                    Send commands to deployed assistants and view their responses in real-time.
                </p>
            </div>

            <div className="mt-6 bg-white dark:bg-gray-800 p-6 rounded-lg border">
                <form onSubmit={handleSend} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Select Deployed Agent
                        </label>
                        <select
                            value={selected}
                            onChange={(e) => setSelected(e.target.value)}
                            className="w-full border rounded-md px-3 py-2 dark:bg-gray-700 dark:border-gray-600"
                        >
                            <option value="">Select a deployed assistant...</option>
                            {agents.map((a) => (
                                <option key={a.assistantId} value={a.assistantId}>
                                    {a.agentId} ({a.assistantId})
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Model (per agent)
                        </label>
                        <select
                            value={currentModel}
                            onChange={(e) => {
                                const value = e.target.value;
                                setModelByAgent((prev) =>
                                    selected ? { ...prev, [selected]: value } : prev,
                                );
                            }}
                            disabled={!selected}
                            className="w-full border rounded-md px-3 py-2 dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50"
                        >
                            {MODEL_OPTIONS.map((opt) => (
                                <option key={opt.value} value={opt.value}>
                                    {opt.label}
                                </option>
                            ))}
                        </select>
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                            Each assistant remembers its last-used model. Default is gpt-4.1.
                        </p>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Command
                        </label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            rows={4}
                            className="w-full border rounded-md px-3 py-2 dark:bg-gray-700 dark:border-gray-600"
                            placeholder="Enter the command or instruction to send to the deployed assistant..."
                        />
                    </div>
                    <div>
                        <button
                            type="submit"
                            disabled={isLoading || !selected}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                        >
                            {isLoading ? 'Sending...' : 'Send Command'}
                        </button>
                    </div>
                </form>
                {result && (
                    <div className="mt-4">
                        <h3 className="text-lg font-semibold">Latest Response</h3>
                        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-md border mt-2">
                            <pre className="whitespace-pre-wrap">{result}</pre>
                        </div>
                    </div>
                )}
            </div>

            <div className="mt-6 bg-white dark:bg-gray-800 p-6 rounded-lg border">
                <h2 className="text-xl font-bold">Recent Responses</h2>
                <div className="mt-4 space-y-4">
                    {history.map((h, idx) => (
                        <div key={idx} className="border rounded p-3 bg-gray-50 dark:bg-gray-700">
                            <div className="text-sm text-gray-500">{h.assistantId}</div>
                            <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-100 mt-2">
                                {h.text}
                            </pre>
                        </div>
                    ))}
                    {history.length === 0 && (
                        <div className="text-gray-500">
                            No responses yet. Send a command to a deployed assistant above.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CommunicationCenter;
