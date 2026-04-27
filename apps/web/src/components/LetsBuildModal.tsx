'use client';

import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader, ChevronDown } from 'lucide-react';
import { streamChat } from '@/lib/api';

interface Toggles {
  voice?: string;
  audience?: string;
  skills?: string[];
  playbook?: string;
  content_type?: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Brief {
  id?: number;
  title: string;
  brief_md: string;
  toggles_json?: string;
}

interface Deliverable {
  id?: number;
  folder_id?: number;
  content_type: string;
  title: string;
  status: string;
}

interface LetsBuildModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (deliverable: Deliverable) => void;
}

const VOICE_OPTIONS = ['opinionated', 'thoughtful', 'objective', 'technical', 'founder'];
const CONTENT_TYPES = ['blog', 'email', 'press_release', 'social_post', 'case_study', 'analyst_briefing'];

export default function LetsBuildModal({ isOpen, onClose, onSuccess }: LetsBuildModalProps) {
  const [mode, setMode] = useState<'guided' | 'yolo'>('guided');
  const [toggles, setToggles] = useState<Toggles>({
    voice: 'thoughtful',
    audience: '',
    skills: [],
    content_type: 'blog',
  });

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [briefPreview, setBriefPreview] = useState<Brief | null>(null);
  const [deliverable, setDeliverable] = useState<Deliverable | null>(null);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (!isOpen) return null;

  const handleToggleChange = (key: string, value: any) => {
    setToggles((prev) => ({ ...prev, [key]: value }));
  };

  const resetForm = () => {
    setMessages([]);
    setInput('');
    setBriefPreview(null);
    setDeliverable(null);
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleModeChange = (newMode: 'guided' | 'yolo') => {
    setMode(newMode);
    resetForm();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-3xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="border-b p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold">Let's Build</h2>
            <div className="flex gap-2">
              <button
                onClick={() => handleModeChange('guided')}
                className={`px-3 py-1 rounded text-sm transition ${
                  mode === 'guided'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Guided
              </button>
              <button
                onClick={() => handleModeChange('yolo')}
                className={`px-3 py-1 rounded text-sm transition ${
                  mode === 'yolo'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                YOLO
              </button>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-gray-100 rounded transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Toggles Panel */}
          <div className="w-64 border-r p-4 overflow-y-auto bg-gray-50">
            <h3 className="font-semibold text-sm mb-4">Settings</h3>

            {/* Voice */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Voice</label>
              <select
                value={toggles.voice || ''}
                onChange={(e) => handleToggleChange('voice', e.target.value)}
                className="w-full px-2 py-1 border rounded text-sm"
              >
                {VOICE_OPTIONS.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
            </div>

            {/* Audience */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Audience</label>
              <input
                type="text"
                value={toggles.audience || ''}
                onChange={(e) => handleToggleChange('audience', e.target.value)}
                placeholder="e.g., AI engineers"
                className="w-full px-2 py-1 border rounded text-sm"
              />
            </div>

            {/* Content Type */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                value={toggles.content_type || ''}
                onChange={(e) => handleToggleChange('content_type', e.target.value)}
                className="w-full px-2 py-1 border rounded text-sm"
              >
                {CONTENT_TYPES.map((ct) => (
                  <option key={ct} value={ct}>
                    {ct}
                  </option>
                ))}
              </select>
            </div>

            {/* Playbook */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Playbook</label>
              <input
                type="text"
                value={toggles.playbook || ''}
                onChange={(e) => handleToggleChange('playbook', e.target.value)}
                placeholder="auto"
                className="w-full px-2 py-1 border rounded text-sm"
              />
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {/* Chat/Input Area */}
            {!briefPreview && !deliverable && (
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 && mode === 'guided' && (
                    <div className="text-center text-gray-500 mt-8">
                      <p className="text-lg mb-2">Ask away, I'll learn as you talk</p>
                      <p className="text-sm">Tell me about what you want to create</p>
                    </div>
                  )}

                  {messages.length === 0 && mode === 'yolo' && (
                    <div className="text-center text-gray-500 mt-8">
                      <p className="text-lg mb-2">What do you want to create?</p>
                      <p className="text-sm">Be specific, give me context</p>
                    </div>
                  )}

                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xl px-4 py-2 rounded-lg ${
                          msg.role === 'user'
                            ? 'bg-blue-600 text-white rounded-br-none'
                            : 'bg-gray-100 text-gray-900 rounded-bl-none'
                        }`}
                      >
                        <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                      </div>
                    </div>
                  ))}

                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 px-4 py-2 rounded-lg rounded-bl-none">
                        <Loader className="w-4 h-4 animate-spin text-gray-600" />
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="flex justify-start">
                      <div className="bg-red-100 text-red-800 px-4 py-2 rounded-lg text-sm">
                        {error}
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="border-t p-4">
                  <div className="flex gap-2">
                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && e.ctrlKey) {
                          handleSendMessage();
                        }
                      }}
                      placeholder={
                        mode === 'guided'
                          ? "Tell me about your content idea..."
                          : "Describe what you want to create..."
                      }
                      className="flex-1 px-3 py-2 border rounded text-sm resize-none"
                      rows={3}
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!input.trim() || loading}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 transition h-fit"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Brief Preview */}
            {briefPreview && (
              <BriefPreview
                brief={briefPreview}
                onConfirm={handleCreateDeliverable}
                onEdit={(md) => setBriefPreview({ ...briefPreview, brief_md: md })}
                loading={loading}
              />
            )}

            {/* Success State */}
            {deliverable && (
              <div className="flex-1 flex flex-col items-center justify-center p-4">
                <div className="text-center">
                  <div className="text-5xl mb-4">✨</div>
                  <h3 className="text-xl font-semibold mb-2">Deliverable Created!</h3>
                  <p className="text-gray-600 mb-6">
                    {deliverable.title} is ready in your workspace
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        onSuccess?.(deliverable);
                        handleClose();
                      }}
                      className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                    >
                      Open Workspace
                    </button>
                    <button
                      onClick={resetForm}
                      className="px-6 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition"
                    >
                      Create Another
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  async function handleSendMessage() {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    if (mode === 'guided') {
      await handleGuidedChat(userMessage);
    } else {
      await handleYoloChat(userMessage);
    }
  }

  async function handleGuidedChat(userMessage: string) {
    setLoading(true);
    try {
      let assistantMessage = '';
      await streamChat(
        userMessage,
        undefined,
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
          // Check if we have enough for a brief (simple heuristic: 2+ exchanges)
          if (messages.length >= 3) {
            generateBriefFromChat(assistantMessage);
          }
          setLoading(false);
        },
        (err) => {
          setError(err);
          setLoading(false);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed');
      setLoading(false);
    }
  }

  async function handleYoloChat(userMessage: string) {
    setLoading(true);
    try {
      const response = await fetch('/api/chat/brief-yolo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: userMessage,
          toggles,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setBriefPreview({
        title: toggles.content_type || 'Untitled',
        brief_md: data.brief_md,
        toggles_json: JSON.stringify(toggles),
      });
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
      setLoading(false);
    }
  }

  function generateBriefFromChat(assistantMessage: string) {
    // Parse brief from assistant's final message
    const briefMd = `# Brief\n\n${assistantMessage}`;
    setBriefPreview({
      title: toggles.content_type || 'Untitled',
      brief_md: briefMd,
      toggles_json: JSON.stringify(toggles),
    });
  }

  async function handleCreateDeliverable() {
    if (!briefPreview) return;

    setLoading(true);
    try {
      // Create brief first
      const briefRes = await fetch('/api/briefs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: briefPreview.title,
          brief_md: briefPreview.brief_md,
          toggles_json: briefPreview.toggles_json,
          content_type: toggles.content_type,
        }),
      });

      if (!briefRes.ok) throw new Error('Failed to create brief');

      const brief = await briefRes.json();

      // Create deliverable
      const delRes = await fetch('/api/deliverables', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brief_id: brief.id,
          content_type: toggles.content_type,
          title: briefPreview.title,
          body_md: '',
        }),
      });

      if (!delRes.ok) throw new Error('Failed to create deliverable');

      const del = await delRes.json();
      setDeliverable(del);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Creation failed');
      setLoading(false);
    }
  }
}

interface BriefPreviewProps {
  brief: Brief;
  onConfirm: () => void;
  onEdit: (md: string) => void;
  loading: boolean;
}

function BriefPreview({ brief, onConfirm, onEdit, loading }: BriefPreviewProps) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="font-semibold mb-4">Brief Preview</h3>
        <textarea
          value={brief.brief_md}
          onChange={(e) => onEdit(e.target.value)}
          className="w-full h-full px-3 py-2 border rounded font-mono text-sm resize-none"
        />
      </div>
      <div className="border-t p-4 flex gap-2 justify-end">
        <button
          onClick={onConfirm}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 transition"
        >
          {loading ? 'Creating...' : 'Create Deliverable'}
        </button>
      </div>
    </div>
  );
}
