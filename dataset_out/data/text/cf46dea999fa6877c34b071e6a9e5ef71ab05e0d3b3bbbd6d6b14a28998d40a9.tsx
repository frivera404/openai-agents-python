import type { CommandResult } from '../../api/types';
import { ResultItem } from './ResultItem';

interface ResultListProps {
  title: string;
  results: CommandResult[];
}

export function ResultList({ title, results }: ResultListProps) {
  const handleCopyAll = async () => {
    const text = results.map((r) => r.content).join('\n\n---\n\n');
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Copy all failed', err);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-sm font-semibold text-slate-100">{title}</h2>
        <button
          type="button"
          onClick={handleCopyAll}
          className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-200 hover:bg-slate-700"
        >
          Copy all
        </button>
      </div>
      <div className="space-y-2 overflow-y-auto flex-1">
        {results.map((r) => (
          <ResultItem key={r.id} result={r} />
        ))}
        {results.length === 0 && (
          <div className="text-xs text-slate-500 italic">No results yet.</div>
        )}
      </div>
    </div>
  );
}
