'use client';
import { useState, useEffect, useCallback } from 'react';
import { getBriefing, refreshBriefing, checkHealth } from '@/lib/api';
import type { Story } from '@/lib/api';
import { StoryCard } from './StoryCard';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { OfflineState } from '@/components/ui/OfflineState';
import { Button } from '@/components/ui/Button';

function formatTime(ts: number | null) {
  if (!ts) return null;
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function BriefingBook() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [offline, setOffline] = useState(false);
  const [offlineMessage, setOfflineMessage] = useState('Start the local API to load your briefing feed.');
  const [refreshedAt, setRefreshedAt] = useState<number | null>(null);
  
  const load = useCallback(async () => {
    setLoading(true);
    const result = await getBriefing();
    setLoading(false);
    if (result.error === 'API_UNAVAILABLE') {
      const health = await checkHealth();
      if (!health.ok) {
        setOffline(true);
        setOfflineMessage('Start the local API on port 8000 to load your briefing feed.');
      } else if (result.stories.length === 0) {
        setOffline(true);
        setOfflineMessage('No briefing items yet. Try refreshing.');
      } else {
        setOffline(false);
        setStories(result.stories);
        setRefreshedAt(result.refreshed_at);
      }
    } else {
      setOffline(false);
      setStories(result.stories);
      setRefreshedAt(result.refreshed_at);
    }
  }, []);
  
  useEffect(() => { load(); }, [load]);
  
  const handleRefresh = async () => {
    setRefreshing(true);
    const result = await refreshBriefing();
    setRefreshing(false);
    if (result.stories.length > 0) {
      setOffline(false);
      setStories(result.stories);
      setRefreshedAt(result.refreshed_at);
    }
  };
  
  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-semibold text-fg-primary">Briefing Book</h2>
          {refreshedAt && !offline && (
            <p className="text-xs text-fg-tertiary mt-0.5">Last refreshed {formatTime(refreshedAt)}</p>
          )}
        </div>
        {!offline && (
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
            loading={refreshing}
          >
            Refresh briefing ↻
          </Button>
        )}
      </div>
      
      {offline ? (
        <OfflineState message={offlineMessage} />
      ) : loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : stories.length === 0 ? (
        <div className="border rounded-lg p-8 text-center">
          <p className="text-sm text-fg-secondary">No briefing items yet.</p>
          <p className="text-xs text-fg-tertiary mt-1">Refresh to load the latest stories from your briefing sources.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {stories.map(story => <StoryCard key={story.id} story={story} />)}
        </div>
      )}
    </section>
  );
}
