export function SkeletonCard() {
  return (
    <div className="border border-border rounded-card p-4 bg-bg-secondary overflow-hidden">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-4 w-16 rounded-chip bg-bg-tertiary animate-shimmer" />
        <div className="h-3 w-8 rounded-chip bg-bg-tertiary animate-shimmer" />
      </div>
      <div className="space-y-2 mb-3">
        <div className="h-4 w-full rounded-chip bg-bg-tertiary animate-shimmer" />
        <div className="h-4 w-3/4 rounded-chip bg-bg-tertiary animate-shimmer" />
      </div>
      <div className="h-3 w-full rounded-chip bg-bg-tertiary animate-shimmer mb-2" />
      <div className="h-3 w-2/3 rounded-chip bg-bg-tertiary animate-shimmer" />
    </div>
  );
}
