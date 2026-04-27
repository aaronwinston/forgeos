'use client';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { getApiBase } from '@/lib/api';
import type { SearchInsight, Project, Folder } from '@/lib/types';

interface StartInsightModalProps {
  isOpen: boolean;
  onClose: () => void;
  insight: SearchInsight;
}

export default function StartInsightModal({ isOpen, onClose, insight }: StartInsightModalProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [title, setTitle] = useState(insight.topic || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadProjects();
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedProject) {
      loadFolders(selectedProject);
    }
  }, [selectedProject]);

  const loadProjects = async () => {
    try {
      const response = await fetch(`${getApiBase()}/api/projects`);
      if (!response.ok) throw new Error('Failed to load projects');
      const data = await response.json();
      setProjects(data);
      if (data.length > 0) {
        setSelectedProject(data[0].id);
      }
    } catch (err) {
      setError('Failed to load projects');
      console.error(err);
    }
  };

  const loadFolders = async (projectId: number) => {
    try {
      const response = await fetch(`${getApiBase()}/api/projects/${projectId}/folders`);
      if (!response.ok) throw new Error('Failed to load folders');
      const data = await response.json();
      setFolders(data);
      if (data.length > 0) {
        setSelectedFolder(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load folders:', err);
    }
  };

  const handleCreateDeliverable = async () => {
    if (!selectedFolder || !title) {
      setError('Please select a folder and enter a title');
      return;
    }

    setLoading(true);
    try {
      // Create a new deliverable with the insight context
      const response = await fetch(`${getApiBase()}/api/deliverables`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          folder_id: selectedFolder,
          title,
          content_type: 'blog',
          status: 'draft',
          metadata_json: JSON.stringify({
            search_insight: insight,
            source_insight_topic: insight.topic,
          }),
        }),
      });

      if (!response.ok) throw new Error('Failed to create deliverable');

      await response.json();
      alert(`Created deliverable "${title}" with insight context`);
      onClose();
    } catch (err) {
      setError('Failed to create deliverable. Try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">Start brief from insight</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Topic</label>
              <p className="text-sm text-fg-secondary bg-gray-50 rounded p-2">{insight.topic}</p>
            </div>

            <div>
              <label htmlFor="title" className="block text-sm font-medium mb-1">
                Deliverable title
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full border rounded-input px-3 py-2 text-sm"
                placeholder="e.g., Blog post on LLM evaluation"
              />
            </div>

            <div>
              <label htmlFor="project" className="block text-sm font-medium mb-1">
                Project
              </label>
              <select
                id="project"
                value={selectedProject || ''}
                onChange={(e) => setSelectedProject(Number(e.target.value))}
                className="w-full border rounded-input px-3 py-2 text-sm"
              >
                <option value="">Select a project</option>
                {projects.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            {folders.length > 0 && (
              <div>
                <label htmlFor="folder" className="block text-sm font-medium mb-1">
                  Folder
                </label>
                <select
                  id="folder"
                  value={selectedFolder || ''}
                  onChange={(e) => setSelectedFolder(Number(e.target.value))}
                  className="w-full border rounded-input px-3 py-2 text-sm"
                >
                  <option value="">Select a folder</option>
                  {folders.map(f => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              </div>
            )}

            {error && (
              <div className="border border-red-300 rounded-input p-2 bg-red-50">
                <p className="text-xs text-red-800">{error}</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex gap-2 p-4 border-t">
          <Button
            variant="secondary"
            size="sm"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleCreateDeliverable}
            loading={loading}
            disabled={!title || !selectedFolder}
          >
            Create brief
          </Button>
        </div>
      </div>
    </div>
  );
}
