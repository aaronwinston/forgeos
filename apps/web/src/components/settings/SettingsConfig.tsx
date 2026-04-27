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
    return <div className="p-6 text-gray-500">Loading settings...</div>;
  }

  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-4 flex gap-2">
            <AlertCircle size={16} className="text-red-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* API Keys Section */}
        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-4">API keys</h2>
          <p className="text-sm text-gray-600 mb-4">Read-only display of configured API keys</p>
          <div className="space-y-3">
            {apiKeys.length === 0 ? (
              <p className="text-sm text-gray-500">No API keys configured</p>
            ) : (
              apiKeys.map(key => (
                <div key={key.name} className="flex items-center gap-3 bg-gray-50 p-4 rounded border">
                  <div className="flex-1">
                    <p className="text-sm font-mono font-medium text-gray-900">{key.name}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <code className="text-xs bg-gray-900 text-gray-100 px-2 py-1 rounded font-mono">
                      {revealedKeys.has(key.name) ? key.value : key.masked}
                    </code>
                    <button
                      onClick={() => toggleKeyReveal(key.name)}
                      className="p-1 hover:bg-gray-200 rounded text-gray-600"
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

        {/* Scrape Config Section */}
        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-4">Intelligence scraping</h2>
          <p className="text-sm text-gray-600 mb-4">
            Manage scrape sources for intelligence gathering.
            <button
              onClick={() => onNavigateTo?.('context/07_research/intelligence-scoring-prompt.md')}
              className="ml-2 text-blue-600 hover:text-blue-700 underline text-sm"
            >
              Edit scoring logic →
            </button>
          </p>
          <div className="space-y-3">
            {scrapeConfig.length === 0 ? (
              <p className="text-sm text-gray-500">No scrape sources configured</p>
            ) : (
              scrapeConfig.map(source => (
                <div key={source.id} className="bg-gray-50 p-4 rounded border">
                  <div className="flex items-center gap-3 mb-3">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" checked={source.enabled} readOnly disabled className="rounded" />
                      <span className="text-sm font-medium text-gray-900">{source.name}</span>
                    </label>
                  </div>
                  {Object.keys(source.params || {}).length > 0 && (
                    <div className="ml-6 space-y-2">
                      {Object.entries(source.params).map(([k, v]) => (
                        <p key={k} className="text-xs text-gray-600">
                          <span className="font-mono text-gray-700">{k}</span>: <span className="text-gray-500">{v}</span>
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>

        {/* Integrations Section */}
        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-4">Integrations</h2>
          <div className="grid gap-4 md:grid-cols-3">
            {INTEGRATIONS.map(integration => (
              <div key={integration.id} className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded border border-gray-200 h-32 flex flex-col">
                <h3 className="text-sm font-bold text-gray-900">{integration.name}</h3>
                <p className="text-xs text-gray-600 mt-2">{integration.description}</p>
                <div className="mt-auto pt-3 border-t border-gray-300">
                  <p className="text-xs text-gray-500 font-medium">{integration.status}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
