'use client';

import { useEffect, useState } from 'react';
import { Eye, EyeOff, AlertCircle } from 'lucide-react';
import { getApiBase } from '@/lib/api';
import { getHeadersWithCSRF } from '@/lib/csrf';

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

type ChannelType = 'cms' | 'analytics' | 'crm' | 'syndication';
type DeliveryMode = 'manual' | 'scheduled' | 'webhook';

interface IntegrationTarget {
  id: string;
  channel_type: ChannelType;
  target_key: string;
  display_name: string;
  endpoint_url: string | null;
  delivery_mode: DeliveryMode;
  enabled: boolean;
  preferences: Record<string, string>;
}

interface SettingsConfigProps {
  onNavigateTo?: (path: string) => void;
}

export default function SettingsConfig({ onNavigateTo }: SettingsConfigProps) {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [revealedKeys, setRevealedKeys] = useState<Set<string>>(new Set());
  const [scrapeConfig, setScrapeConfig] = useState<ScrapeSource[]>([]);
  const [integrationTargets, setIntegrationTargets] = useState<IntegrationTarget[]>([]);
  const [savingIntegration, setSavingIntegration] = useState(false);
  const [integrationForm, setIntegrationForm] = useState({
    channel_type: 'cms' as ChannelType,
    target_key: '',
    display_name: '',
    endpoint_url: '',
    delivery_mode: 'scheduled' as DeliveryMode,
    enabled: true,
    preferences: '',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    setLoading(true);
    try {
      const [apiRes, scrapeRes, targetsRes] = await Promise.all([
        fetch(`${getApiBase()}/api/settings/api-keys`),
        fetch(`${getApiBase()}/api/settings/scrape-config`),
        fetch(`${getApiBase()}/api/integrations/targets`, {
          credentials: 'include',
        }),
      ]);

      if (apiRes.ok) {
        const keys = await apiRes.json();
        setApiKeys(keys);
      }

      if (scrapeRes.ok) {
        const config = await scrapeRes.json();
        setScrapeConfig(config);
      }

      if (targetsRes.ok) {
        const targets = await targetsRes.json();
        setIntegrationTargets(targets);
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

  async function saveIntegrationTarget(e: React.FormEvent) {
    e.preventDefault();
    setSavingIntegration(true);
    setError('');
    try {
      const preferences: Record<string, string> = integrationForm.preferences
        ? JSON.parse(integrationForm.preferences)
        : {};

      const payload = {
        channel_type: integrationForm.channel_type,
        target_key: integrationForm.target_key.trim(),
        display_name: integrationForm.display_name.trim(),
        endpoint_url: integrationForm.endpoint_url.trim() || null,
        delivery_mode: integrationForm.delivery_mode,
        enabled: integrationForm.enabled,
        preferences,
      };

      const res = await fetch(`${getApiBase()}/api/integrations/targets`, {
        method: 'POST',
        credentials: 'include',
        headers: getHeadersWithCSRF({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: 'Failed to save integration target' }));
        throw new Error(body.detail || 'Failed to save integration target');
      }

      setIntegrationForm({
        channel_type: 'cms',
        target_key: '',
        display_name: '',
        endpoint_url: '',
        delivery_mode: 'scheduled',
        enabled: true,
        preferences: '',
      });
      await loadSettings();
    } catch (e) {
      setError(`Failed to save integration target: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setSavingIntegration(false);
    }
  }

  async function toggleIntegrationTarget(target: IntegrationTarget) {
    setError('');
    try {
      const res = await fetch(`${getApiBase()}/api/integrations/targets/${target.id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: getHeadersWithCSRF({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          channel_type: target.channel_type,
          target_key: target.target_key,
          display_name: target.display_name,
          endpoint_url: target.endpoint_url,
          delivery_mode: target.delivery_mode,
          enabled: !target.enabled,
          preferences: target.preferences,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: 'Failed to update integration target' }));
        throw new Error(body.detail || 'Failed to update integration target');
      }
      await loadSettings();
    } catch (e) {
      setError(`Failed to update integration target: ${e instanceof Error ? e.message : String(e)}`);
    }
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
          <h2 className="text-lg font-bold text-fg-primary mb-4">Distribution integrations</h2>
          <p className="text-sm text-fg-secondary mb-4">
            Configure org-scoped CMS, CRM, analytics, and syndication delivery targets.
          </p>

          <form onSubmit={saveIntegrationTarget} className="bg-bg-secondary p-4 rounded-card border border-border space-y-3 mb-4">
            <div className="grid gap-3 md:grid-cols-2">
              <label className="text-sm text-fg-secondary">
                Channel
                <select
                  className="mt-1 w-full bg-bg-tertiary border border-border rounded-input px-2 py-2 text-sm text-fg-primary"
                  value={integrationForm.channel_type}
                  onChange={(e) => setIntegrationForm((prev) => ({ ...prev, channel_type: e.target.value as ChannelType }))}
                >
                  <option value="cms">CMS</option>
                  <option value="crm">CRM</option>
                  <option value="analytics">Analytics</option>
                  <option value="syndication">Syndication</option>
                </select>
              </label>
              <label className="text-sm text-fg-secondary">
                Delivery mode
                <select
                  className="mt-1 w-full bg-bg-tertiary border border-border rounded-input px-2 py-2 text-sm text-fg-primary"
                  value={integrationForm.delivery_mode}
                  onChange={(e) => setIntegrationForm((prev) => ({ ...prev, delivery_mode: e.target.value as DeliveryMode }))}
                >
                  <option value="scheduled">Scheduled</option>
                  <option value="manual">Manual</option>
                  <option value="webhook">Webhook</option>
                </select>
              </label>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <label className="text-sm text-fg-secondary">
                Target key
                <input
                  value={integrationForm.target_key}
                  onChange={(e) => setIntegrationForm((prev) => ({ ...prev, target_key: e.target.value }))}
                  className="mt-1 w-full bg-bg-tertiary border border-border rounded-input px-2 py-2 text-sm text-fg-primary"
                  placeholder="wordpress-main"
                  required
                />
              </label>
              <label className="text-sm text-fg-secondary">
                Display name
                <input
                  value={integrationForm.display_name}
                  onChange={(e) => setIntegrationForm((prev) => ({ ...prev, display_name: e.target.value }))}
                  className="mt-1 w-full bg-bg-tertiary border border-border rounded-input px-2 py-2 text-sm text-fg-primary"
                  placeholder="Main WordPress"
                  required
                />
              </label>
            </div>

            <label className="text-sm text-fg-secondary block">
              Endpoint URL
              <input
                value={integrationForm.endpoint_url}
                onChange={(e) => setIntegrationForm((prev) => ({ ...prev, endpoint_url: e.target.value }))}
                className="mt-1 w-full bg-bg-tertiary border border-border rounded-input px-2 py-2 text-sm text-fg-primary"
                placeholder="https://example.com/api"
              />
            </label>

            <label className="text-sm text-fg-secondary block">
              Preferences JSON
              <textarea
                value={integrationForm.preferences}
                onChange={(e) => setIntegrationForm((prev) => ({ ...prev, preferences: e.target.value }))}
                className="mt-1 w-full bg-bg-tertiary border border-border rounded-input px-2 py-2 text-xs font-mono text-fg-primary h-24"
                placeholder='{"publish_path":"/blog","content_format":"markdown"}'
              />
            </label>

            <label className="inline-flex items-center gap-2 text-sm text-fg-secondary">
              <input
                type="checkbox"
                checked={integrationForm.enabled}
                onChange={(e) => setIntegrationForm((prev) => ({ ...prev, enabled: e.target.checked }))}
              />
              Enabled
            </label>

            <button
              type="submit"
              disabled={savingIntegration}
              className="px-3 py-2 rounded-input bg-accent text-white text-sm font-medium disabled:opacity-60"
            >
              {savingIntegration ? 'Saving...' : 'Add integration target'}
            </button>
          </form>

          <div className="space-y-3">
            {integrationTargets.length === 0 ? (
              <p className="text-sm text-fg-tertiary">No integration targets configured yet</p>
            ) : integrationTargets.map(target => (
              <div key={target.id} className="bg-bg-secondary p-4 rounded-card border border-border">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-bold text-fg-primary">{target.display_name}</p>
                    <p className="text-xs text-fg-secondary">
                      {target.channel_type.toUpperCase()} · {target.delivery_mode} · {target.target_key}
                    </p>
                    {target.endpoint_url && (
                      <p className="text-xs text-fg-tertiary mt-1">{target.endpoint_url}</p>
                    )}
                  </div>
                  <button
                    onClick={() => toggleIntegrationTarget(target)}
                    className="px-3 py-1 rounded-input border border-border text-xs text-fg-secondary hover:text-fg-primary"
                  >
                    {target.enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
