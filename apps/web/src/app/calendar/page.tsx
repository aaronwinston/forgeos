import CalendarView from '@/components/calendar/CalendarView';

export const metadata = { title: 'Calendar — ForgeOS' };

/**
 * /calendar — content calendar with month/week/agenda views.
 * CalendarView is 'use client'; this shell stays server-safe.
 */
export default function CalendarPage() {
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <CalendarView />
    </div>
  );
}
