'use client';
import { useRouter } from 'next/navigation';
import type { Story } from '@/lib/api';

export function StoryCard({ story }: { story: Story }) {
  const router = useRouter();

  function handleClick(e: React.MouseEvent) {
    // Ctrl/Cmd+click → open source URL in new tab
    if (e.ctrlKey || e.metaKey) {
      window.open(story.url, '_blank', 'noopener,noreferrer');
      return;
    }
    // Primary click → open workspace with story as context
    router.push(`/workspace/new?context_item=${story.id}&source_url=${encodeURIComponent(story.url)}&title=${encodeURIComponent(story.title)}`);
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => e.key === 'Enter' && handleClick(e as unknown as React.MouseEvent)}
      className="group block border border-border rounded-card p-4 bg-bg-secondary hover:border-accent/30 hover:shadow-sm transition-all cursor-pointer"
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-base">{story.icon}</span>
        <span
          className="text-xs font-medium px-2 py-0.5 rounded-chip text-white"
          style={{ backgroundColor: story.sourceColor }}
        >
          {story.source}
        </span>
        {story.trending && (
          <span className="text-xs text-warning font-medium">↑ Trending</span>
        )}
        {story.engagement_signal && (
          <span className="text-xs text-fg-tertiary ml-auto">{story.engagement_signal}</span>
        )}
      </div>
      <h3 className="text-sm font-semibold text-fg-primary leading-snug mb-2 group-hover:text-accent transition-colors line-clamp-2">
        {story.title}
      </h3>
      <p className="text-xs text-fg-secondary leading-relaxed mb-3 line-clamp-2">
        {story.why_relevant}
      </p>
      <div className="pt-2 border-t border-border flex items-end justify-between gap-2">
        <p className="text-xs text-fg-tertiary flex-1">
          <span className="font-medium text-fg-secondary">Content angle: </span>
          {story.content_angle}
        </p>
        <span className="text-xs text-fg-tertiary shrink-0">Open in workspace →</span>
      </div>
    </div>
  );
}
