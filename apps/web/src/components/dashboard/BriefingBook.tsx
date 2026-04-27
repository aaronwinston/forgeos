'use client';
import { useState, useEffect, useCallback } from 'react';
import { getBriefing, getBriefingByDate, refreshBriefing, checkHealth } from '@/lib/api';
import type { Story } from '@/lib/api';
import { StoryCard } from './StoryCard';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { OfflineState } from '@/components/ui/OfflineState';
import { Button } from '@/components/ui/Button';
import RefreshProgress from './RefreshProgress';

const MAX_ITEMS = 8;

function formatTime(ts: number | null) {
  if (!ts) return null;
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getYesterdayDate(): string {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d.toISOString().split('T')[0];
}

export function BriefingBook() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [offline, setOffline] = useState(false);
  const [offlineMessage, setOfflineMessage] = useState('Start the local API to load your briefing feed.');
  const [refreshedAt, setRefreshedAt] = useState<number | null>(null);
  const [showYesterday, setShowYesterday] = useState(false);
  const [refreshProgress, setRefreshProgress] = useState<{ sources: number; found: number; scored: number } | null>(null);

  const load = useCallback(async (yesterday = false) => {
    try {
      setLoading(true);
      const result = yesterday
        ? await getBriefingByDate(getYesterdayDate())
        : await getBriefing();
      setLoading(false);
      if (result.error === 'API_UNAVAILABLE') {
        const health = await checkHealth();
        if (!health.ok) {
          setOffline(true);
          setOfflineMessage('Unable to connect to the briefing API. Check that the local API is running on port 8000.');
        } else {
          setOffline(false);
          setStories([]);
        }
      } else {
        setOffline(false);
        setStories((result.stories ?? []).slice(0, MAX_ITEMS));
        setRefreshedAt(result.refreshed_at);
      }
    } catch (err) {
      setLoading(false);
      setOffline(true);
      setOfflineMessage('Error loading briefing. Check your connection and try again.');
      console.error('[BriefingBook] Load error:', err);
    }
  }, []);

  useEffect(() => { load(showYesterday); }, [load, showYesterday]);

  const handleRefresh = async () => {
    if (showYesterday) return; // yesterday view is read-only
    try {
      setRefreshing(true);
      setRefreshProgress({ sources: 0, found: 0, scored: 0 });
      const result = await refreshBriefing((progress) => setRefreshProgress(progress));
      setRefreshProgress(null);
      if ((result.stories ?? []).length > 0 || !result.error) {
        setOffline(false);
        setStories((result.stories ?? []).slice(0, MAX_ITEMS));
        setRefreshedAt(result.refreshed_at);
      }
    } catch (err) {
      setRefreshProgress(null);
      setOffline(true);
      setOfflineMessage('Failed to refresh briefing. Check your connection and try again.');
      console.error('[BriefingBook] Refresh error:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleToggleYesterday = () => {
    const next = !showYesterday;
    setShowYesterday(next);
    setStories([]);
    load(next);
  };

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-semibold text-fg-primary">Briefing book</h2>
          {refreshedAt && !offline && !showYesterday && (
            <p className="text-xs text-fg-tertiary mt-0.5">Last refreshed {formatTime(refreshedAt)}</p>
          )}
          {showYesterday && (
            <p className="text-xs text-fg-tertiary mt-0.5">Showing {getYesterdayDate()}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Yesterday toggle */}
          <button
            onClick={handleToggleYesterday}
            className={`text-xs px-3 py-1.5 rounded-chip border transition-colors ${
              showYesterday
                ? 'bg-accent/10 border-accent text-accent'
                : 'bg-bg-tertiary border-border text-fg-secondary hover:text-fg-primary'
            }`}
          >
            Yesterday
          </button>
          {!offline && !showYesterday && (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleRefresh}
              loading={refreshing}
            >
              Refresh ↻
            </Button>
          )}
        </div>
      </div>

      {refreshProgress && <RefreshProgress progress={refreshProgress} />}

      {offline ? (
        <OfflineState message={offlineMessage} />
      ) : loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : stories.length === 0 ? (
        <div className="border border-border rounded-card p-8 text-center">
          <p className="text-sm text-fg-secondary">
            {showYesterday ? 'No briefing items from yesterday.' : 'No briefing items yet.'}
          </p>
          <p className="text-xs text-fg-tertiary mt-1">
            {showYesterday
              ? 'Yesterday\'s scored items will appear here once they\'ve been scraped.'
              : 'Refresh to load the latest stories from your briefing sources.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {stories.map(story => <StoryCard key={story.id} story={story} />)}
        </div>
      )}
    </section>
  );
}
