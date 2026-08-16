'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type { ProjectTracking, SuggestedTopic, WorkTrackingItem } from '@/lib/api';

interface NewProjectPayload {
  name: string;
  description?: string;
  tracking: ProjectTracking;
}

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (payload: NewProjectPayload) => Promise<void>;
}

const TOPIC_TYPES: SuggestedTopic['type'][] = [
  'seo_article',
  'aeo_article',
  'launch_blog',
  'developer_comms',
  'landing_page',
  'case_study',
  'other',
];

const WORK_CATEGORIES: WorkTrackingItem['category'][] = [
  'seo_article',
  'aeo_article',
  'launch_blog',
  'developer_comms',
  'web_page',
  'case_study',
  'campaign',
  'other',
];

function formatLabel(value: string): string {
  return value
    .split('_')
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(' ');
}

function TagInput({
  label,
  placeholder,
  values,
  onChange,
}: {
  label: string;
  placeholder: string;
  values: string[];
  onChange: (values: string[]) => void;
}) {
  const [input, setInput] = useState('');

  const addTag = () => {
    const value = input.trim();
    if (!value) return;
    if (!values.includes(value)) {
      onChange([...values, value]);
    }
    setInput('');
  };

  return (
    <div className="space-y-2">
      <label className="block text-xs font-semibold uppercase tracking-wide text-fg-tertiary">{label}</label>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              addTag();
            }
          }}
          placeholder={placeholder}
          className="flex-1 px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary placeholder:text-fg-tertiary"
        />
        <button
          type="button"
          onClick={addTag}
          className="px-3 py-2 rounded-lg border border-border bg-bg-tertiary text-sm text-fg-primary hover:bg-bg-secondary"
        >
          Add
        </button>
      </div>
      {values.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {values.map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => onChange(values.filter((v) => v !== value))}
              className="text-xs px-2 py-1 rounded-md border border-border bg-bg-tertiary text-fg-secondary hover:text-fg-primary"
            >
              {value} ×
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function NewProjectModal({ isOpen, onClose, onCreate }: NewProjectModalProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [sites, setSites] = useState<string[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [competitors, setCompetitors] = useState<string[]>([]);
  const [seoFocus, setSeoFocus] = useState<string[]>([]);
  const [aeoQuestions, setAeoQuestions] = useState<string[]>([]);
  const [suggestedTopics, setSuggestedTopics] = useState<SuggestedTopic[]>([]);
  const [workItems, setWorkItems] = useState<WorkTrackingItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setName('');
    setDescription('');
    setSites([]);
    setKeywords([]);
    setCompetitors([]);
    setSeoFocus([]);
    setAeoQuestions([]);
    setSuggestedTopics([]);
    setWorkItems([]);
    setError(null);
  }, [isOpen]);

  const canCreate = useMemo(() => name.trim().length > 0 && !loading, [name, loading]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="surface-elevated w-full max-w-5xl max-h-[92vh] overflow-hidden flex flex-col">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-lg font-semibold text-fg-primary">Start a new project</h2>
          <p className="text-sm text-fg-secondary mt-1">
            Define your website and content strategy scope so ForgeOS can plan and track execution.
          </p>
        </div>

        <form
          ref={formRef}
          className="overflow-y-auto px-5 py-4 space-y-6"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!name.trim()) {
              setError('Project name is required.');
              return;
            }
            setLoading(true);
            setError(null);
            try {
              await onCreate({
                name: name.trim(),
                description: description.trim() || undefined,
                tracking: {
                  sites,
                  keywords,
                  competitors,
                  seo_focus: seoFocus,
                  aeo_questions: aeoQuestions,
                  suggested_topics: suggestedTopics.filter((topic) => topic.title.trim().length > 0),
                  work_items: workItems.filter((item) => item.title.trim().length > 0),
                },
              });
              onClose();
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Failed to create project');
            } finally {
              setLoading(false);
            }
          }}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-fg-tertiary mb-2">Project name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Arize.com Growth Engine"
                className="w-full px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary placeholder:text-fg-tertiary"
                autoFocus
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-fg-tertiary mb-2">Description</label>
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What this project is responsible for"
                className="w-full px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary placeholder:text-fg-tertiary"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <TagInput label="Tracked sites" placeholder="https://arize.com" values={sites} onChange={setSites} />
            <TagInput label="Keyword set" placeholder="agent observability" values={keywords} onChange={setKeywords} />
            <TagInput label="Competitor set" placeholder="langfuse.com" values={competitors} onChange={setCompetitors} />
            <TagInput label="SEO focus" placeholder="comparison pages" values={seoFocus} onChange={setSeoFocus} />
          </div>

          <TagInput
            label="AEO question set"
            placeholder="How do I evaluate agent quality in production?"
            values={aeoQuestions}
            onChange={setAeoQuestions}
          />

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-fg-primary">Suggested topics</h3>
              <button
                type="button"
                onClick={() =>
                  setSuggestedTopics((prev) => [
                    ...prev,
                    { title: '', type: 'seo_article', priority: 'medium', status: 'idea' },
                  ])
                }
                className="px-3 py-1.5 text-xs rounded-md border border-border bg-bg-tertiary text-fg-primary hover:bg-bg-secondary"
              >
                + Add topic
              </button>
            </div>
            <div className="space-y-2">
              {suggestedTopics.map((topic, index) => (
                <div key={`topic-${index}`} className="grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_170px_110px_130px_auto] gap-2">
                  <input
                    value={topic.title}
                    onChange={(e) => {
                      const next = [...suggestedTopics];
                      next[index] = { ...topic, title: e.target.value };
                      setSuggestedTopics(next);
                    }}
                    placeholder="Topic title"
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  />
                  <select
                    value={topic.type}
                    onChange={(e) => {
                      const next = [...suggestedTopics];
                      next[index] = { ...topic, type: e.target.value as SuggestedTopic['type'] };
                      setSuggestedTopics(next);
                    }}
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  >
                    {TOPIC_TYPES.map((value) => (
                      <option key={value} value={value}>{formatLabel(value)}</option>
                    ))}
                  </select>
                  <select
                    value={topic.priority}
                    onChange={(e) => {
                      const next = [...suggestedTopics];
                      next[index] = { ...topic, priority: e.target.value as SuggestedTopic['priority'] };
                      setSuggestedTopics(next);
                    }}
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  >
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                  <select
                    value={topic.status}
                    onChange={(e) => {
                      const next = [...suggestedTopics];
                      next[index] = { ...topic, status: e.target.value as SuggestedTopic['status'] };
                      setSuggestedTopics(next);
                    }}
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  >
                    <option value="idea">Idea</option>
                    <option value="planned">Planned</option>
                    <option value="in_progress">In progress</option>
                    <option value="published">Published</option>
                  </select>
                  <button
                    type="button"
                    onClick={() => setSuggestedTopics((prev) => prev.filter((_, i) => i !== index))}
                    className="px-2 py-2 text-sm rounded-md border border-border text-fg-tertiary hover:text-fg-primary"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </section>

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-fg-primary">Work tracking</h3>
              <button
                type="button"
                onClick={() =>
                  setWorkItems((prev) => [
                    ...prev,
                    { title: '', category: 'seo_article', status: 'backlog', owner: '', due_date: '' },
                  ])
                }
                className="px-3 py-1.5 text-xs rounded-md border border-border bg-bg-tertiary text-fg-primary hover:bg-bg-secondary"
              >
                + Add item
              </button>
            </div>
            <div className="space-y-2">
              {workItems.map((item, index) => (
                <div key={`work-${index}`} className="grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_160px_120px_140px_130px_auto] gap-2">
                  <input
                    value={item.title}
                    onChange={(e) => {
                      const next = [...workItems];
                      next[index] = { ...item, title: e.target.value };
                      setWorkItems(next);
                    }}
                    placeholder="Work item title"
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  />
                  <select
                    value={item.category}
                    onChange={(e) => {
                      const next = [...workItems];
                      next[index] = { ...item, category: e.target.value as WorkTrackingItem['category'] };
                      setWorkItems(next);
                    }}
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  >
                    {WORK_CATEGORIES.map((value) => (
                      <option key={value} value={value}>{formatLabel(value)}</option>
                    ))}
                  </select>
                  <select
                    value={item.status}
                    onChange={(e) => {
                      const next = [...workItems];
                      next[index] = { ...item, status: e.target.value as WorkTrackingItem['status'] };
                      setWorkItems(next);
                    }}
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  >
                    <option value="backlog">Backlog</option>
                    <option value="in_progress">In progress</option>
                    <option value="review">Review</option>
                    <option value="done">Done</option>
                  </select>
                  <input
                    value={item.owner || ''}
                    onChange={(e) => {
                      const next = [...workItems];
                      next[index] = { ...item, owner: e.target.value };
                      setWorkItems(next);
                    }}
                    placeholder="Owner"
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  />
                  <input
                    type="date"
                    value={item.due_date || ''}
                    onChange={(e) => {
                      const next = [...workItems];
                      next[index] = { ...item, due_date: e.target.value };
                      setWorkItems(next);
                    }}
                    className="px-3 py-2 border border-border rounded-lg bg-bg-secondary text-sm text-fg-primary"
                  />
                  <button
                    type="button"
                    onClick={() => setWorkItems((prev) => prev.filter((_, i) => i !== index))}
                    className="px-2 py-2 text-sm rounded-md border border-border text-fg-tertiary hover:text-fg-primary"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </section>

          {error && (
            <div className="text-sm text-error bg-error/10 border border-error/30 rounded-lg px-3 py-2">{error}</div>
          )}
        </form>

        <div className="px-5 py-4 border-t border-border flex items-center justify-end gap-2">
          <button
            type="button"
            className="px-4 py-2 rounded-lg border border-border text-sm text-fg-secondary hover:text-fg-primary"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="button"
            className="px-4 py-2 rounded-lg bg-accent text-white text-sm hover:bg-accent-hover disabled:opacity-50"
            onClick={() => {
              formRef.current?.requestSubmit();
            }}
            disabled={!canCreate}
          >
            {loading ? 'Creating…' : 'Create project'}
          </button>
        </div>
      </div>
    </div>
  );
}
