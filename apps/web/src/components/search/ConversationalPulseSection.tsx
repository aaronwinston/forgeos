'use client';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import StartSocialItemModal from './StartSocialItemModal';
import { getApiBase } from '@/lib/api';
import type { ScrapeItem } from '@/lib/types';

export default function ConversationalPulseSection() {
  const [items, setItems] = useState<ScrapeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<ScrapeItem | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${getApiBase()}/api/intelligence/items?limit=20`);
      if (!response.ok) throw new Error('Failed to load items');
      const data = await response.json();
      setItems(data);
    } catch (err) {
      setError('Failed to load conversational pulse. Try refreshing.');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (item: ScrapeItem) => {
    setSelectedItem(item);
    setShowModal(true);
  };

  const getSourceBadgeColor = (source: string) => {
    switch (source.toLowerCase()) {
      case 'hackernews': return 'bg-orange-100 text-orange-800';
      case 'reddit': return 'bg-purple-100 text-purple-800';
      case 'github': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Conversational pulse</h2>
        <p className="text-sm text-fg-secondary mt-1">Where the conversation is happening, search or not</p>
      </div>

      {error && (
        <div className="border border-red-300 rounded-card p-4 bg-red-50">
          <p className="text-sm text-red-800">{error}</p>
          <Button size="sm" onClick={loadItems} variant="secondary" className="mt-2">Retry</Button>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="border rounded-card p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-full" />
            </div>
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="border rounded-card p-8 text-center">
          <p className="text-sm text-gray-700">No social items yet.</p>
          <p className="text-xs text-gray-500 mt-1">Click &quot;Refresh now&quot; to fetch conversations from Hacker News, Reddit, and GitHub.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map(item => (
            <div
              key={item.id}
              onClick={() => handleItemClick(item)}
              className="border rounded-card p-4 hover:bg-bg-tertiary cursor-pointer transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`inline-block rounded px-2 py-1 text-xs font-medium ${getSourceBadgeColor(item.source)}`}>
                      {item.source}
                    </span>
                    {item.score_relevance && (
                      <span className={`inline-block rounded px-2 py-1 text-xs ${item.score_relevance >= 7 ? 'bg-black text-white' : 'bg-gray-100'}`}>
                        {item.score_relevance.toFixed(1)}/10
                      </span>
                    )}
                  </div>
                  <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:underline block">
                    {item.title}
                  </a>
                  {item.author && <p className="text-xs text-fg-tertiary mt-1">by {item.author}</p>}
                  {item.body && <p className="text-xs text-fg-secondary mt-2 line-clamp-2">{item.body}</p>}
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleItemClick(item);
                  }}
                >
                  Use
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedItem && (
        <StartSocialItemModal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false);
            setSelectedItem(null);
          }}
          item={selectedItem}
        />
      )}
    </div>
  );
}
