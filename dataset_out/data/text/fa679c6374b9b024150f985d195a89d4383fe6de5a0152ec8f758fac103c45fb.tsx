import type { SupervisorAgent } from '../../api/types';

interface SupervisorListProps {
  supervisors: SupervisorAgent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function SupervisorList({ supervisors, selectedId, onSelect }: SupervisorListProps) {
  return (
    <div className="space-y-1 overflow-y-auto">
      {supervisors.map((sup) => {
        const selected = sup.id === selectedId;
        return (
          <button
            key={sup.id}
            type="button"
            onClick={() => onSelect(sup.id)}
            className={`w-full text-left px-3 py-2 rounded-md border text-sm ${
              selected
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-slate-900/40 text-slate-100 border-slate-700 hover:bg-slate-800'
            }`}
          >
            <div className="font-medium">{sup.name}</div>
            <div className="text-xs text-slate-400">{sup.role}</div>
          </button>
        );
      })}
    </div>
  );
}
