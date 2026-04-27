'use client';
import { useState } from 'react';
import { runSession, streamSession } from '@/lib/api';
import type { Session } from '@/lib/api';
import { Button } from '@/components/ui/Button';

const AGENTS = [
  'editorial-director', 'ai-researcher', 'dev-copywriter', 'dev-reviewer',
  'technical-fact-checker', 'seo-strategist', 'copy-chief', 'claims-risk-reviewer',
  'final-publish-reviewer', 'social-editor', 'content-ops-manager',
];

interface AgentChainProps {
  session: Session;
  onUpdate?: (session: Session) => void;
}

export function AgentChain({ session: initialSession, onUpdate }: AgentChainProps) {
  const [session, setSession] = useState(initialSession);
  const [running, setRunning] = useState(false);
  
  const handleRun = async () => {
    setRunning(true);
    await runSession(session.id);
    const stop = streamSession(session.id, (event) => {
      if (event.type === 'agent_update' || event.type === 'agent_complete') {
        setSession(prev => ({
          ...prev,
          current_agent: event.agent as string,
          progress: event.progress as number,
          status: 'active',
        }));
        onUpdate?.({ ...session, status: 'active' });
      }
      if (event.type === 'done') {
        setRunning(false);
        setSession(prev => ({ ...prev, status: 'complete', progress: 100 }));
        onUpdate?.({ ...session, status: 'complete' });
        stop();
      }
    });
  };
  
  const currentIndex = AGENTS.findIndex(a => a === session.current_agent);
  
  return (
    <div className="border border-border rounded-card overflow-hidden bg-bg-secondary">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 className="text-sm font-semibold text-fg-primary">Agent Chain</h3>
        {session.status !== 'complete' && (
          <Button size="sm" onClick={handleRun} loading={running} disabled={running || session.status === 'active'}>
            {session.status === 'active' ? 'Running…' : 'Run Chain'}
          </Button>
        )}
      </div>
      <div className="divide-y divide-border">
        {AGENTS.map((agent, i) => {
          const isDone = session.status === 'complete' || i < currentIndex;
          const isActive = i === currentIndex && session.status === 'active';
          return (
            <div key={agent} className={`flex items-center gap-3 px-4 py-2.5 ${isActive ? 'bg-warning/5' : ''}`}>
              <span className={`w-2 h-2 rounded-full shrink-0 ${isDone ? 'bg-success' : isActive ? 'bg-warning animate-pulse' : 'bg-border'}`} />
              <span className={`text-xs ${isActive ? 'text-fg-primary font-medium' : isDone ? 'text-fg-secondary' : 'text-fg-tertiary'}`}>
                {agent}
              </span>
              {isActive && <span className="text-xs text-warning ml-auto">Active</span>}
              {isDone && <span className="text-xs text-success ml-auto">✓</span>}
            </div>
          );
        })}
      </div>
      <div className="px-4 py-3 border-t border-border">
        <div className="flex justify-between text-xs text-fg-tertiary mb-1.5">
          <span>Overall progress</span>
          <span>{session.progress}%</span>
        </div>
        <div className="h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-500"
            style={{ width: `${session.progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}
