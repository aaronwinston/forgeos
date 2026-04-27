'use client';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import StartInsightModal from './StartInsightModal';
import { getApiBase } from '@/lib/api';
import type { SearchInsight } from '@/lib/types';

export default function DefendingPositionSection() {
  const [insights, setInsights] = useState<SearchInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInsight, setSelectedInsight] = useState<SearchInsight | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${getApiBase()}/api/intelligence/search/insights`);
      if (!response.ok) throw new Error('Failed to load insights');
      const data = await response.json();
      // Filter for defending position: we rank top 10, but trends is flat or falling
      const defending = data.filter((insight: SearchInsight) =>
        insight.our_gsc_position &&
        insight.our_gsc_position <= 10 &&
        (insight.trends_momentum === 'steady' || insight.trends_momentum === 'falling')
      );
      setInsights(defending);
    } catch (err) {
      setError('Failed to load defending position data. Try refreshing.');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInsightClick = (insight: SearchInsight) => {
    setSelectedInsight(insight);
    setShowModal(true);
  };

  const getTrendIcon = (momentum: string) => {
    switch (momentum) {
      case 'rising': return '↑';
      case 'falling': return '↓';
      case 'steady': return '↔';
      default: return '—';
    }
  };

  const getTrendColor = (momentum: string) => {
    switch (momentum) {
      case 'rising': return 'text-green-600';
      case 'falling': return 'text-red-600';
      case 'steady': return 'text-gray-600';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Defending position</h2>
        <p className="text-sm text-fg-secondary mt-1">Queries we rank top 10 for, but search interest is declining</p>
      </div>

      {error && (
        <div className="border border-red-300 rounded-card p-4 bg-red-50">
          <p className="text-sm text-red-800">{error}</p>
          <Button size="sm" onClick={loadInsights} variant="secondary" className="mt-2">Retry</Button>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="border rounded-card p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-3/4" />
            </div>
          ))}
        </div>
      ) : insights.length === 0 ? (
        <div className="border rounded-card p-8 text-center">
          <p className="text-sm text-gray-700">No queries to defend yet.</p>
          <p className="text-xs text-gray-500 mt-1">Insights will appear here when you have top 10 rankings on declining searches.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {insights.map(insight => (
            <div
              key={insight.id}
              onClick={() => handleInsightClick(insight)}
              className="border rounded-card p-4 hover:bg-bg-tertiary cursor-pointer transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium text-sm">{insight.topic}</h3>
                    <span className={`text-sm font-semibold ${getTrendColor(insight.trends_momentum)}`}>
                      {getTrendIcon(insight.trends_momentum)}
                    </span>
                  </div>
                  <p className="text-xs text-fg-secondary">{insight.insight_text}</p>
                  <div className="flex gap-2 mt-2">
                    <span className="inline-block border rounded px-2 py-1 text-xs bg-blue-50">
                      Position: {Math.round(insight.our_gsc_position || 0)}
                    </span>
                    {insight.our_gsc_clicks && (
                      <span className="inline-block border rounded px-2 py-1 text-xs">
                        {insight.our_gsc_clicks} clicks/mo
                      </span>
                    )}
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleInsightClick(insight);
                  }}
                >
                  Refresh content
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedInsight && (
        <StartInsightModal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false);
            setSelectedInsight(null);
          }}
          insight={selectedInsight}
        />
      )}
    </div>
  );
}
