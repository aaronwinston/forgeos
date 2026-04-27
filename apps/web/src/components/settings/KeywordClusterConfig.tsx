'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import type { KeywordCluster } from '@/lib/types';

export default function KeywordClusterConfig() {
  const [clusters, setClusters] = useState<KeywordCluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newKeyword, setNewKeyword] = useState('');
  const [newRegion, setNewRegion] = useState('US');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadClusters();
  }, []);

  const loadClusters = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/api/intelligence/search/keywords');
      if (!response.ok) throw new Error('Failed to load keyword clusters');
      const data = await response.json();
      setClusters(data);
    } catch (err) {
      setError('Failed to load keyword clusters');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddKeyword = async () => {
    if (!newKeyword.trim()) {
      setError('Please enter a keyword');
      return;
    }

    setSaving(true);
    try {
      const response = await fetch('http://localhost:8000/api/intelligence/search/keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: newKeyword, region: newRegion }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to add keyword');
      }

      const newCluster = await response.json();
      setClusters([...clusters, newCluster]);
      setNewKeyword('');
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add keyword');
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveKeyword = async (clusterId: number) => {
    setSaving(true);
    try {
      const response = await fetch(`http://localhost:8000/api/intelligence/search/keywords/${clusterId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete keyword');

      setClusters(clusters.filter(c => c.id !== clusterId));
    } catch (err) {
      setError('Failed to delete keyword');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (cluster: KeywordCluster) => {
    setSaving(true);
    try {
      const response = await fetch(`http://localhost:8000/api/intelligence/search/keywords/${cluster.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: !cluster.active }),
      });

      if (!response.ok) throw new Error('Failed to update keyword');

      const updated = await response.json();
      setClusters(clusters.map(c => c.id === cluster.id ? updated : c));
    } catch (err) {
      setError('Failed to update keyword');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Keyword clusters</h3>
        <p className="text-sm text-fg-secondary">
          Keywords to monitor in Google Trends, GSC, and social signals. Changes apply on next scrape cycle.
        </p>
      </div>

      {error && (
        <div className="border border-red-300 rounded-card p-4 bg-red-50">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="space-y-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
            placeholder="e.g., LLM evaluation, agent observability"
            className="flex-1 border rounded-input px-3 py-2 text-sm"
            disabled={saving}
          />
          <select
            value={newRegion}
            onChange={(e) => setNewRegion(e.target.value)}
            className="border rounded-input px-3 py-2 text-sm"
            disabled={saving}
          >
            <option value="US">US</option>
            <option value="Global">Global</option>
          </select>
          <Button
            size="sm"
            onClick={handleAddKeyword}
            loading={saving}
            disabled={!newKeyword.trim()}
          >
            Add
          </Button>
        </div>

        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="border rounded-card p-3 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : clusters.length === 0 ? (
          <div className="border rounded-card p-6 text-center bg-gray-50">
            <p className="text-sm text-gray-600">No keyword clusters configured yet.</p>
            <p className="text-xs text-gray-500 mt-1">Add one to start monitoring search trends.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {clusters.map(cluster => (
              <div
                key={cluster.id}
                className="flex items-center gap-3 border rounded-card p-3"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium">{cluster.keyword}</p>
                  <p className="text-xs text-fg-tertiary">{cluster.region}</p>
                </div>
                <button
                  onClick={() => handleToggleActive(cluster)}
                  disabled={saving}
                  className={`px-3 py-1 rounded-input text-xs font-medium transition ${
                    cluster.active
                      ? 'bg-green-100 text-green-800 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                  }`}
                >
                  {cluster.active ? 'Active' : 'Inactive'}
                </button>
                <button
                  onClick={() => handleRemoveKeyword(cluster.id)}
                  disabled={saving}
                  className="px-3 py-1 rounded-input text-xs text-red-600 hover:bg-red-50 transition"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-card p-4">
        <p className="text-xs text-blue-900">
          💡 Tip: Use your highest-impact topics or product keywords. Each cluster triggers daily monitoring of Trends, GSC, and social sources.
        </p>
      </div>
    </div>
  );
}
