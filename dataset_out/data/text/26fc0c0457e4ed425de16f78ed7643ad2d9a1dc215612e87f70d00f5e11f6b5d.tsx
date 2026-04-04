import type { CommandResult } from '../../api/types';
import { useState } from 'react';

interface ResultItemProps {
  result: CommandResult;
}

export function ResultItem({ result }: ResultItemProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(result.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (err) {
      console.error('Copy failed', err);
    }
  };

  const date = new Date(result.createdAt);

  return (
    <div className="relative border border-slate-700 rounded-lg p-3 bg-slate-900/60">
      <div className="flex items-center justify-between mb-2 text-xs text-slate-400">
        <span>{result.supervisorName}</span>
        <span>{date.toLocaleTimeString()}</span>
      </div>
      <pre className="whitespace-pre-wrap text-sm text-slate-100 font-mono">
        {result.content}
      </pre>
      <button
        type="button"
        onClick={handleCopy}
        className="absolute top-2 right-2 text-xs px-2 py-1 rounded bg-slate-800 text-slate-200 hover:bg-slate-700"
      >
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  );
}
