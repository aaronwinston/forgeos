'use client';

import { useState, useEffect } from 'react';

interface TreeItemModalProps {
  isOpen: boolean;
  type: 'project' | 'folder' | 'subfolder' | 'deliverable';
  onClose: () => void;
  onCreate: (data: { name: string; contentType?: string; description?: string }) => Promise<void>;
}

const CONTENT_TYPES = [
  { value: 'blog', label: 'Blog post' },
  { value: 'email', label: 'Email' },
  { value: 'press-release', label: 'Press Release' },
  { value: 'case-study', label: 'Case Study' },
  { value: 'whitepaper', label: 'Whitepaper' },
];

export default function TreeItemModal({ isOpen, type, onClose, onCreate }: TreeItemModalProps) {
  const [name, setName] = useState('');
  const [contentType, setContentType] = useState('blog');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      setName('');
      setContentType('blog');
      setDescription('');
      setError('');
    }
  }, [isOpen]);

  const getTitle = () => {
    switch (type) {
      case 'project':
        return 'New project';
      case 'folder':
        return 'New folder';
      case 'subfolder':
        return 'New Subfolder';
      case 'deliverable':
        return 'New deliverable';
      default:
        return 'New Item';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError('Name is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await onCreate({
        name: name.trim(),
        contentType: type === 'deliverable' ? contentType : undefined,
        description: (type === 'project' || type === 'folder') ? description : undefined,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create item');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-bg-secondary border border-border rounded-card shadow-lg w-96 max-w-full mx-4">
        <form onSubmit={handleSubmit}>
          {/* Header */}
          <div className="border-b p-4">
            <h2 className="text-lg font-semibold">{getTitle()}</h2>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4">
            {/* Name field */}
            <div>
              <label className="block text-sm font-medium mb-1">
                {type === 'deliverable' ? 'Title' : 'Name'}
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={type === 'deliverable' ? 'e.g., My Blog Post' : 'e.g., Marketing Q1'}
                className="w-full px-3 py-2 border rounded bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                autoFocus
              />
            </div>

            {/* Content type field (for deliverables) */}
            {type === 'deliverable' && (
              <div>
                <label className="block text-sm font-medium mb-1">Content type</label>
                <select
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  className="w-full px-3 py-2 border rounded bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {CONTENT_TYPES.map((ct) => (
                    <option key={ct.value} value={ct.value}>
                      {ct.label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Description field (for projects and folders) */}
            {(type === 'project' || type === 'folder') && (
              <div>
                <label className="block text-sm font-medium mb-1">Description (optional)</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Add a description..."
                  className="w-full px-3 py-2 border rounded bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  rows={3}
                />
              </div>
            )}

            {/* Error message */}
            {error && <div className="text-sm text-destructive bg-destructive/10 p-2 rounded">{error}</div>}
          </div>

          {/* Footer */}
          <div className="border-t p-4 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm border rounded hover:bg-accent"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
