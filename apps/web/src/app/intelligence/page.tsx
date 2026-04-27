'use client';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';

export default function IntelligencePage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [items, setItems] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadItems = () => fetch('http://localhost:8000/api/intelligence/items')
    .then(r => r.json()).then(setItems).catch(console.error);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { loadItems(); }, []);

  const dismiss = async (id: number) => {
    await fetch(`http://localhost:8000/api/intelligence/items/${id}/dismiss`, { method: 'POST' });
    loadItems();
  };

  const markAsContext = async (id: number) => {
    await fetch(`http://localhost:8000/api/intelligence/items/${id}/use-as-context`, { method: 'POST' });
    alert('Item marked for context use.');
  };

  const handleRefreshNow = async () => {
    setRefreshing(true);
    try {
      await fetch('http://localhost:8000/api/intelligence/scrape', { method: 'POST' });
      await new Promise(resolve => setTimeout(resolve, 3000));
      loadItems();
    } catch (error) {
      console.error('Refresh failed:', error);
      alert('Failed to refresh intelligence. Please try again.');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Intelligence Feed</h1>
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={handleRefreshNow} 
          loading={refreshing}
        >
          Refresh now ↻
        </Button>
      </div>
      {items.length === 0 && (
        <div className="border rounded-lg p-6">
          <p className="text-gray-500">No items yet. Click &quot;Refresh now&quot; to pull the latest intelligence.</p>
        </div>
      )}
      <div className="space-y-3">
        {items.map(item => (
          <div key={item.id} className="border rounded-lg p-4">
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
    </div>
  );
}

