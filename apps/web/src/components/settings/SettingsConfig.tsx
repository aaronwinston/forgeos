'use client';

import { useEffect, useState } from 'react';
import { Eye, EyeOff, AlertCircle } from 'lucide-react';

interface ApiKey {
  name: string;
  value: string;
  masked: string;
}

interface ScrapeSource {
  id: string;
  name: string;
  enabled: boolean;
  params: Record<string, string>;
}

const INTEGRATIONS = [
  {
    id: 'slack',
    name: 'Slack',
    description: 'Post content on publish, mention on replies',
    status: 'v2, coming soon',
  },
  {
    id: 'gmail',
    name: 'Gmail',
    description: 'Create and send draft emails directly',
    status: 'v2, coming soon',
  },
  {
    id: 'hubspot',
    name: 'HubSpot',
    description: 'Sync contacts, trigger on deal stage',
    status: 'v2, coming soon',
  },
];

interface SettingsConfigProps {
  onNavigateTo?: (path: string) => void;
}

export default function SettingsConfig({ onNavigateTo }: SettingsConfigProps) {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [revealedKeys, setRevealedKeys] = useState<Set<string>>(new Set());
  const [scrapeConfig, setScrapeConfig] = useState<ScrapeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    setLoading(true);
    try {
      const [apiRes, scrapeRes] = await Promise.all([
        fetch('http://localhost:8000/api/settings/api-keys'),
        fetch('http://localhost:8000/api/settings/scrape-config'),
      ]);

      if (apiRes.ok) {
        const keys = await apiRes.json();
        setApiKeys(keys);
      }

      if (scrapeRes.ok) {
        const config = await scrapeRes.json();
        setScrapeConfig(config);
      }
    } catch (e) {
      setError(`Failed to load settings: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoading(false);
    }
  }

  function toggleKeyReveal(keyName: string) {
    const newRevealed = new Set(revealedKeys);
    if (newRevealed.has(keyName)) {
      newRevealed.delete(keyName);
    } else {
      newRevealed.add(keyName);
    }
    setRevealedKeys(newRevealed);
  }

  if (loading) {
    return <div className="p-6 text-fg-secondary">Loading settings...</div>;
  }

  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {error && (
          <div className="bg-bg-tertiary border border-error/30 rounded-card p-4 flex gap-2">
            <AlertCircle size={16} className="text-error mt-0.5 flex-shrink-0" />
            <p className="text-sm text-error">{error}</p>
          </div>
        )}

        {/* API keys section */}
        <section>
          <h2 className="text-lg font-bold text-fg-primary mb-4">API keys</h2>
          <p className="text-sm text-fg-secondary mb-4">Read-only display of configured API keys</p>
          <div className="space-y-3">
            {apiKeys.length === 0 ? (
              <p className="text-sm text-fg-tertiary">No API keys configured</p>
            ) : (
              apiKeys.map(key => (
                <div key={key.name} className="flex items-center gap-3 bg-bg-secondary p-4 rounded-card border border-border">
                  <div className="flex-1">
                    <p className="text-sm font-mono font-medium text-fg-primary">{key.name}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <code className="text-xs bg-bg-tertiary text-fg-primary px-2 py-1 rounded-input font-mono border border-border">
                      {revealedKeys.has(key.name) ? key.value : key.masked}
                    </code>
                    <button
                      onClick={() => toggleKeyReveal(key.name)}
                      className="p-1 hover:bg-bg-tertiary rounded-input text-fg-secondary"
                      title={revealedKeys.has(key.name) ? 'Hide' : 'Show'}
                    >
                      {revealedKeys.has(key.name) ? (
                        <EyeOff size={16} />
                      ) : (
                        <Eye size={16} />
                      )}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Intelligence scraping section */}
        <section>
          <h2 className="text-lg font-bold text-fg-primary mb-4">Intelligence scraping</h2>
          <p className="text-sm text-fg-secondary mb-4">
            Manage scrape sources for intelligence gathering.
            <button
              onClick={() => onNavigateTo?.('context/07_research/intelligence-scoring-prompt.md')}
              className="ml-2 text-accent hover:text-accent/80 underline text-sm"
            >
              Edit scoring logic →
            </button>
          </p>
          <div className="space-y-3">
            {scrapeConfig.length === 0 ? (
              <p className="text-sm text-fg-tertiary">No scrape sources configured</p>
            ) : (
              scrapeConfig.map(source => (
                <div key={source.id} className="bg-bg-secondary p-4 rounded-card border border-border">
                  <div className="flex items-center gap-3 mb-3">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" checked={source.enabled} readOnly disabled className="rounded-chip" />
                      <span className="text-sm font-medium text-fg-primary">{source.name}</span>
                    </label>
                  </div>
                  {Object.keys(source.params || {}).length > 0 && (
                    <div className="ml-6 space-y-2">
                      {Object.entries(source.params).map(([k, v]) => (
                        <p key={k} className="text-xs text-fg-secondary">
                          <span className="font-mono text-fg-secondary">{k}</span>: <span className="text-fg-tertiary">{v}</span>
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>

        {/* Integrations section */}
        <section>
          <h2 className="text-lg font-bold text-fg-primary mb-4">Integrations</h2>
          <div className="grid gap-4 md:grid-cols-3">
            {INTEGRATIONS.map(integration => (
              <div key={integration.id} className="bg-bg-secondary p-4 rounded-card border border-border h-32 flex flex-col">
                <h3 className="text-sm font-bold text-fg-primary">{integration.name}</h3>
                <p className="text-xs text-fg-secondary mt-2">{integration.description}</p>
                <div className="mt-auto pt-3 border-t border-border">
                  <p className="text-xs text-fg-tertiary font-medium">{integration.status}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
