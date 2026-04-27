'use client';

import { useState, useCallback } from 'react';

interface ContextInUsePanelProps {
  brief?: {
    id: number;
    context_layers_json?: string;
    skills_json?: string;
    intelligence_items_json?: string;
  };
  intelligenceItems?: Array<{
    id: number;
    title: string;
    source: string;
  }>;
  onChange?: (data: { context_layers?: string[]; skills?: string[]; intelligence_items?: number[] }) => void;
}

export default function ContextInUsePanel({
  brief,
  intelligenceItems = [],
  onChange,
}: ContextInUsePanelProps) {
  const defaultContextLayers = brief?.context_layers_json ? JSON.parse(brief.context_layers_json) : [];
  const defaultSkills = brief?.skills_json ? JSON.parse(brief.skills_json) : [];
  const defaultIntelligenceItems = brief?.intelligence_items_json ? JSON.parse(brief.intelligence_items_json) : [];

  const [contextLayers, setContextLayers] = useState<string[]>(defaultContextLayers);
  const [skills, setSkills] = useState<string[]>(defaultSkills);
  const [intelligenceItemIds, setIntelligenceItemIds] = useState<number[]>(defaultIntelligenceItems);
  const [isRemoving, setIsRemoving] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRemoveContextLayer = useCallback(
    async (layer: string) => {
      if (!brief?.id) return;

      setIsRemoving(`layer-${layer}`);
      setError(null);

      try {
        const response = await fetch(`/api/briefs/${brief.id}/context-layers/${encodeURIComponent(layer)}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error('Failed to remove context layer');
        }

        const newLayers = contextLayers.filter((l) => l !== layer);
        setContextLayers(newLayers);
        onChange?.({ context_layers: newLayers, skills, intelligence_items: intelligenceItemIds });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to remove');
      } finally {
        setIsRemoving(null);
      }
    },
    [contextLayers, skills, intelligenceItemIds, brief?.id, onChange]
  );

  const handleRemoveSkill = useCallback(
    async (skill: string) => {
      if (!brief?.id) return;

      setIsRemoving(`skill-${skill}`);
      setError(null);

      try {
        const response = await fetch(`/api/briefs/${brief.id}/skills/${encodeURIComponent(skill)}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error('Failed to remove skill');
        }

        const newSkills = skills.filter((s) => s !== skill);
        setSkills(newSkills);
        onChange?.({ context_layers: contextLayers, skills: newSkills, intelligence_items: intelligenceItemIds });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to remove');
      } finally {
        setIsRemoving(null);
      }
    },
    [contextLayers, skills, intelligenceItemIds, brief?.id, onChange]
  );

  const handleRemoveIntelligenceItem = useCallback(
    async (itemId: number) => {
      if (!brief?.id) return;

      setIsRemoving(`item-${itemId}`);
      setError(null);

      try {
        const response = await fetch(`/api/briefs/${brief.id}/intelligence-items/${itemId}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error('Failed to remove intelligence item');
        }

        const newItems = intelligenceItemIds.filter((id) => id !== itemId);
        setIntelligenceItemIds(newItems);
        onChange?.({ context_layers: contextLayers, skills, intelligence_items: newItems });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to remove');
      } finally {
        setIsRemoving(null);
      }
    },
    [contextLayers, skills, intelligenceItemIds, brief?.id, onChange]
  );

  const isEmpty = contextLayers.length === 0 && skills.length === 0 && intelligenceItemIds.length === 0;

  return (
    <div className="p-3 border-t border-gray-200 flex-1 overflow-auto">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">📌 Context in Use</p>

      {isEmpty ? (
        <div className="space-y-2">
          <p className="text-xs text-gray-500 italic">No context added yet</p>
          <p className="text-xs text-gray-400">Add context layers, skills, or intelligence items to compose your prompt.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Context Layers */}
          {contextLayers.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1.5">Context Layers</p>
              <div className="space-y-1">
                {contextLayers.map((layer) => (
                  <div
                    key={layer}
                    className="flex items-center justify-between gap-2 text-xs bg-white border border-gray-200 rounded px-2 py-1.5 hover:border-gray-300 hover:bg-gray-50 transition-all group"
                  >
                    <span className="text-gray-700 truncate">{layer}</span>
                    <button
                      onClick={() => handleRemoveContextLayer(layer)}
                      disabled={isRemoving === `layer-${layer}`}
                      className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Remove context layer"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skills */}
          {skills.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1.5">Skills</p>
              <div className="space-y-1">
                {skills.map((skill) => (
                  <div
                    key={skill}
                    className="flex items-center justify-between gap-2 text-xs bg-white border border-gray-200 rounded px-2 py-1.5 hover:border-gray-300 hover:bg-gray-50 transition-all group"
                  >
                    <span className="text-gray-700 truncate">{skill}</span>
                    <button
                      onClick={() => handleRemoveSkill(skill)}
                      disabled={isRemoving === `skill-${skill}`}
                      className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Remove skill"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Intelligence Items */}
          {intelligenceItemIds.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1.5">Intelligence Items</p>
              <div className="space-y-1">
                {intelligenceItemIds.map((itemId) => {
                  const item = intelligenceItems.find((i) => i.id === itemId);
                  return (
                    <div
                      key={itemId}
                      className="flex items-center justify-between gap-2 text-xs bg-white border border-gray-200 rounded px-2 py-1.5 hover:border-gray-300 hover:bg-gray-50 transition-all group"
                    >
                      <span className="text-gray-700 truncate" title={item?.title}>
                        {item?.title || `Item #${itemId}`}
                      </span>
                      <button
                        onClick={() => handleRemoveIntelligenceItem(itemId)}
                        disabled={isRemoving === `item-${itemId}`}
                        className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Remove intelligence item"
                      >
                        ✕
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
        </div>
      )}
    </div>
  );
}
