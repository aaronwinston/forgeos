'use client';
import { useRouter } from 'next/navigation';
import type { CalendarEvent } from '@/lib/api';
import { CONTENT_TYPE_CONFIG } from './contentTypeConfig';
import { SyncStatusBadge } from './SyncStatusBadge';

interface Props {
  event: CalendarEvent;
  /** When true, the pill is being dragged */
  dragging?: boolean;
  onDragStart?: (e: React.DragEvent, event: CalendarEvent) => void;
}

/**
 * A coloured pill representing a calendar event.
 * - Draggable for month-view reschedule.
 * - Click navigates to /workspace/[deliverable_id] when linked.
 */
export function EventPill({ event, dragging, onDragStart }: Props) {
  const router = useRouter();
  const config = CONTENT_TYPE_CONFIG[event.content_type] ?? CONTENT_TYPE_CONFIG['blog'];

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // don't trigger date-cell click (new event modal)
    if (event.deliverable_id) {
      router.push(`/workspace/${event.deliverable_id}`);
    }
  };

  const formattedTime = event.all_day
    ? null
    : new Date(event.start_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart?.(e, event)}
      onClick={handleClick}
      title={`${event.title}${event.deliverable_id ? ' — click to open workspace' : ''}`}
      className={`
        flex items-center gap-1 px-1.5 py-0.5 rounded text-xs border cursor-grab select-none
        transition-opacity duration-150
        ${config.pillClass}
        ${dragging ? 'opacity-40' : 'opacity-100 hover:brightness-95'}
        ${event.deliverable_id ? 'cursor-pointer' : ''}
        ${event.status === 'cancelled' ? 'line-through opacity-60' : ''}
      `}
    >
      {formattedTime && <span className="font-medium shrink-0">{formattedTime}</span>}
      <span className="truncate font-medium">{event.title}</span>
      <SyncStatusBadge status={event.sync_status} className="shrink-0 ml-auto text-[10px]" />
    </div>
  );
}
