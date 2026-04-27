'use client';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';

export default function IntelligencePage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadItems = async () => {
    try {
      setLoading(true);
      setError(null);
      console.debug('[Intelligence] Loading items...');
      const response = await fetch('http://localhost:8000/api/intelligence/items');
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setItems(data);
      console.debug('[Intelligence] Loaded', data.length, 'items');
    } catch (err) {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const message = err instanceof Error ? err.message : 'Failed to load intelligence';
      const userMessage = err instanceof Error && err.message.includes('API error')
        ? 'Unable to connect to intelligence service. Check that the API is running.'
        : 'Failed to load intelligence items. Please try again.';
      setError(userMessage);
      console.error('[Intelligence] Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadItems(); }, []);

  const dismiss = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/intelligence/items/${id}/dismiss`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to dismiss item');
      loadItems();
    } catch (err) {
      console.error('Dismiss failed:', err);
    }
  };

  const markAsContext = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/intelligence/items/${id}/use-as-context`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to mark item');
      alert('Item marked for context use.');
    } catch (err) {
      console.error('Mark failed:', err);
      alert('Failed to mark item. Please try again.');
    }
  };

  const handleRefreshNow = async () => {
    setRefreshing(true);
    try {
      console.debug('[Intelligence] Starting intelligence scrape...');
      const response = await fetch('http://localhost:8000/api/intelligence/scrape', { method: 'POST' });
      if (!response.ok) {
        throw new Error(`Scrape failed: ${response.status}`);
      }
      console.debug('[Intelligence] Scrape initiated, waiting for results...');
      await new Promise(resolve => setTimeout(resolve, 3000));
      await loadItems();
    } catch (err) {
      const userMessage = err instanceof Error && err.message.includes('Scrape failed')
        ? 'Failed to start intelligence scrape. Check the API and try again.'
        : 'Error refreshing intelligence. Please check your configuration.';
      setError(userMessage);
      console.error('[Intelligence] Refresh error:', err);
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Intelligence feed</h1>
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={handleRefreshNow} 
          loading={refreshing}
        >
          Refresh now ↻
        </Button>
      </div>

      {error && (
        <div className="border border-red-300 rounded-card p-4 bg-red-50">
          <p className="text-sm text-red-800 mb-2">{error}</p>
          <Button size="sm" onClick={loadItems} variant="secondary">Retry</Button>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="border rounded-card p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="border rounded-card p-8 text-center">
          <p className="text-sm text-gray-700">No intelligence items yet.</p>
          <p className="text-xs text-gray-500 mt-1">Click &quot;Refresh now&quot; to fetch the latest articles and content from your configured sources.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map(item => (
            <div key={item.id} className="border rounded-card p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex gap-2 mb-1">
                    <span className="inline-block border rounded px-1 text-xs">{item.source}</span>
                    {item.score_relevance && (
                      <span className={`inline-block rounded px-1 text-xs ${item.score_relevance >= 7 ? 'bg-black text-white' : 'bg-gray-100'}`}>
                        {item.score_relevance}/10
                      </span>
                    )}
                  </div>
                  <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:underline">{item.title}</a>
                  {item.why_relevant && <p className="text-xs text-fg-secondary mt-1">{item.why_relevant}</p>}
                  {item.score_reasoning && <p className="text-xs text-gray-500 italic mt-1">{item.score_reasoning}</p>}
                  {item.body && <p className="text-xs mt-1 line-clamp-3">{item.body}</p>}
                </div>
                <div className="flex gap-2 shrink-0">
                  <button onClick={() => markAsContext(item.id)} className="px-2 py-1 border rounded text-xs">Use</button>
                  <button onClick={() => dismiss(item.id)} className="px-2 py-1 text-xs text-gray-500 hover:text-gray-700">Dismiss</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

