'use client';

import { useEffect, useState, useCallback } from 'react';
import { ChevronDown, ChevronRight, FileText, Folder } from 'lucide-react';
import { api } from '@/lib/api';
import { getApiBase } from '@/lib/api';

interface FileHealth {
  path: string;
  word_count: number;
  recommended: number;
  thinness_pct: number;
  badge: string;
}

interface HealthData {
  [path: string]: FileHealth;
}

interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: TreeNode[];
  isOpen?: boolean;
  health?: FileHealth;
}

interface EngineTreeWithHealthProps {
  selectedPath: string | null;
  onSelect: (path: string) => void;
}

export default function EngineTreeWithHealth({ selectedPath, onSelect }: EngineTreeWithHealthProps) {
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [health, setHealth] = useState<HealthData>({});
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['core', 'context', 'skills', 'playbooks', 'rubrics']));
  const [loading, setLoading] = useState(true);

  // Load health data
  useEffect(() => {
    async function loadHealth() {
      try {
        const result = await api.getEngineHealth();
        if (!('error' in result) && result.files) {
          const healthMap: HealthData = {};
          result.files.forEach((f: FileHealth) => {
            healthMap[f.path] = f;
          });
          setHealth(healthMap);
        }
      } catch (err) {
        console.error('[EngineTreeWithHealth] Error loading health:', err);
      }
    }

    loadHealth();
  }, []);

  const buildContextTree = useCallback((dir: string, files: string[]): TreeNode[] => {
    if (dir === 'context') {
      const grouped: Record<string, string[]> = {};
      files.forEach(f => {
        const match = f.match(/context\/(\d+_[^/]+)\//);
        if (match) {
          const layer = match[1];
          if (!grouped[layer]) grouped[layer] = [];
          grouped[layer].push(f);
        }
      });
      
      return Object.keys(grouped).sort().map(layer => ({
        name: layer,
        path: `context/${layer}`,
        type: 'folder' as const,
        children: grouped[layer].map(f => ({
          name: f.split('/').pop() || f,
          path: f,
          type: 'file' as const,
          health: health[f],
        })),
      }));
    }
    
    if (dir === 'skills') {
      const grouped: Record<string, string[]> = {};
      files.forEach(f => {
        const match = f.match(/skills\/([^/]+)\//);
        if (match) {
          const category = match[1];
          if (!grouped[category]) grouped[category] = [];
          grouped[category].push(f);
        }
      });
      
      return Object.keys(grouped).sort().map(category => ({
        name: category,
        path: `skills/${category}`,
        type: 'folder' as const,
        children: grouped[category].map(f => ({
          name: f.split('/').pop() || f,
          path: f,
          type: 'file' as const,
          health: health[f],
        })),
      }));
    }

    if (dir === 'rubrics') {
      const grouped: Record<string, string[]> = {};
      files.forEach(f => {
        const match = f.match(/rubrics\/([^/]+)\//);
        if (match) {
          const category = match[1];
          if (!grouped[category]) grouped[category] = [];
          grouped[category].push(f);
        }
      });
      
      return Object.keys(grouped).sort().map(category => ({
        name: category,
        path: `rubrics/${category}`,
        type: 'folder' as const,
        children: grouped[category].map(f => ({
          name: f.split('/').pop() || f,
          path: f,
          type: 'file' as const,
          health: health[f],
        })),
      }));
    }

    if (dir === 'core') {
      return files.map(f => ({
        name: f.split('/').pop() || f,
        path: f,
        type: 'file' as const,
        health: health[f],
      }));
    }

    return files.map(f => ({
      name: f.split('/').pop() || f,
      path: f,
      type: 'file' as const,
      health: health[f],
    }));
  }, [health]);

  useEffect(() => {
    async function loadTree() {
      try {
        const res = await fetch(`${getApiBase()}/api/files/tree`);
        if (!res.ok) throw new Error('Failed to load tree');
        const data = await res.json();

        const newTree: TreeNode[] = [
          {
            name: 'core',
            path: 'core',
            type: 'folder',
            children: buildContextTree('core', data.core || []),
          },
          {
            name: 'context',
            path: 'context',
            type: 'folder',
            children: buildContextTree('context', data.context || []),
          },
          {
            name: 'skills',
            path: 'skills',
            type: 'folder',
            children: buildContextTree('skills', data.skills || []),
          },
          {
            name: 'playbooks',
            path: 'playbooks',
            type: 'folder',
            children: buildContextTree('playbooks', data.playbooks || []),
          },
          {
            name: 'rubrics',
            path: 'rubrics',
            type: 'folder',
            children: buildContextTree('rubrics', data.rubrics || []),
          },
        ];

        setTree(newTree);
      } catch (err) {
        console.error('[EngineTree] Error loading tree:', err);
      } finally {
        setLoading(false);
      }
    }

    loadTree();
  }, [buildContextTree]);

  const toggleFolder = (path: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderNode = (node: TreeNode, depth: number = 0): React.ReactNode => {
    const isOpen = expanded.has(node.path);
    const isSelected = selectedPath === node.path;

    if (node.type === 'folder') {
      return (
        <div key={node.path}>
          <button
            onClick={() => toggleFolder(node.path)}
            className={`w-full flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-bg-tertiary rounded-sm transition ${
              isSelected ? 'bg-accent/10 text-accent' : 'text-fg-secondary'
            }`}
          >
            {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <Folder size={14} />
            <span className="font-medium">{node.name}</span>
          </button>
          {isOpen && node.children && (
            <div className="pl-2 border-l border-border/50">
              {node.children.map(child => renderNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    }

    const h = node.health;
    const badgeText = h ? (h.badge === 'placeholder' ? '🔴' : h.badge === 'thin' ? '🟡' : '🟢') : '⚪';

    return (
      <button
        key={node.path}
        onClick={() => onSelect(node.path)}
        className={`w-full flex items-center justify-between gap-2 px-3 py-1.5 text-sm hover:bg-bg-tertiary rounded-sm transition ${
          isSelected ? 'bg-accent/10 text-accent' : 'text-fg-secondary hover:text-fg-primary'
        }`}
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <FileText size={14} />
          <span className="truncate">{node.name}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {h && (
            <div className="flex items-center gap-1">
              <span title={`${h.word_count}/${h.recommended} words`} className="text-xs text-fg-tertiary">
                {Math.round(h.thinness_pct)}%
              </span>
              <span title={h.badge}>{badgeText}</span>
            </div>
          )}
        </div>
      </button>
    );
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-bg-secondary">
      <div className="p-3 border-b border-border">
        <h3 className="text-xs font-semibold text-fg-tertiary uppercase tracking-wide">Engine files</h3>
      </div>
      
      {loading ? (
        <div className="flex items-center justify-center h-32 text-fg-tertiary text-sm">
          Loading...
        </div>
      ) : (
        <div className="flex-1 overflow-auto">
          <div className="p-2 space-y-1">
            {tree.map(node => renderNode(node))}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="border-t border-border p-3 space-y-2 text-xs">
        <p className="text-fg-tertiary font-medium">Health</p>
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-fg-secondary">
            <span>🟢</span>
            <span>Complete (75%+)</span>
          </div>
          <div className="flex items-center gap-2 text-fg-secondary">
            <span>🟡</span>
            <span>Thin (25-75%)</span>
          </div>
          <div className="flex items-center gap-2 text-fg-secondary">
            <span>🔴</span>
            <span>Placeholder (&lt;25%)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
