import type { SupervisorAgent } from '../../api/types';
import { useCallback, KeyboardEvent } from 'react';

interface CommandInputBarProps {
  supervisors: SupervisorAgent[];
  selectedId: string | null;
  command: string;
  loading: boolean;
  onSelect: (id: string) => void;
  onChangeCommand: (text: string) => void;
  onSend: () => void;
}

export function CommandInputBar({
  supervisors,
  selectedId,
  command,
  loading,
  onSelect,
  onChangeCommand,
  onSend,
}: CommandInputBarProps) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        onSend();
      }
    },
    [onSend],
  );

  const disableSend = loading || !command.trim() || !selectedId;

  return (
    <div className="border-t border-slate-800 pt-3 mt-3">
      <div className="flex items-center gap-2 mb-2">
        <select
          className="bg-slate-900 border border-slate-700 text-slate-100 text-sm rounded px-2 py-1"
          value={selectedId ?? ''}
          onChange={(e) => onSelect(e.target.value)}
        >
          <option value="" disabled>
            Select supervisor
          </option>
          {supervisors.map((sup) => (
            <option key={sup.id} value={sup.id}>
              {sup.name}
            </option>
          ))}
        </select>
        {loading && <span className="text-xs text-slate-400">Loading supervisors…</span>}
      </div>
      <div className="flex items-end gap-2">
        <textarea
          className="flex-1 bg-slate-900 border border-slate-700 text-slate-100 text-sm rounded px-2 py-1 min-h-[48px] max-h-32 resize-y"
          placeholder="Type a command for the selected supervisor…"
          value={command}
          onChange={(e) => onChangeCommand(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="button"
          disabled={disableSend}
          onClick={onSend}
          className={`px-3 py-2 rounded text-sm font-medium ${
            disableSend
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-500'
          }`}
        >
          Send
        </button>
      </div>
    </div>
  );
}
