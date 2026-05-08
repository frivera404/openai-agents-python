
import React from 'react';

interface HeaderProps {
    title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
    return (
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex-shrink-0 flex items-center justify-between px-6">
            <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-200">{title}</h2>
            <div>
                {/* Placeholder for user profile or actions */}
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    A
                </div>
            </div>
        </header>
    );
};

export default Header;
