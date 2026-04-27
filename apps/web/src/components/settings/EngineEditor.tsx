'use client';

import { useEffect, useState } from 'react';
import { AlertCircle, Link2 } from 'lucide-react';
import MarkdownEditor from '@/components/MarkdownEditor';

interface EngineEditorProps {
  filePath: string | null;
  isDirty: boolean;
  onDirtyChange: (dirty: boolean) => void;
  onSave?: () => Promise<void>;
}

export default function EngineEditor({ filePath, isDirty, onDirtyChange, onSave }: EngineEditorProps) {
  const [content, setContent] = useState('');
  const [metadata, setMetadata] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [references, setReferences] = useState<{ skills: number; playbooks: number }>({ skills: 0, playbooks: 0 });
  const [loadingRefs, setLoadingRefs] = useState(false);

  // Load file when path changes
  useEffect(() => {
    if (!filePath) {
      setContent('');
      setMetadata({});
      setReferences({ skills: 0, playbooks: 0 });
      return;
    }

    setLoading(true);
    setError('');
    onDirtyChange(false);

    fetch(`http://localhost:8000/api/files/read?path=${encodeURIComponent(filePath)}`)
      .then(r => {
        if (!r.ok) throw new Error('Failed to load file');
        return r.json();
      })
      .then(data => {
        setContent(data.content);
        setMetadata(data.metadata || {});
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));

    // Load references count
    loadReferencesCount(filePath);
  }, [filePath, onDirtyChange]);

  async function loadReferencesCount(path: string) {
    setLoadingRefs(true);
    try {
      const response = await fetch(`http://localhost:8000/api/settings/references?path=${encodeURIComponent(path)}`);
      if (response.ok) {
        const refsData = await response.json();
        setReferences(refsData);
      }
    } catch (e) {
      console.error('Failed to load references:', e);
    } finally {
      setLoadingRefs(false);
    }
  }

  function handleContentChange(newContent: string) {
    setContent(newContent);
    onDirtyChange(true);
  }

  function handleMetadataChange(newMetadata: Record<string, unknown>) {
    setMetadata(newMetadata);
    onDirtyChange(true);
  }

  // Build frontmatter + content for save
  async function handleSave() {
    if (!filePath) return;

    const lines: string[] = [];
    if (Object.keys(metadata).length > 0) {
      lines.push('---');
      lines.push(formatYaml(metadata));
      lines.push('---');
    }
    lines.push(content);

    try {
      const response = await fetch('http://localhost:8000/api/files/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath, content: lines.join('\n') }),
      });

      if (!response.ok) throw new Error('Save failed');
      
      onDirtyChange(false);
      
      if (onSave) {
        await onSave();
      }
    } catch (e) {
      setError(`Save failed: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  function formatYaml(obj: Record<string, unknown>): string {
    return Object.entries(obj)
      .map(([k, v]) => {
        if (typeof v === 'string') {
          const needsQuotes = v.includes(':') || v.includes('\n');
          return `${k}: ${needsQuotes ? `"${v.replace(/"/g, '\\"')}"` : v}`;
        }
        if (Array.isArray(v)) {
          return `${k}:\n${v.map(item => `  - ${item}`).join('\n')}`;
        }
        return `${k}: ${v}`;
      })
      .join('\n');
  }

  if (!filePath) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-500">Select a file from the tree to edit it</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white h-full overflow-hidden">
      {/* Header */}
      <div className="border-b bg-gray-50 p-4 flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs text-gray-500 font-mono mb-1">{filePath}</p>
          <div className="flex items-center gap-2">
            {!loadingRefs && (references.skills > 0 || references.playbooks > 0) && (
              <div className="flex items-center gap-1 text-xs text-blue-600">
                <Link2 size={14} />
                <span>Referenced by {references.skills} skills, {references.playbooks} playbooks</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {isDirty && <span className="text-xs text-orange-600 font-medium">Unsaved changes</span>}
          <button
            onClick={handleSave}
            className="px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 font-medium"
          >
            Save
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 p-3 flex items-start gap-2">
          <AlertCircle size={16} className="text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Frontmatter panel */}
      {Object.keys(metadata).length > 0 && (
        <div className="border-b bg-gray-50 p-4">
          <h3 className="text-xs font-bold text-gray-700 mb-3 uppercase">Frontmatter</h3>
          <div className="space-y-2">
            {Object.entries(metadata).map(([key, value]) => (
              <div key={key} className="flex gap-2 items-start text-xs">
                <span className="font-mono text-gray-600 w-20">{key}:</span>
                <input
                  type="text"
                  value={typeof value === 'string' ? value : JSON.stringify(value)}
                  onChange={e => handleMetadataChange({ ...metadata, [key]: e.target.value })}
                  className="flex-1 px-2 py-1 border rounded text-gray-900 font-mono bg-white"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Editor */}
      <MarkdownEditor value={content} onChange={handleContentChange} />
    </div>
  );
}
