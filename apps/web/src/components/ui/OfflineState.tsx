interface OfflineStateProps {
  message?: string;
  command?: string;
}

export function OfflineState({ message = "Start the local API to load your briefing feed.", command = "cd apps/api && python -m uvicorn main:app --reload" }: OfflineStateProps) {
  return (
    <div className="flex flex-col items-start gap-3 p-5 bg-bg-tertiary border border-border rounded-card">
      <div className="flex items-center gap-2 text-fg-secondary">
        <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-sm">{message}</p>
      </div>
      <code className="text-xs font-mono bg-bg-secondary border border-border rounded px-3 py-2 text-fg-primary w-full block">
        {command}
      </code>
    </div>
  );
}
