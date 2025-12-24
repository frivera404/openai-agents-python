import { create } from 'zustand';
import type { CommandResult, SupervisorAgent } from '../api/types';
import { getSupervisors } from '../api/agentApi';

interface CommandCenterState {
  supervisors: SupervisorAgent[];
  selectedSupervisorId: string | null;
  command: string;
  mainFeed: CommandResult[];
  resultsBySupervisor: Record<string, CommandResult[]>;
  loading: boolean;
  error: string | null;
  init: () => Promise<void>;
  setSelectedSupervisor: (id: string | null) => void;
  setCommand: (text: string) => void;
  sendCommand: () => Promise<void>;
}

export const useCommandCenterStore = create<CommandCenterState>((set, get) => ({
  supervisors: [],
  selectedSupervisorId: null,
  command: '',
  mainFeed: [],
  resultsBySupervisor: {},
  loading: false,
  error: null,

  init: async () => {
    try {
      set({ loading: true, error: null });
      const supervisors = await getSupervisors();
      set(state => ({
        supervisors,
        loading: false,
        selectedSupervisorId: state.selectedSupervisorId ?? supervisors[0]?.id ?? null,
      }));
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  },

  setSelectedSupervisor: (id) => set({ selectedSupervisorId: id }),

  setCommand: (text) => set({ command: text }),

  sendCommand: async () => {
    const { command, selectedSupervisorId, supervisors } = get();
    if (!command.trim() || !selectedSupervisorId) {
      return;
    }

    const supervisor = supervisors.find(s => s.id === selectedSupervisorId);
    if (!supervisor) {
      return;
    }

    const result: CommandResult = {
      id: crypto.randomUUID(),
      supervisorId: supervisor.id,
      supervisorName: supervisor.name,
      content: command.trim(),
      createdAt: new Date().toISOString(),
    };

    set(state => ({
      command: '',
      mainFeed: [result, ...state.mainFeed],
      resultsBySupervisor: {
        ...state.resultsBySupervisor,
        [supervisor.id]: [result, ...(state.resultsBySupervisor[supervisor.id] ?? [])],
      },
    }));
  },
}));
