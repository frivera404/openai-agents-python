import type { ReactNode } from 'react';

export interface Agent {
    id: string;
    name: string;
    description: string;
    language: 'Python' | 'Java';
    icon: ReactNode;
}

export interface Tool {
    id: string;
    name: string;
    description: string;
    category: string;
    parameters?: string;
    status: 'active' | 'inactive';
}
