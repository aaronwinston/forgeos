import Link from 'next/link';
import type { Session } from '@/lib/api';
import { StatusBadge } from '@/components/ui/StatusBadge';

export function SessionCard({ session }: { session: Session }) {
  return (
    <Link
      href={`/sessions/${session.id}`}
      className="block border border-border rounded-xl p-4 bg-bg-secondary hover:border-brand-purple/30 hover:shadow-sm transition-all group"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="text-sm font-semibold text-fg-primary group-hover:text-brand-purple transition-colors leading-snug">
          {session.title}
        </h3>
        <StatusBadge status={session.status} />
      </div>
      <div className="flex items-center gap-3 text-xs text-fg-tertiary mb-3">
        <span className="capitalize">{session.type}</span>
        {session.audience && <><span>·</span><span>{session.audience}</span></>}
      </div>
      <div className="space-y-2 mb-3">
        {session.brief_id && (
          <div className="text-xs text-fg-tertiary">
            Brief <span className="text-brand-purple">#{session.brief_id}</span>
          </div>
        )}
        {session.deliverable_id && (
          <div className="text-xs text-fg-tertiary">
            Deliverable <span className="text-brand-purple">#{session.deliverable_id}</span>
          </div>
        )}
      </div>
      {session.status !== 'pending' && (
        <div>
          <div className="flex justify-between text-xs text-fg-tertiary mb-1">
            <span>{session.current_agent || 'Idle'}</span>
            <span>{session.progress}%</span>
          </div>
          <div className="h-1 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-purple rounded-full transition-all"
              style={{ width: `${session.progress}%` }}
            />
          </div>
        </div>
      )}
    </Link>
  );
}
