'use client';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { ApiError, apiGet, apiPost } from '@/lib/apiClient';
import ErrorBoundary from '@/components/ErrorBoundary';

interface PlanningQueueItem {
  item_id: number;
  title: string;
  source: string;
  source_url: string;
  rank_score: number;
  score_signal: number;
  recency_signal: number;
  strategic_fit_signal: number;
  strategic_fit_reasons: string[];
  linkage: {
    suggested_content_type: string;
    suggested_playbook: string;
    suggested_lifecycle_state: string;
    owner_placeholder: string;
  };
}

interface ConversionTaxonomyDefinition {
  id: number;
  event_key: string;
  funnel_stage: string;
  definition: string;
  primary_cta: string | null;
  success_metric: string | null;
}

interface ConversionOutcomeSnapshot {
  id: number;
  period_label: string;
  visitors: number | null;
  conversions: number | null;
  conversion_rate: number | null;
  observed_outcome: string | null;
}

interface DeliverableCTAExperiment {
  id: number;
  experiment_key: string;
  variant_label: string;
  status: string;
  conversion_rate: number | null;
  observed_outcome: string | null;
}

interface ConversionLoopData {
  deliverable_id: number;
  content_type: string;
  taxonomy_definitions: ConversionTaxonomyDefinition[];
  conversion_outcomes: ConversionOutcomeSnapshot[];
  cta_experiments: DeliverableCTAExperiment[];
}

export default function IntelligencePage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [items, setItems] = useState<any[]>([]);
  const [planningQueue, setPlanningQueue] = useState<PlanningQueueItem[]>([]);
  const [planningError, setPlanningError] = useState<string | null>(null);
  const [conversionLoop, setConversionLoop] = useState<ConversionLoopData | null>(null);
  const [conversionError, setConversionError] = useState<string | null>(null);
  const [deliverableIdInput, setDeliverableIdInput] = useState('');
  const [loadingConversion, setLoadingConversion] = useState(false);
  const [taxonomyForm, setTaxonomyForm] = useState({
    event_key: '',
    funnel_stage: '',
    definition: '',
    primary_cta: '',
    success_metric: '',
  });
  const [outcomeForm, setOutcomeForm] = useState({
    period_label: '',
    visitors: '',
    conversions: '',
    conversion_rate: '',
    observed_outcome: '',
    notes: '',
  });
  const [ctaForm, setCtaForm] = useState({
    experiment_key: '',
    variant_label: 'A',
    status: 'active',
    conversion_rate: '',
    observed_outcome: '',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadItems = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      console.debug('[Intelligence] Loading items...');
      const data = await apiGet<unknown[]>('/api/intelligence/items');
      setItems(data);
      console.debug('[Intelligence] Loaded', data.length, 'items');
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        // API routes are unavailable in this deployment; show empty state instead of error.
        setItems([]);
        setError(null);
        return;
      }
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

  const loadPlanningQueue = async (): Promise<void> => {
    try {
      setPlanningError(null);
      const data = await apiGet<PlanningQueueItem[]>('/api/intelligence/planning/queue?limit=10');
      setPlanningQueue(Array.isArray(data) ? data : []);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setPlanningQueue([]);
        setPlanningError(null);
        return;
      }
      console.error('[Intelligence] Planning queue load error:', err);
      setPlanningError('Unable to load the weekly planning queue right now.');
      setPlanningQueue([]);
    }
  };

  const loadConversionLoop = async (deliverableId: number): Promise<void> => {
    try {
      setLoadingConversion(true);
      setConversionError(null);
      const data = await apiGet<ConversionLoopData>(`/api/deliverables/${deliverableId}/conversion-loop`);
      setConversionLoop(data);
    } catch (err) {
      console.error('[Intelligence] Conversion loop load error:', err);
      setConversionLoop(null);
      setConversionError('Unable to load conversion loop artifacts for this deliverable.');
    } finally {
      setLoadingConversion(false);
    }
  };

  useEffect(() => {
    void Promise.all([loadItems(), loadPlanningQueue()]);
  }, []);

  const dismiss = async (id: number) => {
    try {
      await apiPost(`/api/intelligence/items/${id}/dismiss`);
      loadItems();
    } catch (err) {
      console.error('Dismiss failed:', err);
    }
  };

  const markAsContext = async (id: number) => {
    try {
      await apiPost(`/api/intelligence/items/${id}/use-as-context`);
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
      await apiPost(`/api/intelligence/scrape`);
      console.debug('[Intelligence] Scrape initiated, waiting for results...');
      await new Promise(resolve => setTimeout(resolve, 3000));
      await Promise.all([loadItems(), loadPlanningQueue()]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setError(null);
        return;
      }
      const userMessage = err instanceof Error && err.message.includes('Scrape failed')
        ? 'Failed to start intelligence scrape. Check the API and try again.'
        : 'Error refreshing intelligence. Please check your configuration.';
      setError(userMessage);
      console.error('[Intelligence] Refresh error:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleLoadConversionLoop = async () => {
    const parsedId = parseInt(deliverableIdInput, 10);
    if (!Number.isFinite(parsedId) || parsedId <= 0) {
      setConversionError('Enter a valid deliverable ID.');
      return;
    }
    await loadConversionLoop(parsedId);
  };

  const saveTaxonomyDefinition = async () => {
    if (!conversionLoop) return;
    await apiPost(`/api/deliverables/${conversionLoop.deliverable_id}/conversion-taxonomy`, taxonomyForm);
    setTaxonomyForm({ event_key: '', funnel_stage: '', definition: '', primary_cta: '', success_metric: '' });
    await loadConversionLoop(conversionLoop.deliverable_id);
  };

  const saveConversionOutcome = async () => {
    if (!conversionLoop) return;
    const payload = {
      ...outcomeForm,
      visitors: outcomeForm.visitors ? Number(outcomeForm.visitors) : null,
      conversions: outcomeForm.conversions ? Number(outcomeForm.conversions) : null,
      conversion_rate: outcomeForm.conversion_rate ? Number(outcomeForm.conversion_rate) : null,
    };
    await apiPost(`/api/deliverables/${conversionLoop.deliverable_id}/conversion-outcomes`, payload);
    setOutcomeForm({ period_label: '', visitors: '', conversions: '', conversion_rate: '', observed_outcome: '', notes: '' });
    await loadConversionLoop(conversionLoop.deliverable_id);
  };

  const saveCtaExperiment = async () => {
    if (!conversionLoop) return;
    const payload = {
      ...ctaForm,
      conversion_rate: ctaForm.conversion_rate ? Number(ctaForm.conversion_rate) : null,
    };
    await apiPost(`/api/deliverables/${conversionLoop.deliverable_id}/cta-experiments`, payload);
    setCtaForm({ experiment_key: '', variant_label: 'A', status: 'active', conversion_rate: '', observed_outcome: '' });
    await loadConversionLoop(conversionLoop.deliverable_id);
  };

  const intelligenceFallback = (error: Error, reset: () => void) => (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 p-8">
      <h2 className="text-xl font-semibold text-red-600">Intelligence feed failed to load</h2>
      <p className="text-sm text-gray-500">{error.message}</p>
      <div className="flex gap-3">
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Try again
        </button>
        <a
          href="/dashboard"
          className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
        >
          Back to dashboard
        </a>
      </div>
    </div>
  );

  return (
    <ErrorBoundary fallback={intelligenceFallback}>
    <div className="page-shell">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Intelligence feed</h1>
          <p className="text-sm text-fg-secondary mt-1">Content signals, ranking priorities, and conversion loop artifacts.</p>
        </div>
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
        <div className="surface-card border-error/40 bg-error/10 p-4">
          <p className="text-sm text-error mb-2">{error}</p>
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
        <div className="surface-card p-8 text-center">
          <p className="text-sm text-fg-primary">No intelligence items yet.</p>
          <p className="text-xs text-fg-tertiary mt-1">Click &quot;Refresh now&quot; to fetch the latest articles and content from your configured sources.</p>
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

      <div className="pt-4">
        <div className="mb-2">
          <h2 className="text-xl font-semibold">Weekly publishing queue</h2>
          <p className="text-sm text-fg-secondary">Ranked by score, recency, and strategic fit</p>
        </div>

        {planningError && (
          <div className="surface-card border-error/40 bg-error/10 p-4">
            <p className="text-sm text-error mb-2">{planningError}</p>
            <Button size="sm" onClick={loadPlanningQueue} variant="secondary">Retry queue</Button>
          </div>
        )}

        {!planningError && planningQueue.length === 0 && (
          <div className="surface-card p-6 text-center">
            <p className="text-sm text-fg-primary">No ranked planning items yet.</p>
            <p className="text-xs text-fg-tertiary mt-1">Run refresh and add keyword/insight signals to generate the weekly queue.</p>
          </div>
        )}

        {!planningError && planningQueue.length > 0 && (
          <div className="space-y-2">
            {planningQueue.map((queueItem, index) => (
              <div key={queueItem.item_id} className="border rounded-card p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs text-fg-secondary">#{index + 1} · rank {queueItem.rank_score.toFixed(2)}</p>
                    <a href={queueItem.source_url} target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:underline">
                      {queueItem.title}
                    </a>
                    <p className="text-xs text-fg-secondary mt-1">
                      {queueItem.linkage.suggested_content_type} · {queueItem.linkage.suggested_playbook} · {queueItem.linkage.suggested_lifecycle_state} · {queueItem.linkage.owner_placeholder}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      score {queueItem.score_signal.toFixed(1)} · recency {queueItem.recency_signal.toFixed(1)} · strategic fit {queueItem.strategic_fit_signal.toFixed(1)}
                    </p>
                  </div>
                  <span className="inline-block border rounded px-2 py-1 text-xs">{queueItem.source}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="pt-4 space-y-3">
        <div>
          <h2 className="text-xl font-semibold">Conversion feedback loop</h2>
          <p className="text-sm text-fg-secondary">Track taxonomy, outcomes, and CTA tests by deliverable.</p>
        </div>
        <div className="flex gap-2">
          <input
            className="border rounded px-2 py-1 text-sm w-56"
            value={deliverableIdInput}
            onChange={(e) => setDeliverableIdInput(e.target.value)}
            placeholder="Deliverable ID"
          />
          <Button size="sm" onClick={handleLoadConversionLoop} loading={loadingConversion}>Load</Button>
        </div>
        {conversionError && <p className="text-sm text-red-700">{conversionError}</p>}

        {conversionLoop && (
          <div className="space-y-3">
            <p className="text-xs text-fg-secondary">
              Deliverable {conversionLoop.deliverable_id} · {conversionLoop.content_type}
            </p>

            <div className="border rounded-card p-3 space-y-2">
              <p className="text-sm font-medium">Taxonomy definitions</p>
              <div className="grid gap-2 md:grid-cols-5">
                <input className="border rounded px-2 py-1 text-xs" placeholder="event_key" value={taxonomyForm.event_key} onChange={(e) => setTaxonomyForm((prev) => ({ ...prev, event_key: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="funnel_stage" value={taxonomyForm.funnel_stage} onChange={(e) => setTaxonomyForm((prev) => ({ ...prev, funnel_stage: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="definition" value={taxonomyForm.definition} onChange={(e) => setTaxonomyForm((prev) => ({ ...prev, definition: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="primary_cta" value={taxonomyForm.primary_cta} onChange={(e) => setTaxonomyForm((prev) => ({ ...prev, primary_cta: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="success_metric" value={taxonomyForm.success_metric} onChange={(e) => setTaxonomyForm((prev) => ({ ...prev, success_metric: e.target.value }))} />
              </div>
              <Button size="sm" onClick={() => void saveTaxonomyDefinition().catch(() => setConversionError('Failed to save taxonomy definition.'))}>Add taxonomy</Button>
              <div className="space-y-1">
                {conversionLoop.taxonomy_definitions.map((item) => (
                  <p key={item.id} className="text-xs text-fg-secondary">{item.event_key} · {item.funnel_stage} · {item.definition}</p>
                ))}
              </div>
            </div>

            <div className="border rounded-card p-3 space-y-2">
              <p className="text-sm font-medium">Conversion outcomes</p>
              <div className="grid gap-2 md:grid-cols-6">
                <input className="border rounded px-2 py-1 text-xs" placeholder="period_label" value={outcomeForm.period_label} onChange={(e) => setOutcomeForm((prev) => ({ ...prev, period_label: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="visitors" value={outcomeForm.visitors} onChange={(e) => setOutcomeForm((prev) => ({ ...prev, visitors: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="conversions" value={outcomeForm.conversions} onChange={(e) => setOutcomeForm((prev) => ({ ...prev, conversions: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="rate(0-1)" value={outcomeForm.conversion_rate} onChange={(e) => setOutcomeForm((prev) => ({ ...prev, conversion_rate: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="observed_outcome" value={outcomeForm.observed_outcome} onChange={(e) => setOutcomeForm((prev) => ({ ...prev, observed_outcome: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="notes" value={outcomeForm.notes} onChange={(e) => setOutcomeForm((prev) => ({ ...prev, notes: e.target.value }))} />
              </div>
              <Button size="sm" onClick={() => void saveConversionOutcome().catch(() => setConversionError('Failed to save conversion outcome.'))}>Add outcome</Button>
              <div className="space-y-1">
                {conversionLoop.conversion_outcomes.map((item) => (
                  <p key={item.id} className="text-xs text-fg-secondary">{item.period_label} · rate {item.conversion_rate ?? 'n/a'} · {item.observed_outcome ?? 'No notes'}</p>
                ))}
              </div>
            </div>

            <div className="border rounded-card p-3 space-y-2">
              <p className="text-sm font-medium">CTA experiments</p>
              <div className="grid gap-2 md:grid-cols-5">
                <input className="border rounded px-2 py-1 text-xs" placeholder="experiment_key" value={ctaForm.experiment_key} onChange={(e) => setCtaForm((prev) => ({ ...prev, experiment_key: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="variant_label" value={ctaForm.variant_label} onChange={(e) => setCtaForm((prev) => ({ ...prev, variant_label: e.target.value }))} />
                <select className="border rounded px-2 py-1 text-xs" value={ctaForm.status} onChange={(e) => setCtaForm((prev) => ({ ...prev, status: e.target.value }))}>
                  <option value="active">active</option>
                  <option value="paused">paused</option>
                  <option value="completed">completed</option>
                </select>
                <input className="border rounded px-2 py-1 text-xs" placeholder="rate(0-1)" value={ctaForm.conversion_rate} onChange={(e) => setCtaForm((prev) => ({ ...prev, conversion_rate: e.target.value }))} />
                <input className="border rounded px-2 py-1 text-xs" placeholder="observed_outcome" value={ctaForm.observed_outcome} onChange={(e) => setCtaForm((prev) => ({ ...prev, observed_outcome: e.target.value }))} />
              </div>
              <Button size="sm" onClick={() => void saveCtaExperiment().catch(() => setConversionError('Failed to save CTA experiment.'))}>Add CTA experiment</Button>
              <div className="space-y-1">
                {conversionLoop.cta_experiments.map((item) => (
                  <p key={item.id} className="text-xs text-fg-secondary">{item.experiment_key} · {item.variant_label} · {item.status} · rate {item.conversion_rate ?? 'n/a'}</p>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
    </ErrorBoundary>
  );
}
