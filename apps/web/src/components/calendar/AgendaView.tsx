'use client';
import { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import type { CalendarEvent } from '@/lib/api';
import { CONTENT_TYPE_CONFIG } from './contentTypeConfig';
import { SyncStatusBadge } from './SyncStatusBadge';

interface Props {
  events: CalendarEvent[];
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function dateKey(iso: string) {
  return iso.slice(0, 10);
}

/**
 * Chronological list view grouped by date.
 * Best for scanning upcoming events without visual noise of a grid.
 */
export function AgendaView({ events }: Props) {
  const router = useRouter();

  const grouped = useMemo(() => {
    const map: Record<string, CalendarEvent[]> = {};
    for (const ev of events) {
      const key = dateKey(ev.start_at);
      if (!map[key]) map[key] = [];
      map[key].push(ev);
    }
    // Sort keys chronologically
    return Object.entries(map).sort(([a], [b]) => a.localeCompare(b));
  }, [events]);

  if (grouped.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-fg-tertiary gap-2">
        <span className="text-4xl">📅</span>
        <p className="text-sm">No events in this range</p>
      </div>
    );
  }

  return (
    <div className="overflow-y-auto h-full divide-y divide-border">
      {grouped.map(([dateStr, dayEvents]) => (
        <div key={dateStr} className="flex gap-6 px-6 py-4 hover:bg-bg-secondary transition-colors group">
          {/* Date label */}
          <div className="w-36 shrink-0">
            <p className="text-xs font-semibold text-fg-tertiary uppercase tracking-wider">
              {formatDate(`${dateStr}T00:00:00`).split(',')[0]}
            </p>
            <p className="text-sm font-medium text-fg-primary">
              {formatDate(`${dateStr}T00:00:00`).split(',').slice(1).join(',').trim()}
            </p>
          </div>

          {/* Events for the day */}
          <div className="flex flex-col gap-3 flex-1 min-w-0">
            {dayEvents.map(ev => {
              const config = CONTENT_TYPE_CONFIG[ev.content_type] ?? CONTENT_TYPE_CONFIG['blog'];
              return (
                <div
                  key={ev.id}
                  onClick={() => ev.deliverable_id && router.push(`/workspace/${ev.deliverable_id}`)}
                  className={`
                    flex items-start gap-3 p-3 rounded-card border border-border bg-bg-primary
                    ${ev.deliverable_id ? 'cursor-pointer hover:border-accent/40 hover:shadow-sm' : ''}
                    transition-all duration-150
                    ${ev.status === 'cancelled' ? 'opacity-50' : ''}
                  `}
                >
                  {/* Colour stripe */}
                  <div className="w-1 self-stretch rounded-full shrink-0" style={{ backgroundColor: config.color }} />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className={`text-sm font-medium text-fg-primary truncate ${ev.status === 'cancelled' ? 'line-through' : ''}`}>
                        {ev.title}
                      </p>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium shrink-0 ${config.pillClass}`}>
                        {config.label}
                      </span>
                      <SyncStatusBadge status={ev.sync_status} className="text-xs" />
                    </div>
                    <p className="text-xs text-fg-tertiary mt-0.5">
                      {ev.all_day ? 'All day' : `${formatTime(ev.start_at)}${ev.end_at ? ` – ${formatTime(ev.end_at)}` : ''}`}
                    </p>
                    {ev.notes && <p className="text-xs text-fg-secondary mt-1 line-clamp-2">{ev.notes}</p>}
                  </div>

                  {ev.deliverable_id && (
                    <span className="text-xs text-fg-tertiary shrink-0 group-hover:text-accent transition-colors">→</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
