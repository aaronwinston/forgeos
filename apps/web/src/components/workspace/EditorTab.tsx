'use client';

import { useState, useEffect } from 'react';
import TipTapEditor from './TipTapEditor';
import { Save, AlertCircle } from 'lucide-react';

interface EditorTabProps {
  deliverable: {
    id: number;
    title: string;
    body_md?: string;
  };
}

export default function EditorTab({ deliverable }: EditorTabProps) {
  const [markdown, setMarkdown] = useState(deliverable.body_md || '');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [lastSavedMarkdown, setLastSavedMarkdown] = useState(
    deliverable.body_md || ''
  );

  const handleEditorChange = (newMarkdown: string) => {
    setMarkdown(newMarkdown);
    setHasUnsavedChanges(newMarkdown !== lastSavedMarkdown);
    setSaveError(null);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveError(null);

    try {
      const response = await fetch(
        `/api/deliverables/${deliverable.id}/body`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ body_md: markdown }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to save: ${response.statusText}`);
      }

      setLastSavedMarkdown(markdown);
      setHasUnsavedChanges(false);
    } catch (error) {
      setSaveError(
        error instanceof Error ? error.message : 'Failed to save changes'
      );
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        if (hasUnsavedChanges) {
          handleSave();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [hasUnsavedChanges, markdown]);

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header with Save button and unsaved indicator */}
      <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between bg-gray-50">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-gray-800">
            {deliverable.title}
          </h3>
          {hasUnsavedChanges && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
              <span className="text-xs text-orange-600 font-medium">
                Unsaved changes
              </span>
            </div>
          )}
          {saveError && (
            <div className="flex items-center gap-1">
              <AlertCircle size={14} className="text-red-500" />
              <span className="text-xs text-red-600 font-medium">
                {saveError}
              </span>
            </div>
          )}
        </div>

        <button
          onClick={handleSave}
          disabled={!hasUnsavedChanges || isSaving}
          className="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm font-medium"
        >
          <Save size={16} />
          {isSaving ? 'Saving...' : 'Save'}
        </button>
      </div>

      {/* Editor */}
      <TipTapEditor initialMarkdown={markdown} onChange={handleEditorChange} />
    </div>
  );
}
