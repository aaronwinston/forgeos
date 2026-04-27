'use client';
import { useEffect, useState, useRef } from 'react';
import { CONTENT_TYPES } from '@/lib/types';
import CreateItemModal from '@/components/projects/CreateItemModal';

export default function ProjectPage({ params }: { params: { id: string } }) {
  const projectId = parseInt(params.id);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [folders, setFolders] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [selectedFolder, setSelectedFolder] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [deliverables, setDeliverables] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [selectedDeliverable, setSelectedDeliverable] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [toggles, setToggles] = useState({
    brief_first: true,
    audience: 'AI engineers',
    voice: 'thoughtful',
    content_type: 'blog',
    playbook: 'auto',
    yolo: false,
  });
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [showDeliverableModal, setShowDeliverableModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/api/projects/${projectId}/folders`).then(r => r.json()).then(setFolders).catch(console.error);
    fetch('http://localhost:8000/api/chat/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId }),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    }).then(r => r.json()).then((s: any) => setSessionId(s.id)).catch(console.error);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  useEffect(() => {
    if (selectedFolder) {
      fetch(`http://localhost:8000/api/folders/${selectedFolder.id}/deliverables`).then(r => r.json()).then(setDeliverables).catch(console.error);
    }
  }, [selectedFolder]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || streaming) return;
    const userContent = input;
    const userMsg = { role: 'user', content: userContent, id: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setStreaming(true);
    const aiMsgId = Date.now() + 1;
    setMessages(prev => [...prev, { role: 'assistant', content: '', id: aiMsgId }]);
    try {
      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, project_id: projectId, message: userContent, toggles }),
      });
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let full = '';
      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                full += data.chunk;
                setMessages(prev => prev.map(m => m.id === aiMsgId ? { ...m, content: full } : m));
              }
            } catch { /* ignore parse errors */ }
          }
        }
      }
    } catch (e) { console.error(e); }
    setStreaming(false);
  };

  return (
    <div className="flex h-full">
      <aside className="w-48 border-r p-3 space-y-2 overflow-auto">
        <p className="text-xs font-semibold text-gray-500 uppercase">Folders</p>
        {folders.map(f => (
          <button key={f.id} onClick={() => setSelectedFolder(f)}
            className={`w-full text-left text-xs px-2 py-1.5 rounded ${selectedFolder?.id === f.id ? 'bg-gray-100' : 'hover:bg-gray-50'}`}>
            {f.name}
          </button>
        ))}
        <button className="text-xs text-gray-500 hover:text-gray-700 w-full text-left" onClick={() => setShowFolderModal(true)}>+ New folder</button>
        {selectedFolder && (<>
          <p className="text-xs font-semibold text-gray-500 uppercase mt-3">Deliverables</p>
          {deliverables.map(d => (
            <button key={d.id} onClick={() => setSelectedDeliverable(d)}
              className={`w-full text-left text-xs px-2 py-1.5 rounded ${selectedDeliverable?.id === d.id ? 'bg-gray-100' : 'hover:bg-gray-50'}`}>
              <span className="inline-block border rounded px-1 text-[10px] mr-1">{d.content_type}</span>{d.title}
            </button>
          ))}
          <button className="text-xs text-gray-500 hover:text-gray-700 w-full text-left" onClick={() => setShowDeliverableModal(true)}>+ New deliverable</button>
        </>)}
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b flex">
          {['chat', 'editor', 'brief'].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm ${activeTab === tab ? 'border-b-2 border-black font-medium' : 'text-gray-500'}`}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col">
            <div className="flex-1 overflow-auto p-4 space-y-3">
              {messages.length === 0 && <p className="text-sm text-gray-500">Start a conversation. Describe what you want to create.</p>}
              {messages.map(msg => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${msg.role === 'user' ? 'bg-black text-white' : 'bg-gray-100'}`}>
                    {msg.content || (streaming && msg.role === 'assistant' ? '...' : '')}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className="border-t p-3 flex gap-2">
              <textarea value={input} onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }}}
                placeholder="Describe what you want to create..." className="flex-1 resize-none border rounded p-2 text-sm" rows={2} />
              <button onClick={sendMessage} disabled={streaming || !input.trim()} className="px-4 py-2 bg-black text-white rounded text-sm disabled:opacity-50">
                {streaming ? '...' : 'Send'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'editor' && (
          <div className="flex-1 p-4 flex flex-col">
            {selectedDeliverable ? (
              <div className="h-full flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <h2 className="font-medium">{selectedDeliverable.title}</h2>
                  <button className="px-3 py-1 bg-black text-white rounded text-sm" onClick={async () => {
                    await fetch(`http://localhost:8000/api/deliverables/${selectedDeliverable.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ body_md: selectedDeliverable.body_md }) });
                  }}>Save</button>
                </div>
                <textarea className="flex-1 font-mono text-sm resize-none border rounded p-3"
                  value={selectedDeliverable.body_md || ''}
                  onChange={e => setSelectedDeliverable({ ...selectedDeliverable, body_md: e.target.value })} />
              </div>
            ) : <p className="text-gray-500 text-sm">Select a deliverable to edit it.</p>}
          </div>
        )}

        {activeTab === 'brief' && (
          <div className="flex-1 p-4 space-y-3">
            <p className="text-sm text-gray-500">Generate a structured brief from your prompt.</p>
            <button onClick={async () => {
              if (!input) return alert('Enter a prompt in the chat tab first.');
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              const result: any = await fetch('http://localhost:8000/api/chat/brief', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_id: projectId, user_prompt: input, content_type: toggles.content_type, toggles }),
              }).then(r => r.json());
              setMessages(prev => [...prev, { role: 'assistant', content: result.brief_md, id: Date.now() }]);
              setActiveTab('chat');
            }} className="px-4 py-2 bg-black text-white rounded text-sm">Generate Brief from Prompt</button>
          </div>
        )}
      </div>

      <aside className="w-56 border-l p-3 space-y-4 overflow-auto">
        <p className="text-xs font-semibold text-gray-500 uppercase">Toggles</p>
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Content Type</label>
          <select className="w-full text-xs border rounded px-2 py-1.5 bg-white" value={toggles.content_type}
            onChange={e => setToggles(t => ({ ...t, content_type: e.target.value }))}>
            {CONTENT_TYPES.map(ct => <option key={ct} value={ct}>{ct}</option>)}
          </select>
        </div>
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Voice</label>
          <select className="w-full text-xs border rounded px-2 py-1.5 bg-white" value={toggles.voice}
            onChange={e => setToggles(t => ({ ...t, voice: e.target.value }))}>
            {['opinionated', 'thoughtful', 'objective', 'technical', 'founder'].map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Audience</label>
          <input type="text" className="w-full text-xs border rounded px-2 py-1.5" value={toggles.audience}
            onChange={e => setToggles(t => ({ ...t, audience: e.target.value }))} />
        </div>
        <div className="flex items-center justify-between">
          <label className="text-xs text-gray-500">Brief first</label>
          <input type="checkbox" checked={toggles.brief_first} onChange={e => setToggles(t => ({ ...t, brief_first: e.target.checked }))} />
        </div>
        <div className="flex items-center justify-between">
          <label className="text-xs text-gray-500">YOLO mode</label>
          <input type="checkbox" checked={toggles.yolo} onChange={e => setToggles(t => ({ ...t, yolo: e.target.checked }))} />
        </div>
        <div className="space-y-1">
          <label className="text-xs text-gray-500">Playbook</label>
          <input type="text" className="w-full text-xs border rounded px-2 py-1.5" value={toggles.playbook}
            onChange={e => setToggles(t => ({ ...t, playbook: e.target.value }))} placeholder="auto" />
        </div>
      </aside>
    </div>
  );
}
