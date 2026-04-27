'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { getApiBase } from '@/lib/api';
import { Send, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ExpandPage() {
  const searchParams = useSearchParams();
  const filePath = searchParams?.get('file') || '';
  
  const [fileContent, setFileContent] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [draft, setDraft] = useState('');

  // Initialize the expansion flow
  useEffect(() => {
    if (!filePath) return;
    
    async function initExpand() {
      try {
        // Load file content
        const fileRes = await fetch(`${getApiBase()}/api/files/read?path=${encodeURIComponent(filePath)}`);
        if (fileRes.ok) {
          const { content } = await fileRes.json();
          setFileContent(content);
        }

        // Initialize expansion flow
        const res = await fetch(`${getApiBase()}/api/files/expand/init`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_path: filePath }),
        });

        if (res.ok) {
          const data = await res.json();
          setMessages([{
            role: 'assistant',
            content: data.initial_message,
          }]);
        }
      } catch (e) {
        console.error('Failed to initialize expansion:', e);
      } finally {
        setLoading(false);
      }
    }

    initExpand();
  }, [filePath]);

  async function handleSendMessage() {
    if (!input.trim() || !filePath) return;

    const newMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setSending(true);

    try {
      const res = await fetch(`${getApiBase()}/api/files/expand/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          message: input,
          conversation: messages,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
        }]);

        // Check if this was the final response (should indicate draft is ready)
        if (data.response.includes('draft') || messages.length > 8) {
          // Trigger draft generation
          await generateDraft();
        }
      }
    } catch (e) {
      console.error('Failed to send message:', e);
    } finally {
      setSending(false);
    }
  }

  async function generateDraft() {
    try {
      const res = await fetch(`${getApiBase()}/api/files/expand/draft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          conversation: messages,
          original_content: fileContent,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setDraft(data.draft);
      }
    } catch (e) {
      console.error('Failed to generate draft:', e);
    }
  }

  async function handleSaveDraft() {
    if (!draft || !filePath) return;
    setSavingDraft(true);

    try {
      const res = await fetch(`${getApiBase()}/api/files/expand/save-draft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
          draft,
        }),
      });

      if (res.ok) {
        // Redirect back to settings with the updated file
        window.location.href = `/settings?file=${encodeURIComponent(filePath)}`;
      }
    } catch (e) {
      console.error('Failed to save draft:', e);
    } finally {
      setSavingDraft(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-bg-primary">
        <p className="text-fg-secondary">Loading expansion flow...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-bg-primary">
      {/* Header */}
      <div className="border-b border-border bg-bg-secondary px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/settings" className="text-fg-secondary hover:text-fg-primary">
              <ArrowLeft size={20} />
            </Link>
            <div>
              <h1 className="text-lg font-bold text-fg-primary">Expand file</h1>
              <p className="text-xs text-fg-tertiary font-mono">{filePath}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden gap-6 p-6">
        {/* Chat */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 overflow-auto space-y-4 mb-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-md rounded-lg p-4 ${
                    msg.role === 'user'
                      ? 'bg-accent text-white'
                      : 'bg-bg-tertiary text-fg-primary border border-border'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Type your answer..."
              className="flex-1 px-4 py-2 border border-border rounded-lg bg-bg-secondary text-fg-primary placeholder-fg-tertiary focus:outline-none focus:ring-2 focus:ring-accent"
              disabled={sending}
            />
            <button
              onClick={handleSendMessage}
              disabled={sending || !input.trim()}
              className="px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>
        </div>

        {/* Draft preview */}
        {draft && (
          <div className="w-96 flex flex-col border-l border-border pl-6">
            <h2 className="text-sm font-bold text-fg-primary mb-3">Generated draft</h2>
            <div className="flex-1 overflow-auto bg-bg-secondary rounded-lg p-4 text-sm text-fg-secondary mb-4">
              <p className="whitespace-pre-wrap">{draft}</p>
            </div>
            <button
              onClick={handleSaveDraft}
              disabled={savingDraft}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
            >
              {savingDraft ? 'Saving...' : 'Save to file'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
