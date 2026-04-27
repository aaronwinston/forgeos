'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getSessionById, getDeliverableById, isApiError } from '@/lib/api';
import type { Session, Deliverable } from '@/lib/api';
import { AgentChain } from '@/components/sessions/AgentChain';
import { ChatInterface } from '@/components/sessions/ChatInterface';
import { DocumentEditor } from '@/components/sessions/DocumentEditor';
import { StatusBadge } from '@/components/ui/StatusBadge';

export default function SessionPage() {
  const params = useParams();
  const id = Number(params.id);
  const [session, setSession] = useState<Session | null>(null);
  const [deliverable, setDeliverable] = useState<Deliverable | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    getSessionById(id).then(result => {
      if (!isApiError(result)) {
        setSession(result);
        if (result.deliverable_id) {
          getDeliverableById(result.deliverable_id).then(delResult => {
            if (!isApiError(delResult)) {
              setDeliverable(delResult);
            }
          });
        }
      }
      setLoading(false);
    });
  }, [id]);
  
  if (loading) return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="h-8 w-64 bg-bg-tertiary rounded animate-pulse mb-6" />
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 h-96 bg-bg-tertiary rounded-card animate-pulse" />
        <div className="col-span-2 space-y-4">
          <div className="h-80 bg-bg-tertiary rounded-card animate-pulse" />
          <div className="h-64 bg-bg-tertiary rounded-card animate-pulse" />
        </div>
      </div>
    </div>
  );
  
  if (!session) return (
    <div className="p-6 text-center">
      <p className="text-fg-secondary">Session not found.</p>
    </div>
  );
  
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <div>
          <h1 className="text-xl font-semibold text-fg-primary">{session.title}</h1>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-fg-tertiary capitalize">{session.type}</span>
            {session.audience && <><span className="text-fg-tertiary">·</span><span className="text-xs text-fg-tertiary">{session.audience}</span></>}
          </div>
          {session.brief_id && <div className="text-xs text-fg-tertiary mt-2">Brief ID: {session.brief_id}</div>}
          {session.deliverable_id && <div className="text-xs text-fg-tertiary">Deliverable ID: {session.deliverable_id}</div>}
        </div>
        <StatusBadge status={session.status} />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <AgentChain session={session} onUpdate={setSession} />
          <ChatInterface sessionId={id} />
        </div>
        <div className="lg:col-span-2">
          <DocumentEditor output={deliverable?.body_md} />
        </div>
      </div>
    </div>
  );
}
