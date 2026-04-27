interface RefreshProgressProps {
  progress: {
    sources: number;
    found: number;
    scored: number;
  };
}

export default function RefreshProgress({ progress }: RefreshProgressProps) {
  return (
    <div className="mb-4 flex items-center gap-4 p-3 bg-bg-secondary border border-border rounded-card text-xs text-fg-secondary">
      <span className="flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
        Scraping sources…
      </span>
      {progress.sources > 0 && (
        <span className="text-fg-tertiary">{progress.sources} sources</span>
      )}
      {progress.found > 0 && (
        <span className="text-fg-tertiary">{progress.found} items found</span>
      )}
      {progress.scored > 0 && (
        <span className="text-accent font-medium">{progress.scored} scored ≥7</span>
      )}
    </div>
  );
}
