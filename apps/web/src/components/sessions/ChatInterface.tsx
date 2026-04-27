'use client';
import { useState, useRef, useEffect } from 'react';
import { streamChat } from '@/lib/api';
import { Button } from '@/components/ui/Button';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatInterface({ sessionId }: { sessionId: number }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const send = () => {
    if (!input.trim() || streaming) return;
    const msg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    setStreaming(true);
    
    let assistantMsg = '';
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
    
    const stop = streamChat(msg, sessionId, (chunk) => {
      assistantMsg += chunk;
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1] = { role: 'assistant', content: assistantMsg };
        return next;
      });
    });
    
    setTimeout(() => { setStreaming(false); stop(); }, 30000);
  };
  
  return (
    <div className="border border-border rounded-card overflow-hidden bg-bg-secondary flex flex-col h-80">
      <div className="px-4 py-3 border-b border-border">
        <h3 className="text-sm font-semibold text-fg-primary">Chat</h3>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-xs text-fg-tertiary text-center pt-4">Ask anything about this session...</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] text-xs px-3 py-2 rounded-card leading-relaxed ${
              m.role === 'user'
                ? 'bg-brand-purple text-white'
                : 'bg-bg-tertiary text-fg-primary border border-border'
            }`}>
              {m.content || <span className="animate-pulse">▊</span>}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="px-3 py-3 border-t border-border flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask anything..."
          className="flex-1 text-sm border border-border rounded-input px-3 py-1.5 bg-bg-primary text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-2 focus:ring-accent/30"
        />
        <Button size="sm" onClick={send} loading={streaming}>Send</Button>
      </div>
    </div>
  );
}
