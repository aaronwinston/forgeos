export default function RefreshProgress() {
  return (
    <div className="mb-4 flex items-center gap-3 p-3 bg-bg-secondary border border-border rounded-card text-xs text-fg-secondary">
      <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse flex-shrink-0" />
      <span>Refreshing… this may take ~30 seconds</span>
    </div>
  );
}
