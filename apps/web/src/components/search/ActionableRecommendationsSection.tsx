'use client';
import { useEffect, useState } from 'react';
import { ApiError, apiGet } from '@/lib/apiClient';
import type { SeoRecommendation } from '@/lib/types';

interface RecommendationsResponse {
  recommendations: SeoRecommendation[];
  total_count: number;
}

export default function ActionableRecommendationsSection() {
  const [recommendations, setRecommendations] = useState<SeoRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiGet<RecommendationsResponse>('/api/intelligence/search/recommendations?limit=5');
      setRecommendations(Array.isArray(data.recommendations) ? data.recommendations : []);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setRecommendations([]);
        setError(null);
        return;
      }
      console.error('Failed to load actionable recommendations:', err);
      setError('Unable to load actionable recommendations right now.');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Actionable recommendations</h2>
        <p className="text-sm text-fg-secondary mt-1">Intent-mapped SEO actions generated from search insights</p>
      </div>

      {error && (
        <div className="border border-red-300 rounded-card p-4 bg-red-50">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="border rounded-card p-4 animate-pulse h-20" />
      ) : recommendations.length === 0 ? (
        <div className="border rounded-card p-6 text-center">
          <p className="text-sm text-gray-700">No recommendations yet.</p>
          <p className="text-xs text-gray-500 mt-1">Add search insights and active keyword clusters to generate actions.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {recommendations.map((recommendation) => (
            <div key={recommendation.recommendation_id} className="border rounded-card p-4">
              <div className="flex items-center justify-between gap-3 mb-1">
                <p className="text-sm font-medium">{recommendation.topic}</p>
                <span className="inline-block border rounded px-2 py-1 text-xs">
                  {recommendation.intent.intent_stage} · {recommendation.intent.target_page_type}
                </span>
              </div>
              <p className="text-xs text-fg-secondary">{recommendation.serp_gap_summary}</p>
              <p className="text-xs mt-2">{recommendation.recommended_action}</p>
              <p className="text-xs text-gray-500 mt-2">
                Priority {recommendation.priority_score.toFixed(1)}
                {typeof recommendation.movement.position_delta === 'number' && (
                  <> · Position delta {recommendation.movement.position_delta.toFixed(1)}</>
                )}
                {typeof recommendation.movement.click_delta === 'number' && (
                  <> · Click delta {recommendation.movement.click_delta}</>
                )}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
