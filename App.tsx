import React, { useState, useCallback, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import AgentCatalog from './pages/AgentCatalog';
import AgentConfig from './pages/AgentConfig';
import PlaceholderPage from './pages/PlaceholderPage';
import { ToolsPage } from './frontend/src/pages/ToolsPage';
import BackendGuide from './pages/BackendGuide';
import CommunicationCenter from './pages/CommunicationCenter';
import { AGENTS } from './constants';
import type { Agent } from './types';
import { launchAgent } from './services/openaiService';

const StatusBanner: React.FC<{
    banner: { text: string; variant: 'success' | 'error' };
}> = ({ banner }) => {
    const variantStyles: Record<'success' | 'error', string> = {
        success: 'bg-emerald-500/90 text-white border-emerald-600 border-l-emerald-500',
        error: 'bg-rose-500/90 text-white border-rose-600 border-l-rose-500',
    };
    const icon = banner.variant === 'success' ? '✅' : '⚠️';

    return (
        <div
            role="status"
            aria-live="polite"
            className={`status-banner flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium shadow-lg animate-slide-in ${variantStyles[banner.variant]}`}
        >
            <span className="text-base">{icon}</span>
            <span>{banner.text}</span>
        </div>
    );
};

const App: React.FC = () => {
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
        const [activePage, setActivePage] = useState<string>('Communication Center');
    const [launchingAgentId, setLaunchingAgentId] = useState<string | null>(null);
    const [statusBanner, setStatusBanner] = useState<{
        text: string;
        variant: 'success' | 'error';
    } | null>(null);
    const statusTimeoutRef = useRef<number | null>(null);

    const handleSelectAgent = useCallback((agent: Agent) => {
        setSelectedAgent(agent);
        setActivePage(agent.name);
    }, []);

    const handleBackToCatalog = useCallback(() => {
        setSelectedAgent(null);
        setActivePage('Agents');
    }, []);

    const handleNavClick = useCallback((page: string) => {
        setSelectedAgent(null);
        setActivePage(page);
    }, []);

    const showStatusBanner = useCallback((text: string, variant: 'success' | 'error') => {
        if (statusTimeoutRef.current) {
            window.clearTimeout(statusTimeoutRef.current);
        }
        setStatusBanner({ text, variant });
        statusTimeoutRef.current = window.setTimeout(() => {
            setStatusBanner(null);
        }, 5000);
    }, []);

    const handleQuickLaunch = useCallback(
        async (agent: Agent) => {
            setLaunchingAgentId(agent.id);
            try {
                const response = await launchAgent({
                    agentId: agent.id,
                    model: 'gpt-4.1',
                    temperature: 0.6,
                    systemInstruction: `You are ${agent.name} ready to help the user.`,
                    prompt: `Provide a concise summary of how the ${agent.name} helps users and why it is useful.`,
                    tools: [],
                });
                showStatusBanner(`Quick launch succeeded: ${response}`, 'success');
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Unknown error';
                showStatusBanner(`Quick launch failed: ${message}`, 'error');
            } finally {
                setLaunchingAgentId(null);
            }
        },
        [showStatusBanner]
    );

    const renderContent = () => {
        if (selectedAgent) {
            return <AgentConfig agent={selectedAgent} onBack={handleBackToCatalog} />;
        }

        switch (activePage) {
            case 'Agents':
                return (
                    <AgentCatalog
                        agents={AGENTS}
                        onSelectAgent={handleSelectAgent}
                        onLaunch={handleQuickLaunch}
                        launchingAgentId={launchingAgentId}
                    />
                );
            case 'Tools':
                return <ToolsPage />;
            case 'Communication Center':
                return <CommunicationCenter />;
            default:
                return <AgentCatalog agents={AGENTS} onSelectAgent={handleSelectAgent} />;
        }
    };

    const getHeaderTitle = () => {
        if (selectedAgent) return `Agents / ${selectedAgent.name} / Configure`;
        return activePage;
    };

    return (
        <div className="flex h-screen bg-tech-gradient font-sans text-gray-100">
            <Sidebar activePage={activePage} onNavClick={handleNavClick} />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Header title={getHeaderTitle()} />
                {statusBanner && (
                    <div className="px-6 py-3 animate-fade-in">
                        <StatusBanner banner={statusBanner} />
                    </div>
                )}
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-tech-gradient">
                    <div className="animate-fade-in">{renderContent()}</div>
                </main>
            </div>
        </div>
    );
};

export default App;
