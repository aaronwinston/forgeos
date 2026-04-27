'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import type { CalendarEvent, ContentType } from '@/lib/api';
import { createCalendarEvent, isApiError, getProjects } from '@/lib/api';
import type { Project } from '@/lib/api';
import { CONTENT_TYPES, CONTENT_TYPE_CONFIG } from './contentTypeConfig';

interface Props {
  defaultDate: Date;
  onClose: () => void;
  onCreated: (event: CalendarEvent) => void;
}

function toLocalDatetimeValue(d: Date) {
  // Returns "YYYY-MM-DDThh:mm" for datetime-local input
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/**
 * Modal for creating a new calendar event.
 *
 * Flow:
 *  1. User sets title, content type, date, optional notes
 *  2. Optionally links to a project (triggers folder creation prompt)
 *     — or leaves unlinked (event exists without a deliverable)
 *  3. POST /api/calendar/events
 *     - If folder_id supplied → creates CalendarEvent + Deliverable atomically
 *     - Navigate to /workspace/[deliverableId] on success
 */
export function NewEventModal({ defaultDate, onClose, onCreated }: Props) {
  const router = useRouter();

  const [title, setTitle] = useState('');
  const [contentType, setContentType] = useState<ContentType>('blog');
  const [startAt, setStartAt] = useState(toLocalDatetimeValue(defaultDate));
  const [allDay, setAllDay] = useState(true);
  const [notes, setNotes] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | ''>('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProjects().then(setProjects).catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) { setError('Title is required'); return; }

    setSubmitting(true);
    setError(null);

    const startDate = new Date(startAt);

    const result = await createCalendarEvent({
      title: title.trim(),
      content_type: contentType,
      start_at: startDate.toISOString(),
      all_day: allDay,
      notes: notes.trim() || undefined,
      project_id: selectedProjectId ? Number(selectedProjectId) : undefined,
    });

    setSubmitting(false);

    if (isApiError(result)) {
      setError('Failed to create event. Is the API running?');
      return;
    }

    onCreated(result);

    // Navigate to workspace if a deliverable was created
    if (result.deliverable?.id) {
      router.push(`/workspace/${result.deliverable.id}`);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-bg-primary rounded-card border border-border shadow-xl w-full max-w-md mx-4 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border shrink-0">
          <h2 className="text-base font-semibold text-fg-primary">New calendar event</h2>
          <button onClick={onClose} className="text-fg-tertiary hover:text-fg-primary transition-colors text-lg leading-none">✕</button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 px-6 py-5 overflow-y-auto">
          {/* Title */}
          <div>
            <label className="block text-xs font-medium text-fg-secondary mb-1">Title *</label>
            <input
              autoFocus
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="e.g. Series X funding announcement blog"
              className="w-full px-3 py-2 text-sm rounded-input border border-border bg-bg-secondary text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-1 focus:ring-accent"
            />
          </div>

          {/* Content type */}
          <div>
            <label className="block text-xs font-medium text-fg-secondary mb-1.5">Content type</label>
            <div className="flex flex-wrap gap-2">
              {CONTENT_TYPES.map(ct => {
                const cfg = CONTENT_TYPE_CONFIG[ct];
                const selected = contentType === ct;
                return (
                  <button
                    key={ct}
                    type="button"
                    onClick={() => setContentType(ct)}
                    className={`px-2.5 py-1 text-xs rounded border font-medium transition-all ${
                      selected
                        ? `${cfg.pillClass} ring-1 ring-offset-1`
                        : 'border-border text-fg-tertiary hover:border-accent/40'
                    }`}
                  >
                    {cfg.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Date/time */}
          <div>
            <label className="block text-xs font-medium text-fg-secondary mb-1">Date & time</label>
            <input
              type="datetime-local"
              value={startAt}
              onChange={e => setStartAt(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-input border border-border bg-bg-secondary text-fg-primary focus:outline-none focus:ring-1 focus:ring-accent"
            />
            <label className="flex items-center gap-2 mt-2 cursor-pointer">
              <input
                type="checkbox"
                checked={allDay}
                onChange={e => setAllDay(e.target.checked)}
                className="rounded border-border accent-accent"
              />
              <span className="text-xs text-fg-secondary">All-day event</span>
            </label>
          </div>

          {/* Project link (optional) */}
          <div>
            <label className="block text-xs font-medium text-fg-secondary mb-1">
              Link to project <span className="text-fg-tertiary font-normal">(optional — creates deliverable)</span>
            </label>
            <select
              value={selectedProjectId}
              onChange={e => setSelectedProjectId(e.target.value === '' ? '' : Number(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-input border border-border bg-bg-secondary text-fg-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              <option value="">No project — event only</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            {selectedProjectId && (
              <p className="text-[11px] text-fg-tertiary mt-1">
                A draft deliverable will be created in this project.
              </p>
            )}
          </div>

          {/* Notes */}
          <div>
            <label className="block text-xs font-medium text-fg-secondary mb-1">Notes <span className="text-fg-tertiary font-normal">(optional)</span></label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              rows={2}
              placeholder="Brief, angle, key messages…"
              className="w-full px-3 py-2 text-sm rounded-input border border-border bg-bg-secondary text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-1 focus:ring-accent resize-none"
            />
          </div>

          {/* Error */}
          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-input px-3 py-2">{error}</p>
          )}
        </form>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm rounded-input border border-border text-fg-secondary hover:text-fg-primary hover:bg-bg-secondary transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="new-event-form"
            onClick={handleSubmit}
            disabled={submitting}
            className="px-4 py-2 text-sm rounded-input bg-accent text-white font-medium hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? 'Creating…' : selectedProjectId ? 'Create & open workspace →' : 'Create event'}
          </button>
        </div>
      </div>
    </div>
  );
}
