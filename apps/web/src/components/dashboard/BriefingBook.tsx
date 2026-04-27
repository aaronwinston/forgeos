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
    try {
      setLoading(true);
      const result = await getBriefing();
      setLoading(false);
      if (result.error === 'API_UNAVAILABLE') {
        const health = await checkHealth();
        if (!health.ok) {
          setOffline(true);
          setOfflineMessage('Unable to connect to the briefing API. Check that the local API is running on port 8000.');
          console.debug('[BriefingBook] API unavailable - health check failed');
        } else if (result.stories.length === 0) {
          setOffline(true);
          setOfflineMessage('No briefing items yet. Click refresh to fetch the latest stories.');
          console.debug('[BriefingBook] API available but no stories');
        } else {
          setOffline(false);
          setStories(result.stories);
          setRefreshedAt(result.refreshed_at);
          console.debug('[BriefingBook] Loaded', result.stories.length, 'stories');
        }
      } else {
        setOffline(false);
        setStories(result.stories);
        setRefreshedAt(result.refreshed_at);
        console.debug('[BriefingBook] Loaded', result.stories.length, 'stories');
      }
    } catch (err) {
      setOffline(true);
      setOfflineMessage('Error loading briefing. Check your connection and try again.');
      console.error('[BriefingBook] Load error:', err);
    }
  }, []);
  
  useEffect(() => { load(); }, [load]);
  
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      console.debug('[BriefingBook] Refreshing briefing feed...');
      const result = await refreshBriefing();
      if (result.stories.length > 0) {
        setOffline(false);
        setStories(result.stories);
        setRefreshedAt(result.refreshed_at);
        console.debug('[BriefingBook] Refresh successful. Loaded', result.stories.length, 'stories');
      } else {
        console.debug('[BriefingBook] Refresh returned no stories');
      }
    } catch (err) {
      setOffline(true);
      setOfflineMessage('Failed to refresh briefing. Check your connection and try again.');
      console.error('[BriefingBook] Refresh error:', err);
    } finally {
      setRefreshing(false);
    }
  };
  
  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-semibold text-fg-primary">Briefing book</h2>
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
        <div className="border border-border rounded-card p-8 text-center">
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
