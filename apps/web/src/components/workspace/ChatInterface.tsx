'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader } from 'lucide-react';
import { streamChat } from '@/lib/api';
import MarkdownMessage from './MarkdownMessage';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  deliverableId: number;
  briefId?: number;
  briefData?: {
    id: number;
    brief_md: string;
    toggles_json?: string;
  };
  sessionId?: number;
}

export default function ChatInterface({
  deliverableId,
  briefData,
  sessionId,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    let assistantMessage = '';
    const cancelStream = streamChat(
      userMessage,
      sessionId,
      (chunk) => {
        assistantMessage += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          if (updated[updated.length - 1]?.role === 'assistant') {
            updated[updated.length - 1].content = assistantMessage;
          } else {
            updated.push({ role: 'assistant', content: assistantMessage });
          }
          return updated;
        });
      },
      () => {
        // Stream completed successfully
        setLoading(false);
      },
      (errorMsg) => {
        // Stream error
        setError(errorMsg);
        setLoading(false);
      }
    );

    // Cleanup function for component unmount
    return () => {
      cancelStream();
    };
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Messages Container */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">💬 Ready to chat</p>
              <p className="text-xs text-gray-500">Ask me to help with: {briefData?.id || deliverableId}</p>
              <p className="text-xs text-gray-400 mt-4">Tip: Use Cmd+Enter to send (Ctrl+Enter on Windows)</p>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-2xl ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-lg px-4 py-3'
                    : 'bg-gray-100 text-gray-900 rounded-lg px-4 py-3'
                }`}
              >
                {msg.role === 'assistant' ? (
                  <MarkdownMessage content={msg.content} />
                ) : (
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-3 flex items-center gap-2">
              <Loader className="w-4 h-4 animate-spin" />
              <span className="text-sm text-gray-600">Thinking...</span>
            </div>
          </div>
        )}
        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 max-w-md">
              <p className="text-sm font-medium">Error</p>
              <p className="text-xs mt-1">{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  setLoading(false);
                }}
                className="text-xs mt-2 text-red-600 hover:text-red-700 font-medium"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={handleSend} className="flex gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me to draft a blog post..."
            disabled={loading}
            className="flex-1 min-h-10 max-h-32 px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span className="text-sm">Send</span>
              </>
            )}
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2">Press Cmd+Enter (or Ctrl+Enter) to send • Shift+Enter for new line</p>
      </div>
    </div>
  );
}
