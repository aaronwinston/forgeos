'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import type { CalendarEvent, ContentType, Folder } from '@/lib/api';
import { createCalendarEvent, isApiError, getProjects, getProjectFolders } from '@/lib/api';
import type { Project } from '@/lib/api';
import { CONTENT_TYPES, CONTENT_TYPE_CONFIG } from './contentTypeConfig';

interface Props {
  defaultDate: Date;
  onClose: () => void;
  onCreated: (event: CalendarEvent) => void;
}

function toLocalDatetimeValue(d: Date) {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/**
 * Modal for creating a new calendar event.
 *
 * Folder resolution (mirrors backend priority):
 *   1. User picks project → modal loads that project's folders
 *   2. User picks a folder → folder_id sent to API
 *   3. No folders exist → project_id sent, backend auto-creates "Content" folder
 *   4. No project selected → event-only, no deliverable
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
  const [folders, setFolders] = useState<Folder[]>([]);
  const [foldersLoading, setFoldersLoading] = useState(false);
  const [selectedFolderId, setSelectedFolderId] = useState<number | ''>('');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load projects on mount
  useEffect(() => {
    getProjects().then(setProjects).catch(() => {});
  }, []);

  // Load folders whenever project changes
  useEffect(() => {
    setSelectedFolderId('');
    setFolders([]);
    if (!selectedProjectId) return;

    setFoldersLoading(true);
    getProjectFolders(Number(selectedProjectId))
      .then(setFolders)
      .catch(() => setFolders([]))
      .finally(() => setFoldersLoading(false));
  }, [selectedProjectId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) { setError('Title is required'); return; }

    setSubmitting(true);
    setError(null);

    const result = await createCalendarEvent({
      title: title.trim(),
      content_type: contentType,
      start_at: new Date(startAt).toISOString(),
      all_day: allDay,
      notes: notes.trim() || undefined,
      // Send folder_id if the user picked one; otherwise send project_id so the
      // backend can auto-create/find the default "Content" folder atomically.
      folder_id: selectedFolderId ? Number(selectedFolderId) : undefined,
      project_id: !selectedFolderId && selectedProjectId ? Number(selectedProjectId) : undefined,
    });

    setSubmitting(false);

    if (isApiError(result)) {
      setError('Failed to create event. Is the API running?');
      return;
    }

    onCreated(result);

    if (result.deliverable?.id) {
      router.push(`/workspace/${result.deliverable.id}`);
    }
  };

  const willCreateDeliverable = Boolean(selectedProjectId);
  const folderHint = (() => {
    if (!selectedProjectId) return null;
    if (foldersLoading) return 'Loading folders…';
    if (folders.length === 0) return 'No folders yet — a "Content" folder will be created automatically.';
    if (!selectedFolderId) return 'Select a folder, or leave blank to use the first available.';
    return null;
  })();

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

          {/* Project selector */}
          <div>
            <label className="block text-xs font-medium text-fg-secondary mb-1">
              Project <span className="text-fg-tertiary font-normal">(optional — creates workspace deliverable)</span>
            </label>
            <select
              value={selectedProjectId}
              onChange={e => setSelectedProjectId(e.target.value === '' ? '' : Number(e.target.value))}
              className="w-full px-3 py-2 text-sm rounded-input border border-border bg-bg-secondary text-fg-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              <option value="">No project — calendar event only</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          {/* Folder selector — shown only when a project is selected and has folders */}
          {selectedProjectId !== '' && (
            <div>
              <label className="block text-xs font-medium text-fg-secondary mb-1">
                Folder <span className="text-fg-tertiary font-normal">(optional)</span>
              </label>
              {foldersLoading ? (
                <div className="h-9 rounded-input border border-border bg-bg-secondary animate-shimmer" />
              ) : folders.length > 0 ? (
                <select
                  value={selectedFolderId}
                  onChange={e => setSelectedFolderId(e.target.value === '' ? '' : Number(e.target.value))}
                  className="w-full px-3 py-2 text-sm rounded-input border border-border bg-bg-secondary text-fg-primary focus:outline-none focus:ring-1 focus:ring-accent"
                >
                  <option value="">Auto-select first folder</option>
                  {folders.map(f => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              ) : null}
              {folderHint && (
                <p className="text-[11px] text-fg-tertiary mt-1">{folderHint}</p>
              )}
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-xs font-medium text-fg-secondary mb-1">
              Notes <span className="text-fg-tertiary font-normal">(optional)</span>
            </label>
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
            type="button"
            onClick={handleSubmit}
            disabled={submitting}
            className="px-4 py-2 text-sm rounded-input bg-accent text-white font-medium hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? 'Creating…' : willCreateDeliverable ? 'Create & open workspace →' : 'Create event'}
          </button>
        </div>
      </div>
    </div>
  );
}
