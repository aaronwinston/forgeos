'use client';
import { useState, useEffect } from 'react';
import { getSessions } from '@/lib/api';
import type { Session } from '@/lib/api';
import { SessionCard } from '@/components/sessions/SessionCard';
import { NewSessionModal } from '@/components/dashboard/NewSessionModal';
import { Button } from '@/components/ui/Button';
import { SkeletonCard } from '@/components/ui/SkeletonCard';

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  
  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      console.debug('[Sessions] Loading sessions...');
      const data = await getSessions();
      setSessions(data);
      console.debug('[Sessions] Loaded', data.length, 'sessions');
    } catch (err) {
      const userMessage = 'Unable to load sessions. Check that the API is running and try again.';
      setError(userMessage);
      console.error('[Sessions] Load error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => { load(); }, []);
  
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg-primary">Sessions</h1>
          <p className="text-sm text-fg-secondary mt-1">All your AI content sessions</p>
        </div>
        <Button onClick={() => setShowModal(true)}>+ New session</Button>
      </div>

      {error && (
        <div className="mb-6 border border-red-300 rounded-lg p-4 bg-red-50">
          <p className="text-sm text-red-800 mb-2">{error}</p>
          <Button size="sm" onClick={load} variant="secondary">Retry</Button>
        </div>
      )}
      
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-fg-secondary text-sm mb-4">No sessions yet.</p>
          <Button onClick={() => setShowModal(true)}>Create your first session</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {sessions.map(s => <SessionCard key={s.id} session={s} />)}
        </div>
      )}
      
      {showModal && (
        <NewSessionModal
          onClose={() => setShowModal(false)}
          onCreated={() => { setShowModal(false); load(); }}
        />
      )}
    </div>
  );
}
