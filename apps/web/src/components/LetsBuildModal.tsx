'use client';

import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader } from 'lucide-react';

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
  created_at?: string;
  updated_at?: string;
}

interface LetsBuildModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (deliverable: Deliverable) => void;
}

const VOICE_OPTIONS = ['opinionated', 'thoughtful', 'objective', 'technical', 'founder'];
const CONTENT_TYPES = ['blog', 'email', 'press_release', 'social_post', 'case_study', 'analyst_briefing'];

const formatContentTypeLabel = (value: string) =>
  value
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');

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

  const handleToggleChange = (key: string, value: string | string[]) => {
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
    <div className="fixed inset-0 bg-black/65 backdrop-blur-sm flex items-center justify-center z-50 p-4 sm:p-6">
      <div className="surface-elevated w-full max-w-6xl h-[86vh] min-h-[640px] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="border-b border-border/80 px-5 py-4 flex items-start justify-between gap-4">
          <div className="space-y-3">
            <div>
              <h2 className="text-xl font-semibold tracking-tight text-fg-primary">Let&apos;s build</h2>
              <p className="text-sm text-fg-secondary mt-1">
                Turn a rough idea into a ready-to-edit deliverable.
              </p>
            </div>
            <div className="inline-flex items-center rounded-lg border border-border bg-bg-tertiary p-1 gap-1">
            <button
              onClick={() => handleModeChange('guided')}
                className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                mode === 'guided'
                    ? 'bg-bg-secondary text-fg-primary border border-border shadow-sm'
                    : 'text-fg-secondary hover:text-fg-primary'
              }`}
            >
              Guided
            </button>
            <button
              onClick={() => handleModeChange('yolo')}
                className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                mode === 'yolo'
                    ? 'bg-bg-secondary text-fg-primary border border-border shadow-sm'
                    : 'text-fg-secondary hover:text-fg-primary'
              }`}
            >
              YOLO
            </button>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 text-fg-tertiary hover:text-fg-primary hover:bg-bg-tertiary rounded-md border border-transparent hover:border-border transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Toggles Panel */}
          <div className="w-[300px] border-r border-border/80 p-4 overflow-y-auto bg-bg-tertiary/40">
            <h3 className="font-semibold text-sm tracking-tight mb-4 text-fg-primary">Session settings</h3>

            {/* Voice */}
            <div className="mb-4">
              <label className="block text-xs font-semibold uppercase tracking-wide text-fg-tertiary mb-2">Voice</label>
              <select
                value={toggles.voice || ''}
                onChange={(e) => handleToggleChange('voice', e.target.value)}
                className="w-full px-3 py-2 border border-border bg-bg-secondary rounded-lg text-sm text-fg-primary focus:outline-none focus:ring-2 focus:ring-accent/30"
              >
                {VOICE_OPTIONS.map((v) => (
                  <option key={v} value={v}>
                    {v.charAt(0).toUpperCase() + v.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Audience */}
            <div className="mb-4">
              <label className="block text-xs font-semibold uppercase tracking-wide text-fg-tertiary mb-2">Audience</label>
              <input
                type="text"
                value={toggles.audience || ''}
                onChange={(e) => handleToggleChange('audience', e.target.value)}
                placeholder="e.g., AI engineers"
                className="w-full px-3 py-2 border border-border bg-bg-secondary rounded-lg text-sm text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-2 focus:ring-accent/30"
              />
            </div>

            {/* Content Type */}
            <div className="mb-4">
              <label className="block text-xs font-semibold uppercase tracking-wide text-fg-tertiary mb-2">Type</label>
              <select
                value={toggles.content_type || ''}
                onChange={(e) => handleToggleChange('content_type', e.target.value)}
                className="w-full px-3 py-2 border border-border bg-bg-secondary rounded-lg text-sm text-fg-primary focus:outline-none focus:ring-2 focus:ring-accent/30"
              >
                {CONTENT_TYPES.map((ct) => (
                  <option key={ct} value={ct}>
                    {formatContentTypeLabel(ct)}
                  </option>
                ))}
              </select>
            </div>

            {/* Playbook */}
            <div className="mb-4">
              <label className="block text-xs font-semibold uppercase tracking-wide text-fg-tertiary mb-2">Playbook</label>
              <input
                type="text"
                value={toggles.playbook || ''}
                onChange={(e) => handleToggleChange('playbook', e.target.value)}
                placeholder="auto"
                className="w-full px-3 py-2 border border-border bg-bg-secondary rounded-lg text-sm text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-2 focus:ring-accent/30"
              />
            </div>

            <div className="mt-6 rounded-xl border border-border bg-bg-secondary/70 p-3 text-xs text-fg-secondary leading-relaxed">
              {mode === 'guided'
                ? 'Guided asks follow-up questions and builds a stronger brief before drafting.'
                : 'YOLO creates a complete brief and deliverable from a single prompt.'}
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {/* Chat/Input Area */}
            {!briefPreview && !deliverable && (
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-5 space-y-4">
                  {messages.length === 0 && mode === 'guided' && (
                    <div className="surface-muted p-6 text-center mt-10 max-w-xl mx-auto">
                      <p className="text-lg mb-2 text-fg-primary">Ask away, I&apos;ll learn as you talk</p>
                      <p className="text-sm text-fg-secondary">Share your goal and constraints. I&apos;ll shape the brief with you.</p>
                    </div>
                  )}

                  {messages.length === 0 && mode === 'yolo' && (
                    <div className="surface-muted p-6 text-center mt-10 max-w-xl mx-auto">
                      <p className="text-lg mb-2 text-fg-primary">What do you want to create?</p>
                      <p className="text-sm text-fg-secondary">Describe your goal clearly and include the audience and angle.</p>
                    </div>
                  )}

                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xl px-4 py-2 rounded-card ${
                          msg.role === 'user'
                            ? 'bg-accent text-white rounded-br-none shadow-sm'
                            : 'bg-bg-tertiary text-fg-primary rounded-bl-none border border-border'
                        }`}
                      >
                        <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                      </div>
                    </div>
                  ))}

                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-bg-tertiary border border-border px-4 py-2 rounded-card rounded-bl-none">
                        <Loader className="w-4 h-4 animate-spin text-fg-secondary" />
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="flex justify-start">
                      <div className="bg-error/10 text-error px-4 py-2 rounded-card text-sm">
                        {error}
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="border-t border-border/80 p-4">
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
                      className="flex-1 px-3 py-2.5 border border-border bg-bg-tertiary/50 rounded-lg text-sm resize-none text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-2 focus:ring-accent/30"
                      rows={3}
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!input.trim() || loading}
                      className="px-4 py-2.5 bg-accent text-white rounded-lg hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed transition h-fit border border-transparent"
                      aria-label="Send message"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-xs text-fg-tertiary mt-2">Tip: press Ctrl+Enter to send</p>
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
                    <h3 className="text-xl font-semibold mb-2">Deliverable created!</h3>
                  <p className="text-fg-secondary mb-6">
                    {deliverable.title} is ready in your workspace
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        onSuccess?.(deliverable);
                        handleClose();
                      }}
                      className="px-6 py-2 bg-accent text-white rounded-lg hover:bg-accent-hover transition"
                    >
                      Open workspace
                    </button>
                    <button
                      onClick={resetForm}
                      className="px-6 py-2 bg-bg-tertiary text-fg-primary border border-border rounded-lg hover:bg-bg-tertiary/80 transition"
                    >
                      Create another
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
      // First check if we have a chat session and messages
      const newMessages = [...messages, { role: 'user' as const, content: userMessage }];
      
      // Call the guided brief endpoint
      const response = await fetch('/api/chat/brief-guided', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages,
          toggles,
          mode: 'guided',
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let isBriefComplete = false;
      let completeBriefMd = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                assistantMessage += data.chunk;
                setMessages((prev) => {
                  const updated = [...prev];
                  if (updated[updated.length - 1]?.role === 'assistant') {
                    updated[updated.length - 1].content = assistantMessage;
                  } else {
                    updated.push({ role: 'assistant', content: assistantMessage });
                  }
                  return updated;
                });
              }
              if (data.done && data.state === 'complete') {
                // Agent returned complete brief as JSON
                isBriefComplete = true;
                completeBriefMd = data.brief_md || assistantMessage;
              }
            } catch {
              // Silent parse error
            }
          }
        }
      }

      // If agent completed, show brief preview
      if (isBriefComplete) {
        generateBriefFromChat(completeBriefMd);
      }

      setLoading(false);
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
      
      // YOLO mode is atomic: brief and deliverable are created by the backend
      // We just show the brief preview, but the deliverable is already created
      setBriefPreview({
        title: data.brief.title || (toggles.content_type || 'Untitled'),
        brief_md: data.brief.brief_md,
        toggles_json: data.brief.toggles_json,
      });
      
      // Store the deliverable so we can navigate to it on confirm
      setDeliverable({
        id: data.deliverable.id,
        folder_id: data.deliverable.folder_id,
        content_type: data.deliverable.content_type,
        title: data.deliverable.title,
        status: data.deliverable.status,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
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
      // If deliverable already exists (YOLO mode), just navigate to it
      if (deliverable) {
        setLoading(false);
        return; // Guided mode will handle the creation below
      }

      // GUIDED MODE: Create brief and deliverable atomically
      // Get or create default project and folder
      const projectsRes = await fetch('/api/projects');
      const projects = await projectsRes.json();
      let projectId = projects[0]?.id;

      if (!projectId) {
        const createProjectRes = await fetch('/api/projects', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: 'Default Project' }),
        });
        const project = await createProjectRes.json();
        projectId = project.id;
      }

      // Get or create default folder
      const foldersRes = await fetch(`/api/projects/${projectId}/folders`);
      const folders = await foldersRes.json();
      let folderId = folders[0]?.id;

      if (!folderId) {
        const createFolderRes = await fetch('/api/folders', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_id: projectId,
            name: 'Deliverables',
          }),
        });
        const folder = await createFolderRes.json();
        folderId = folder.id;
      }

      // Create brief (project_id is now optional, will use default)
      const briefRes = await fetch('/api/briefs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          title: briefPreview.title || (toggles.content_type || 'Untitled'),
          brief_md: briefPreview.brief_md,
          toggles_json: briefPreview.toggles_json,
        }),
      });

      if (!briefRes.ok) throw new Error('Failed to create brief');

      await briefRes.json();

      // Create deliverable (folder_id is now optional, will use default)
      const delRes = await fetch('/api/deliverables', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          folder_id: folderId,
          content_type: toggles.content_type || 'blog',
          title: briefPreview.title || (toggles.content_type || 'Untitled'),
          status: 'draft',
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
      <div className="flex-1 overflow-y-auto p-5">
        <h3 className="font-semibold mb-4 tracking-tight text-fg-primary">Brief preview</h3>
        <textarea
          value={brief.brief_md}
          onChange={(e) => onEdit(e.target.value)}
          className="w-full h-full min-h-[340px] px-3 py-2 border border-border bg-bg-tertiary/50 rounded-lg font-mono text-sm resize-none text-fg-primary focus:outline-none focus:ring-2 focus:ring-accent/30"
        />
      </div>
      <div className="border-t border-border/80 p-4 flex gap-2 justify-end">
        <button
          onClick={onConfirm}
          disabled={loading}
          className="px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Creating...' : 'Create deliverable'}
        </button>
      </div>
    </div>
  );
}
