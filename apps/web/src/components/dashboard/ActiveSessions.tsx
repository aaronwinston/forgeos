'use client';
import { useState, useEffect } from 'react';
import { getSessions } from '@/lib/api';
import type { Session } from '@/lib/api';
import { StatusBadge } from '@/components/ui/StatusBadge';
import Link from 'next/link';

export function ActiveSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    getSessions()
      .then(all => setSessions(all.filter(s => s.status === 'active' || s.status === 'pending').slice(0, 5)))
      .finally(() => setLoading(false));
  }, []);
  
  if (loading) {
    return (
      <section>
        <h2 className="text-base font-semibold text-fg-primary mb-3">Active sessions</h2>
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 border border-border rounded-xl bg-bg-secondary animate-pulse" />
          ))}
        </div>
      </section>
    );
  }
  
  if (sessions.length === 0) return null;
  
  return (
    <section>
      <h2 className="text-base font-semibold text-fg-primary mb-3">Active sessions</h2>
      <div className="space-y-2">
        {sessions.map(session => (
          <Link
            key={session.id}
            href={`/sessions/${session.id}`}
            className="flex items-center gap-3 p-3 border border-border rounded-xl bg-bg-secondary hover:border-brand-purple/30 transition-colors group"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-fg-primary truncate group-hover:text-brand-purple transition-colors">
                {session.title}
              </p>
              {session.current_agent && (
                <p className="text-xs text-fg-tertiary mt-0.5">Agent: {session.current_agent}</p>
              )}
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {session.status === 'active' && (
                <div className="text-xs text-fg-tertiary">{session.progress}%</div>
              )}
              <StatusBadge status={session.status} />
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
