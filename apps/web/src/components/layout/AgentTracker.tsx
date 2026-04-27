'use client';
import { useEffect, useState, useCallback } from 'react';
import { getSessions } from '@/lib/api';
import type { Session } from '@/lib/api';

const AGENTS = [
  { name: 'editorial-director', task: 'Content strategy & direction' },
  { name: 'ai-researcher', task: 'Research & source gathering' },
  { name: 'dev-copywriter', task: 'Draft creation' },
  { name: 'dev-reviewer', task: 'Copy review & polish' },
  { name: 'technical-fact-checker', task: 'Technical accuracy' },
  { name: 'seo-strategist', task: 'SEO optimization' },
  { name: 'copy-chief', task: 'Final copy edit' },
  { name: 'claims-risk-reviewer', task: 'Claims & risk review' },
  { name: 'final-publish-reviewer', task: 'Publish readiness' },
  { name: 'social-editor', task: 'Social content' },
  { name: 'content-ops-manager', task: 'Distribution & ops' },
];

function AgentDot({ status }: { status: 'idle' | 'active' | 'done' }) {
  const colors = {
    idle: 'bg-border',
    active: 'bg-warning animate-pulse',
    done: 'bg-success',
  };
  return <span className={`inline-block w-2 h-2 rounded-full shrink-0 ${colors[status]}`} />;
}

export function AgentTracker() {
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  
  const refresh = useCallback(async () => {
    const sessions = await getSessions();
    const active = sessions.find(s => s.status === 'active');
    setActiveSession(active || null);
  }, []);
  
  useEffect(() => {
    refresh();
    const interval = setInterval(() => {
      if (activeSession?.status === 'active') refresh();
    }, 3000);
    return () => clearInterval(interval);
  }, [refresh, activeSession?.status]);
  
  const currentAgentIndex = activeSession
    ? AGENTS.findIndex(a => a.name === activeSession.current_agent)
    : -1;

  return (
    <aside className="w-64 border-l border-border bg-bg-secondary flex flex-col shrink-0">
      <div className="p-4 border-b border-border">
        <h3 className="text-xs font-semibold text-fg-tertiary tracking-wide">Agent team</h3>
        {activeSession && (
          <p className="text-xs text-fg-secondary mt-0.5 truncate">{activeSession.title}</p>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {AGENTS.map((agent, i) => {
          let status: 'idle' | 'active' | 'done' = 'idle';
          if (activeSession) {
            if (i < currentAgentIndex) status = 'done';
            else if (i === currentAgentIndex) status = 'active';
          }
          return (
            <div key={agent.name} className="flex items-start gap-2.5 px-2 py-2 rounded-lg hover:bg-bg-tertiary transition-colors">
              <AgentDot status={status} />
              <div className="min-w-0">
                <p className={`text-xs font-medium truncate ${status === 'active' ? 'text-fg-primary' : 'text-fg-secondary'}`}>
                  {agent.name}
                </p>
                <p className="text-xs text-fg-tertiary truncate">{agent.task}</p>
              </div>
            </div>
          );
        })}
        {!activeSession && (
          <p className="text-xs text-fg-tertiary text-center py-4">No active session</p>
        )}
      </div>
      {activeSession && (
        <div className="p-3 border-t border-border">
          <div className="flex justify-between text-xs text-fg-tertiary mb-1">
            <span>Progress</span>
            <span>{activeSession.progress}%</span>
          </div>
          <div className="h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full bg-accent rounded-full transition-all duration-500"
              style={{ width: `${activeSession.progress}%` }}
            />
          </div>
        </div>
      )}
    </aside>
  );
}
