import React from 'react';
import type { Agent } from '../types';

interface AgentCardProps {
    agent: Agent;
    onSelect: () => void;
    onLaunch: () => void;
    isLaunching: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, onSelect, onLaunch, isLaunching }) => {
    const langColor =
        agent.language === 'Python'
            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
            : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';

    return (
        <div className="agent-card bg-card-gradient rounded-lg shadow-lg flex flex-col border border-gray-600 hover:border-blue-500/50">
            <div className="p-6 flex-grow">
                <div className="flex items-start justify-between">
                    <div className="flex items-start">
                        <div className="flex-shrink-0 text-tech-accent">{agent.icon}</div>
                        <div className="ml-4">
                            <h3 className="text-lg font-bold text-white">{agent.name}</h3>
                            <span
                                className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full ${langColor} mt-1`}
                            >
                                {agent.language}
                            </span>
                        </div>
                    </div>
                </div>
                <p className="mt-4 text-sm text-gray-300 leading-relaxed">{agent.description}</p>
            </div>
            <div className="border-t border-gray-600 bg-gray-800/50 p-4 rounded-b-lg">
                <div className="flex justify-end space-x-3">
                    <button onClick={onSelect} className="btn-primary">
                        Configure
                    </button>
                    <button
                        onClick={onLaunch}
                        disabled={isLaunching}
                        className="btn-secondary disabled:cursor-wait disabled:opacity-70"
                    >
                        {isLaunching ? 'Launching...' : 'Launch'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AgentCard;
