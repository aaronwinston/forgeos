'use client';
import { useState, useEffect, useCallback } from 'react';
import type { CalendarEvent, CalendarEventPatchPayload } from '@/lib/api';
import { getCalendarEvents, updateCalendarEvent, isApiError } from '@/lib/api';
import { MonthView } from './MonthView';
import { WeekView } from './WeekView';
import { AgendaView } from './AgendaView';
import { NewEventModal } from './NewEventModal';

type ViewMode = 'month' | 'week' | 'agenda';

const MONTH_NAMES = ['January','February','March','April','May','June',
                     'July','August','September','October','November','December'];

function addMonths(d: Date, n: number) {
  return new Date(d.getFullYear(), d.getMonth() + n, 1);
}

function addWeeks(d: Date, n: number) {
  const r = new Date(d);
  r.setDate(r.getDate() + n * 7);
  return r;
}

/**
 * Top-level calendar shell.
 *
 * Owns:
 *  - view mode toggle (Month / Week / Agenda)
 *  - date navigation (prev/next/today)
 *  - event list state (fetched from API, refreshed on nav)
 *  - optimistic drag-reschedule: update local state immediately, fire PATCH async
 *  - NewEventModal open/close
 */
export default function CalendarView() {
  const [viewMode, setViewMode] = useState<ViewMode>('month');
  const [cursor, setCursor] = useState(new Date()); // drives which period is shown
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // eventId → ISO string of pending new date (optimistic DnD)
  const [pendingMoves, setPendingMoves] = useState<Record<number, string>>({});
  // Date pre-filled in NewEventModal
  const [newEventDate, setNewEventDate] = useState<Date | null>(null);

  // ── Fetch events ──────────────────────────────────────────────────────────

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    setError(null);

    let start: Date, end: Date;
    if (viewMode === 'month') {
      start = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
      end   = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0, 23, 59, 59);
    } else if (viewMode === 'week') {
      // Week containing cursor
      const sunday = new Date(cursor);
      sunday.setDate(cursor.getDate() - cursor.getDay());
      start = sunday;
      end = new Date(sunday);
      end.setDate(end.getDate() + 6);
      end.setHours(23, 59, 59);
    } else {
      // Agenda: next 60 days from today
      start = new Date();
      end = new Date();
      end.setDate(end.getDate() + 60);
    }

    const result = await getCalendarEvents(start.toISOString(), end.toISOString());
    if (!Array.isArray(result)) {
      setError('Could not load calendar events. Is the API running?');
    } else {
      setEvents(result);
    }
    setLoading(false);
  }, [viewMode, cursor]);

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  // ── Navigation ────────────────────────────────────────────────────────────

  const goToToday = () => setCursor(new Date());

  const goPrev = () => {
    if (viewMode === 'month') setCursor(c => addMonths(c, -1));
    else setCursor(c => addWeeks(c, -1));
  };

  const goNext = () => {
    if (viewMode === 'month') setCursor(c => addMonths(c, 1));
    else setCursor(c => addWeeks(c, 1));
  };

  const periodLabel = () => {
    if (viewMode === 'month') return `${MONTH_NAMES[cursor.getMonth()]} ${cursor.getFullYear()}`;
    if (viewMode === 'week') {
      const sunday = new Date(cursor);
      sunday.setDate(cursor.getDate() - cursor.getDay());
      const saturday = new Date(sunday);
      saturday.setDate(saturday.getDate() + 6);
      return `${sunday.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} – ${saturday.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
    return 'Agenda (next 60 days)';
  };

  // ── Drag-to-reschedule ────────────────────────────────────────────────────

  /**
   * Called by MonthView when an event is dropped on a new date cell.
   * 1. Immediately apply optimistic update (pendingMoves)
   * 2. Fire PATCH async — on failure, roll back and show error
   */
  const handleEventDrop = useCallback(async (eventId: number, newDate: Date) => {
    const event = events.find(e => e.id === eventId);
    if (!event) return;

    // Build new ISO string preserving time-of-day
    const oldStart = new Date(event.start_at);
    const newStart = new Date(newDate);
    newStart.setHours(oldStart.getHours(), oldStart.getMinutes(), oldStart.getSeconds());

    const newStartISO = newStart.toISOString();

    // 1. Optimistic update
    setPendingMoves(pm => ({ ...pm, [eventId]: newStartISO }));

    // 2. PATCH
    const patch: CalendarEventPatchPayload = { start_at: newStartISO, sync_status: 'syncing' };
    if (event.end_at) {
      const diff = new Date(event.end_at).getTime() - new Date(event.start_at).getTime();
      patch.end_at = new Date(newStart.getTime() + diff).toISOString();
    }

    const result = await updateCalendarEvent(eventId, patch);
    if (isApiError(result)) {
      // Roll back
      setPendingMoves(pm => { const next = { ...pm }; delete next[eventId]; return next; });
      setError('Failed to reschedule event — changes rolled back.');
    } else {
      // Commit: update events list and clear pending
      setEvents(evs => evs.map(e => e.id === eventId ? result : e));
      setPendingMoves(pm => { const next = { ...pm }; delete next[eventId]; return next; });
    }
  }, [events]);

  // ── New event modal ───────────────────────────────────────────────────────

  const handleDateClick = (date: Date) => setNewEventDate(date);

  const handleEventCreated = (newEvent: CalendarEvent) => {
    setEvents(evs => [...evs, newEvent].sort((a, b) => a.start_at.localeCompare(b.start_at)));
    setNewEventDate(null);
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full bg-bg-primary">
      {/* ── Toolbar ── */}
      <div className="flex items-center justify-between gap-4 px-6 py-3 border-b border-border bg-bg-secondary shrink-0">
        {/* Left: nav */}
        <div className="flex items-center gap-2">
          <button
            onClick={goToToday}
            className="px-3 py-1.5 text-sm rounded-input border border-border bg-bg-primary text-fg-primary hover:bg-bg-tertiary transition-colors"
          >
            Today
          </button>
          <button onClick={goPrev} className="p-1.5 rounded-input border border-border hover:bg-bg-tertiary transition-colors" title="Previous">
            ‹
          </button>
          <button onClick={goNext} className="p-1.5 rounded-input border border-border hover:bg-bg-tertiary transition-colors" title="Next">
            ›
          </button>
          <h2 className="text-base font-semibold text-fg-primary ml-2">{periodLabel()}</h2>
        </div>

        {/* Center: sync legend */}
        <div className="hidden md:flex items-center gap-4 text-xs text-fg-tertiary">
          <span><span className="text-green-600 font-bold">✓</span> Synced</span>
          <span><span className="text-yellow-500">⟳</span> Syncing</span>
          <span><span className="text-gray-400">⚠</span> Offline</span>
        </div>

        {/* Right: view toggle + new event */}
        <div className="flex items-center gap-2">
          <div className="flex rounded-input border border-border overflow-hidden">
            {(['month', 'week', 'agenda'] as ViewMode[]).map(v => (
              <button
                key={v}
                onClick={() => setViewMode(v)}
                className={`px-3 py-1.5 text-sm capitalize transition-colors ${
                  viewMode === v
                    ? 'bg-accent text-white font-medium'
                    : 'bg-bg-primary text-fg-secondary hover:bg-bg-tertiary'
                }`}
              >
                {v}
              </button>
            ))}
          </div>
          <button
            onClick={() => setNewEventDate(new Date())}
            className="px-3 py-1.5 text-sm rounded-input bg-accent text-white font-medium hover:bg-accent/90 transition-colors"
          >
            + New event
          </button>
        </div>
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div className="mx-6 mt-3 p-3 rounded-card bg-red-50 border border-red-200 text-sm text-red-700 flex items-center justify-between">
          {error}
          <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700 ml-4">✕</button>
        </div>
      )}

      {/* ── Loading skeleton ── */}
      {loading && (
        <div className="flex-1 flex items-center justify-center text-fg-tertiary">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            <p className="text-sm">Loading events…</p>
          </div>
        </div>
      )}

      {/* ── Calendar body ── */}
      {!loading && (
        <div className="flex-1 overflow-hidden">
          {viewMode === 'month' && (
            <MonthView
              year={cursor.getFullYear()}
              month={cursor.getMonth()}
              events={events}
              onDateClick={handleDateClick}
              onEventDrop={handleEventDrop}
              pendingMoves={pendingMoves}
            />
          )}
          {viewMode === 'week' && (
            <WeekView
              weekStart={cursor}
              events={events}
              onDateClick={handleDateClick}
            />
          )}
          {viewMode === 'agenda' && (
            <AgendaView events={events} />
          )}
        </div>
      )}

      {/* ── New event modal ── */}
      {newEventDate && (
        <NewEventModal
          defaultDate={newEventDate}
          onClose={() => setNewEventDate(null)}
          onCreated={handleEventCreated}
        />
      )}
    </div>
  );
}
