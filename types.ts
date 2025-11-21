
import type { ReactNode } from 'react';

export interface Agent {
  id: string;
  name: string;
  description: string;
  language: 'Python' | 'Java';
  icon: ReactNode;
}
