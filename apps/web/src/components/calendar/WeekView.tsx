'use client';
import { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import type { CalendarEvent } from '@/lib/api';
import { EventPill } from './EventPill';

interface Props {
  /** Any date within the target week */
  weekStart: Date;
  events: CalendarEvent[];
  onDateClick: (date: Date) => void;
}

function addDays(d: Date, n: number) {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}

function isToday(d: Date) {
  const now = new Date();
  return d.toDateString() === now.toDateString();
}

/**
 * Week strip view — 7 columns, one day each, events as stacked pills.
 * No hour-level positioning (keeps it dep-free); all-day semantics.
 */
export function WeekView({ weekStart, events, onDateClick }: Props) {
  // Align weekStart to Sunday
  const sunday = useMemo(() => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() - d.getDay());
    return d;
  }, [weekStart]);

  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => addDays(sunday, i)), [sunday]);

  const eventsByDate = useMemo(() => {
    const map: Record<string, CalendarEvent[]> = {};
    for (const ev of events) {
      const key = ev.start_at.slice(0, 10);
      if (!map[key]) map[key] = [];
      map[key].push(ev);
    }
    return map;
  }, [events]);

  const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const DOW = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

  return (
    <div className="flex flex-col h-full">
      {/* Header row */}
      <div className="grid grid-cols-7 border-b border-border">
        {days.map((d, i) => {
          const today = isToday(d);
          return (
            <div key={i} className="py-3 text-center border-r border-border last:border-r-0">
              <p className="text-xs text-fg-tertiary font-medium uppercase">{DOW[i]}</p>
              <p className={`
                text-xl font-bold mt-0.5 mx-auto w-9 h-9 flex items-center justify-center rounded-full
                ${today ? 'bg-accent text-white' : 'text-fg-primary'}
              `}>
                {d.getDate()}
              </p>
              <p className="text-[10px] text-fg-tertiary mt-0.5">{MONTH_NAMES[d.getMonth()]}</p>
            </div>
          );
        })}
      </div>

      {/* Event rows */}
      <div className="grid grid-cols-7 flex-1 overflow-y-auto">
        {days.map((d, i) => {
          const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
          const dayEvents = eventsByDate[key] ?? [];

          return (
            <div
              key={i}
              onClick={() => onDateClick(d)}
              className="border-r border-border last:border-r-0 p-2 flex flex-col gap-1 cursor-pointer hover:bg-bg-secondary transition-colors min-h-[200px]"
            >
              {dayEvents.map(ev => (
                <EventPill key={ev.id} event={ev} />
              ))}
              {dayEvents.length === 0 && (
                <span className="text-[11px] text-fg-tertiary italic mt-1 px-1">No events</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
