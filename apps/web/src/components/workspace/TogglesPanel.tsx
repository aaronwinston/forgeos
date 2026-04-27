'use client';

/* eslint-disable @typescript-eslint/no-explicit-any */

import { useState, useCallback } from 'react';

interface TogglesPanelProps {
  brief?: {
    id: number;
    toggles_json?: string;
  };
  onChange?: (toggles: Record<string, any>) => void;
}

const VOICE_OPTIONS = ['opinionated', 'thoughtful', 'objective', 'technical', 'founder'];
const CONTENT_TYPE_OPTIONS = ['blog', 'email', 'press-release', 'case-study', 'whitepaper'];

export default function TogglesPanel({ brief, onChange }: TogglesPanelProps) {
  const defaultToggles = brief?.toggles_json ? JSON.parse(brief.toggles_json) : {};

  const [toggles, setToggles] = useState<Record<string, any>>({
    brief_first: defaultToggles.brief_first ?? false,
    audience: defaultToggles.audience ?? '',
    voice: defaultToggles.voice ?? 'thoughtful',
    skills: defaultToggles.skills ?? ['auto'],
    playbook: defaultToggles.playbook ?? 'auto',
    content_type: defaultToggles.content_type ?? 'blog',
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleChange = useCallback(
    async (key: string, value: any) => {
      const newToggles = { ...toggles, [key]: value };
      setToggles(newToggles);
      setSaveError(null);

      if (!brief?.id) return;

      setIsSaving(true);
      try {
        const response = await fetch(`/api/briefs/${brief.id}/toggles`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newToggles),
        });

        if (!response.ok) {
          throw new Error('Failed to save toggles');
        }

        onChange?.(newToggles);
      } catch (error) {
        setSaveError(error instanceof Error ? error.message : 'Save failed');
        setToggles(toggles);
      } finally {
        setIsSaving(false);
      }
    },
    [toggles, brief?.id, onChange]
  );

  const handleSkillsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const skills = value.split(',').map((s) => s.trim()).filter(Boolean);
    handleChange('skills', skills.length > 0 ? skills : ['auto']);
  };

  return (
    <div className="p-3 border-b border-gray-200 space-y-3">
      <div>
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">🔄 Brief-First</p>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={toggles.brief_first}
            onChange={(e) => handleChange('brief_first', e.target.checked)}
            disabled={isSaving}
            className="w-4 h-4 rounded cursor-pointer disabled:opacity-50"
          />
          <span className="text-xs text-gray-700">Start with brief</span>
        </label>
        {saveError && <p className="text-xs text-red-600 mt-1">{saveError}</p>}
      </div>

      <div className="space-y-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">📝 Audience</label>
        <input
          type="text"
          value={toggles.audience}
          onChange={(e) => handleChange('audience', e.target.value)}
          disabled={isSaving}
          placeholder="AI engineers, product managers, etc."
          className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      <div className="space-y-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">🎨 Voice</label>
        <select
          value={toggles.voice}
          onChange={(e) => handleChange('voice', e.target.value)}
          disabled={isSaving}
          className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {VOICE_OPTIONS.map((voice) => (
            <option key={voice} value={voice}>
              {voice.charAt(0).toUpperCase() + voice.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">💡 Skills</label>
        <input
          type="text"
          value={toggles.skills?.join(', ') || ''}
          onChange={handleSkillsChange}
          disabled={isSaving}
          placeholder="auto, editorial-director, content-ops"
          className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      <div className="space-y-1">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">📋 Playbook</label>
        <input
          type="text"
          value={toggles.playbook}
          onChange={(e) => handleChange('playbook', e.target.value)}
          disabled={isSaving}
          placeholder="auto"
          className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      <div className="space-y-1">
        <label className="text-xs font-semibold text-gray-500 tracking-wider block">📦 Content type</label>
        <select
          value={toggles.content_type}
          onChange={(e) => handleChange('content_type', e.target.value)}
          disabled={isSaving}
          className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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

      {isSaving && <p className="text-xs text-gray-500 italic">Saving...</p>}
    </div>
  );
}
