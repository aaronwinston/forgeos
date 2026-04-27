import type { SyncStatus } from '@/lib/api';

interface Props {
  status: SyncStatus;
  className?: string;
}

/**
 * Shows the Google Calendar sync state of an event.
 * Rendered inline on EventPill and as a legend in CalendarView header.
 */
export function SyncStatusBadge({ status, className = '' }: Props) {
  if (status === 'synced') {
    return (
      <span title="Synced to Google Calendar" className={`text-green-600 ${className}`}>
        ✓
      </span>
    );
  }
  if (status === 'syncing') {
    return (
      <span title="Syncing…" className={`text-yellow-500 animate-spin inline-block ${className}`}>
        ⟳
      </span>
    );
  }
  // offline
  return (
    <span title="Not synced to Google Calendar" className={`text-gray-400 ${className}`}>
      ⚠
    </span>
  );
}
