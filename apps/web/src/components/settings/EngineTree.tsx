'use client';

import { useEffect, useState, useCallback } from 'react';
import { ChevronDown, ChevronRight, FileText, Folder } from 'lucide-react';
import { getApiBase } from '@/lib/api';

interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: TreeNode[];
  isOpen?: boolean;
}

interface EngineTreeProps {
  selectedPath: string | null;
  onSelect: (path: string) => void;
}

export default function EngineTree({ selectedPath, onSelect }: EngineTreeProps) {
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['core', 'context', 'skills', 'playbooks', 'rubrics']));

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
        })),
      }));
    }

    return files.map(f => ({
      name: f.split('/').pop() || f,
      path: f,
      type: 'file' as const,
    }));
  }, []);

  const buildTree = useCallback((fileTree: Record<string, string[]>): TreeNode[] => {
    const dirs = ['core', 'context', 'skills', 'playbooks', 'rubrics'];
    
    return dirs.map(dir => {
      const files = fileTree[dir] || [];
      const children = buildContextTree(dir, files);
      
      return {
        name: dir,
        path: dir,
        type: 'folder' as const,
        children,
        isOpen: true,
      };
    });
  }, [buildContextTree]);

  useEffect(() => {
    fetch(`${getApiBase()}/api/files/tree`)
      .then(r => r.json())
      .then((fileTree: Record<string, string[]>) => {
        const nodes = buildTree(fileTree);
        setTree(nodes);
      })
      .catch(console.error);
  }, [buildTree]);

  function toggleExpanded(path: string) {
    const newExpanded = new Set(expanded);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpanded(newExpanded);
  }

  function renderTree(nodes: TreeNode[], depth = 0): JSX.Element {
    return (
      <>
        {nodes.map(node => (
          <div key={node.path}>
            <div className={`flex items-center gap-1 px-2 py-1 hover:bg-gray-100 rounded cursor-pointer text-sm`}
              style={{ paddingLeft: `${depth * 16 + 8}px` }}
              onClick={() => {
                if (node.type === 'folder') {
                  toggleExpanded(node.path);
                } else {
                  onSelect(node.path);
                }
              }}
            >
              {node.type === 'folder' ? (
                <>
                  {expanded.has(node.path) ? (
                    <ChevronDown size={16} className="flex-shrink-0" />
                  ) : (
                    <ChevronRight size={16} className="flex-shrink-0" />
                  )}
                  <Folder size={14} className="flex-shrink-0 text-amber-600" />
                  <span className="font-medium">{node.name}</span>
                </>
              ) : (
                <>
                  <div className="w-4" />
                  <FileText size={14} className={`flex-shrink-0 ${selectedPath === node.path ? 'text-blue-600' : 'text-gray-400'}`} />
                  <span className={selectedPath === node.path ? 'font-semibold text-blue-700' : ''}>{node.name}</span>
                </>
              )}
            </div>
            {node.type === 'folder' && node.children && expanded.has(node.path) && (
              renderTree(node.children, depth + 1)
            )}
          </div>
        ))}
      </>
    );
  }

  return (
    <div className="w-80 flex-shrink-0 border-r bg-gray-50 overflow-auto h-full">
      <div className="p-4 border-b sticky top-0 bg-white">
        <h2 className="text-sm font-bold text-gray-900">Engine structure</h2>
      </div>
      <div className="p-2">
        {renderTree(tree)}
      </div>
    </div>
  );
}
