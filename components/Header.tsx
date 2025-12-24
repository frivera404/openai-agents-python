import React from 'react';

interface HeaderProps {
    title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
    return (
        <header className="h-16 bg-black/20 border-b border-gray-600 flex-shrink-0 flex items-center justify-between px-6 backdrop-blur-sm">
            <h2 className="text-lg font-bold text-white">{title}</h2>
            <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-300">
                    System Status: <span className="text-green-400 font-semibold">ONLINE</span>
                </div>
                <div className="w-8 h-8 bg-tech-accent rounded-full flex items-center justify-center text-black font-bold animate-pulse">
                    A
                </div>
            </div>
        </header>
    );
};

export default Header;
