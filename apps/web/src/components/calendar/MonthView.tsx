'use client';
import { useMemo, useState } from 'react';
import type { CalendarEvent } from '@/lib/api';
import { EventPill } from './EventPill';

interface Props {
  year: number;
  month: number; // 0-indexed
  events: CalendarEvent[];
  onDateClick: (date: Date) => void;
  onEventDrop: (eventId: number, newDate: Date) => void;
  /** Optimistically-moved event ids mapped to their pending new date string */
  pendingMoves: Record<number, string>;
}

function isSameDay(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();
}

function isToday(d: Date) {
  return isSameDay(d, new Date());
}

/**
 * Month grid calendar view.
 *
 * Drag-to-reschedule is implemented via native HTML5 DnD:
 * 1. EventPill sets draggable + onDragStart → stores event id in dataTransfer
 * 2. Date cells accept onDragOver + onDrop → calls onEventDrop with new date
 * 3. Optimistic update is applied immediately via pendingMoves (no waiting for PATCH)
 */
export function MonthView({ year, month, events, onDateClick, onEventDrop, pendingMoves }: Props) {
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [dragOverDate, setDragOverDate] = useState<string | null>(null);

  // Build the 6×7 grid of dates
  const days = useMemo(() => {
    const first = new Date(year, month, 1);
    const last = new Date(year, month + 1, 0);
    const startDow = first.getDay(); // 0=Sun

    const grid: Date[] = [];
    // Pad from previous month
    for (let i = startDow - 1; i >= 0; i--) {
      const d = new Date(year, month, -i);
      grid.push(d);
    }
    // Current month
    for (let d = 1; d <= last.getDate(); d++) {
      grid.push(new Date(year, month, d));
    }
    // Pad to complete last row
    while (grid.length % 7 !== 0) {
      grid.push(new Date(year, month + 1, grid.length - last.getDate() - startDow + 1));
    }
    return grid;
  }, [year, month]);

  // Map date string → events for fast lookup
  const eventsByDate = useMemo(() => {
    const map: Record<string, CalendarEvent[]> = {};
    for (const ev of events) {
      // Apply optimistic move
      const dateStr = pendingMoves[ev.id]
        ? pendingMoves[ev.id].slice(0, 10)
        : ev.start_at.slice(0, 10);
      if (!map[dateStr]) map[dateStr] = [];
      map[dateStr].push(ev);
    }
    return map;
  }, [events, pendingMoves]);

  const handleDragStart = (e: React.DragEvent, event: CalendarEvent) => {
    e.dataTransfer.setData('eventId', String(event.id));
    e.dataTransfer.effectAllowed = 'move';
    setDraggingId(event.id);
  };

  const handleDragOver = (e: React.DragEvent, dateStr: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverDate(dateStr);
  };

  const handleDrop = (e: React.DragEvent, date: Date) => {
    e.preventDefault();
    const idStr = e.dataTransfer.getData('eventId');
    if (!idStr) return;
    const id = parseInt(idStr, 10);
    setDraggingId(null);
    setDragOverDate(null);
    onEventDrop(id, date);
  };

  const DOW_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="flex flex-col h-full select-none">
      {/* Day-of-week header */}
      <div className="grid grid-cols-7 border-b border-border">
        {DOW_LABELS.map(d => (
          <div key={d} className="py-2 text-center text-xs font-semibold text-fg-tertiary uppercase tracking-wider">
            {d}
          </div>
        ))}
      </div>

      {/* Date grid */}
      <div className="grid grid-cols-7 flex-1" style={{ gridTemplateRows: `repeat(${days.length / 7}, minmax(0, 1fr))` }}>
        {days.map((date, idx) => {
          const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
          const inMonth = date.getMonth() === month;
          const today = isToday(date);
          const isOver = dragOverDate === dateStr;
          const cellEvents = eventsByDate[dateStr] ?? [];

          return (
            <div
              key={idx}
              onClick={() => inMonth && onDateClick(date)}
              onDragOver={(e) => handleDragOver(e, dateStr)}
              onDragLeave={() => setDragOverDate(null)}
              onDrop={(e) => handleDrop(e, date)}
              className={`
                border-r border-b border-border p-1 flex flex-col gap-0.5 min-h-[80px] overflow-hidden
                transition-colors duration-100
                ${inMonth ? 'bg-bg-primary cursor-pointer hover:bg-bg-secondary' : 'bg-bg-secondary/40 cursor-default'}
                ${isOver ? 'bg-accent/10 outline outline-1 outline-accent' : ''}
              `}
            >
              {/* Date number */}
              <span className={`
                text-xs font-medium w-6 h-6 flex items-center justify-center rounded-full shrink-0
                ${today ? 'bg-accent text-white font-bold' : inMonth ? 'text-fg-primary' : 'text-fg-tertiary'}
              `}>
                {date.getDate()}
              </span>

              {/* Events — show up to 3, then "+N more" */}
              <div className="flex flex-col gap-0.5 overflow-hidden">
                {cellEvents.slice(0, 3).map(ev => (
                  <EventPill
                    key={ev.id}
                    event={ev}
                    dragging={draggingId === ev.id}
                    onDragStart={handleDragStart}
                  />
                ))}
                {cellEvents.length > 3 && (
                  <span className="text-[10px] text-fg-tertiary pl-1">
                    +{cellEvents.length - 3} more
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
