
import React from 'react';
import type { Agent } from '../types';

interface AgentCardProps {
    agent: Agent;
    onSelect: () => void;
    onLaunch: () => void;
    isLaunching: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, onSelect, onLaunch, isLaunching }) => {
    const langColor = agent.language === 'Python' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800';

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 flex flex-col border border-gray-200 dark:border-gray-700">
            <div className="p-6 flex-grow">
                <div className="flex items-start justify-between">
                    <div className="flex items-start">
                        <div className="flex-shrink-0">{agent.icon}</div>
                        <div className="ml-4">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
                            <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full ${langColor} mt-1`}>
                                {agent.language}
                            </span>
                        </div>
                    </div>
                </div>
                <p className="mt-4 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    {agent.description}
                </p>
            </div>
            <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-b-lg">
                <div className="flex justify-end space-x-3">
                    <button
                        onClick={onSelect}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Configure
                    </button>
                    <button
                        onClick={onLaunch}
                        disabled={isLaunching}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white dark:bg-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:cursor-wait disabled:opacity-70"
                    >
                        {isLaunching ? 'Launching...' : 'Launch'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AgentCard;
