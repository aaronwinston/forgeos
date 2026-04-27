'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';

interface EngineHealthReport {
  total_files: number;
  placeholder_count: number;
  thin_count: number;
  files: Array<{
    path: string;
    word_count: number;
    recommended: number;
    thinness_pct: number;
    badge: string;
  }>;
  highest_leverage_file: { path: string; thinness_pct: number };
  timestamp: string;
  cached: boolean;
}

export function EngineHealthCard() {
  const [health, setHealth] = useState<EngineHealthReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const result = await api.getEngineHealth();
        if (!('error' in result)) {
          setHealth(result as EngineHealthReport);
        }
      } catch (err) {
        console.error('[EngineHealthCard] Error:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchHealth();
  }, []);

  if (loading) {
    return (
      <div className="border border-border rounded-card p-4 bg-bg-secondary animate-pulse">
        <div className="h-6 bg-border rounded w-32 mb-2"></div>
        <div className="h-4 bg-border rounded w-48"></div>
      </div>
    );
  }

  if (!health) {
    return null;
  }

  const attentionCount = health.placeholder_count + health.thin_count;

  if (attentionCount === 0) {
    return (
      <div className="border border-border rounded-card p-4 bg-bg-secondary">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-fg-primary">Engine health</h3>
            <p className="text-xs text-fg-tertiary mt-1">All doctrine files are complete ✓</p>
          </div>
          <div className="text-2xl">✅</div>
        </div>
      </div>
    );
  }

  const highestFile = health.highest_leverage_file;

  return (
    <div className="border border-border rounded-card p-4 bg-bg-secondary">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-semibold text-fg-primary">Engine health</h3>
          <p className="text-xs text-fg-tertiary mt-1">
            {health.placeholder_count > 0 && (
              <>
                <span className="inline-block mr-3">
                  <span className="text-xs px-2 py-1 rounded-chip bg-red-500/10 text-red-600">
                    {health.placeholder_count} placeholder
                  </span>
                </span>
              </>
            )}
            {health.thin_count > 0 && (
              <span className="inline-block">
                <span className="text-xs px-2 py-1 rounded-chip bg-yellow-500/10 text-yellow-600">
                  {health.thin_count} thin
                </span>
              </span>
            )}
          </p>
        </div>
        <div className="text-lg">⚠️</div>
      </div>

      {highestFile && (
        <div className="mt-4 p-3 bg-bg-tertiary rounded-chip border border-border">
          <p className="text-xs text-fg-secondary mb-2">
            <strong>Expand first:</strong>
          </p>
          <p className="text-xs text-fg-primary font-medium mb-3">
            {highestFile.path}
          </p>
          <p className="text-xs text-fg-tertiary mb-3">
            {highestFile.word_count} / {highestFile.recommended} words
            <span className="ml-2 font-medium">
              {Math.round(highestFile.thinness_pct)}%
            </span>
          </p>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              // Navigate to Settings → Engine and open expand flow
              window.location.href = `/settings?tab=engine&expand=${encodeURIComponent(highestFile.path)}`;
            }}
          >
            Expand this file
          </Button>
        </div>
      )}
    </div>
  );
}
