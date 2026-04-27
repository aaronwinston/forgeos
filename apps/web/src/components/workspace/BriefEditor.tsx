'use client';

/* eslint-disable @typescript-eslint/no-explicit-any */

import { useState, useCallback } from 'react';

interface BriefEditorProps {
  brief?: {
    id: number;
    title?: string;
    audience?: string;
    description?: string;
    brief_md?: string;
    toggles_json?: string;
  };
  deliverableId: number;
  onChange?: (brief: any) => void;
}

const VOICE_OPTIONS = ['opinionated', 'thoughtful', 'objective', 'technical', 'founder'];
const CONTENT_TYPE_OPTIONS = ['blog', 'email', 'press-release', 'case-study', 'whitepaper'];

export default function BriefEditor({ brief, onChange }: BriefEditorProps) {
  const defaultToggles = brief?.toggles_json ? JSON.parse(brief.toggles_json) : {};

  const [title, setTitle] = useState(brief?.title || '');
  const [audience, setAudience] = useState(brief?.audience || defaultToggles.audience || '');
  const [description, setDescription] = useState(brief?.description || brief?.brief_md || '');
  const [voice, setVoice] = useState(defaultToggles.voice || 'thoughtful');
  const [skills, setSkills] = useState(defaultToggles.skills || ['auto']);
  const [playbook, setPlaybook] = useState(defaultToggles.playbook || 'auto');
  const [contentType, setContentType] = useState(defaultToggles.content_type || 'blog');

  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [unsaved, setUnsaved] = useState(false);

  const handleSave = useCallback(async () => {
    if (!brief?.id) return;

    setIsSaving(true);
    setSaveError(null);

    try {
      const response = await fetch(`/api/briefs/${brief.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          audience,
          description,
          toggles: {
            brief_first: defaultToggles.brief_first ?? false,
            audience,
            voice,
            skills,
            playbook,
            content_type: contentType,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save brief');
      }

      const updatedBrief = await response.json();
      setUnsaved(false);
      onChange?.(updatedBrief);
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : 'Save failed');
    } finally {
      setIsSaving(false);
    }
  }, [brief?.id, title, audience, description, voice, skills, playbook, contentType, onChange, defaultToggles.brief_first]);

  const handleTitleChange = (value: string) => {
    setTitle(value);
    setUnsaved(true);
  };

  const handleAudienceChange = (value: string) => {
    setAudience(value);
    setUnsaved(true);
  };

  const handleDescriptionChange = (value: string) => {
    setDescription(value);
    setUnsaved(true);
  };

  const handleVoiceChange = (value: string) => {
    setVoice(value);
    setUnsaved(true);
  };

  const handlePlaybookChange = (value: string) => {
    setPlaybook(value);
    setUnsaved(true);
  };

  const handleContentTypeChange = (value: string) => {
    setContentType(value);
    setUnsaved(true);
  };

  const handleSkillsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const skillsList = value.split(',').map((s) => s.trim()).filter(Boolean);
    setSkills(skillsList.length > 0 ? skillsList : ['auto']);
    setUnsaved(true);
  };

  return (
    <div className="h-full flex flex-col bg-white p-6 overflow-y-auto">
      {/* Title */}
      <div className="mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
          📌 Title
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => handleTitleChange(e.target.value)}
          disabled={isSaving}
          placeholder="Brief title"
          className="w-full text-sm border border-gray-300 rounded px-3 py-2 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      {/* Audience */}
      <div className="mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
          👥 Audience
        </label>
        <input
          type="text"
          value={audience}
          onChange={(e) => handleAudienceChange(e.target.value)}
          disabled={isSaving}
          placeholder="AI engineers, product managers, etc."
          className="w-full text-sm border border-gray-300 rounded px-3 py-2 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      {/* Description/Prompt */}
      <div className="mb-6 flex-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
          📝 Brief / Prompt
        </label>
        <textarea
          value={description}
          onChange={(e) => handleDescriptionChange(e.target.value)}
          disabled={isSaving}
          placeholder="Write your brief or prompt here. This is the core instruction for the generation."
          className="w-full h-48 text-sm border border-gray-300 rounded px-3 py-2 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed resize-none"
        />
        <p className="text-xs text-gray-500 mt-1">
          {description.length} characters
        </p>
      </div>

      {/* Voice */}
      <div className="mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
          🎨 Voice
        </label>
        <select
          value={voice}
          onChange={(e) => handleVoiceChange(e.target.value)}
          disabled={isSaving}
          className="w-full text-sm border border-gray-300 rounded px-3 py-2 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {VOICE_OPTIONS.map((v) => (
            <option key={v} value={v}>
              {v.charAt(0).toUpperCase() + v.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Skills */}
      <div className="mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
          💡 Skills
        </label>
        <input
          type="text"
          value={skills?.join(', ') || ''}
          onChange={handleSkillsChange}
          disabled={isSaving}
          placeholder="auto, editorial-director, content-ops"
          className="w-full text-sm border border-gray-300 rounded px-3 py-2 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      {/* Playbook */}
      <div className="mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
          📋 Playbook
        </label>
        <input
          type="text"
          value={playbook}
          onChange={(e) => handlePlaybookChange(e.target.value)}
          disabled={isSaving}
          placeholder="auto"
          className="w-full text-sm border border-gray-300 rounded px-3 py-2 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      {/* Content Type */}
      <div className="mb-6">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
          📦 Content Type
        </label>
        <select
          value={contentType}
          onChange={(e) => handleContentTypeChange(e.target.value)}
          disabled={isSaving}
          className="w-full text-sm border border-gray-300 rounded px-3 py-2 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {CONTENT_TYPE_OPTIONS.map((type) => (
            <option key={type} value={type}>
              {type
                .split('-')
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ')}
            </option>
          ))}
        </select>
      </div>

      {/* Error Message */}
      {saveError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-xs text-red-600">
          {saveError}
        </div>
      )}

      {/* Action Bar */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            disabled={isSaving || !brief?.id || !unsaved}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          {unsaved && (
            <span className="text-xs text-amber-600 font-medium">
              ⚠️ Unsaved changes
            </span>
          )}
        </div>
        {!unsaved && !isSaving && (
          <span className="text-xs text-green-600 font-medium">
            ✅ Saved
          </span>
        )}
      </div>
    </div>
  );
}
