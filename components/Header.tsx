import React from 'react';
import useMcpStatus from '../hooks/useMcpStatus';

interface HeaderProps {
    title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
    const { status, isOnline } = useMcpStatus();

    return (
        <header className="h-16 bg-black/20 border-b border-gray-600 flex-shrink-0 flex items-center justify-between px-4 md:px-6 backdrop-blur-sm">
            <button className="md:hidden p-2 mr-2 text-gray-300 hover:text-white" aria-label="Toggle sidebar">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
            <h2 className="text-lg font-bold text-white">{title}</h2>
            <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-300">
                    System Status:{' '}
                    {status === 'unknown' ? (
                        <span className="text-yellow-400 font-semibold">CONNECTING</span>
                    ) : isOnline ? (
                        <span className="text-green-400 font-semibold">ONLINE</span>
                    ) : (
                        <span className="text-red-400 font-semibold">OFFLINE</span>
                    )}
                </div>
                <div
                    aria-hidden
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-black font-bold ${
                        isOnline ? 'bg-green-400' : status === 'unknown' ? 'bg-yellow-400' : 'bg-red-400'
                    }`}
                >
                    A
                </div>
            </div>
        </header>
    );
};

export default Header;
