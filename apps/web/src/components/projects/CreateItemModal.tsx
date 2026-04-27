'use client';

import { useState, useEffect } from 'react';

interface CreateItemModalProps {
  isOpen: boolean;
  type: 'folder' | 'deliverable';
  onClose: () => void;
  onCreate: (data: { name?: string; contentType?: string }) => Promise<void>;
  contentTypes?: string[];
  defaultContentType?: string;
}

const DEFAULT_CONTENT_TYPES = ['blog', 'email', 'press-release', 'case-study', 'whitepaper'];

export default function CreateItemModal({
  isOpen,
  type,
  onClose,
  onCreate,
  contentTypes = DEFAULT_CONTENT_TYPES,
  defaultContentType = 'blog',
}: CreateItemModalProps) {
  const [name, setName] = useState('');
  const [contentType, setContentType] = useState(defaultContentType);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      setName('');
      setContentType(defaultContentType);
      setError('');
    }
  }, [isOpen, defaultContentType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError(type === 'folder' ? 'Folder name is required' : 'Title is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await onCreate({
        name: name.trim(),
        contentType: type === 'deliverable' ? contentType : undefined,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to create ${type}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const title = type === 'folder' ? 'New Folder' : 'New Deliverable';
  const placeholder = type === 'folder' ? 'e.g., Q1 Content' : 'e.g., Product Launch Post';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white border rounded-lg shadow-lg w-96 max-w-full mx-4">
        <form onSubmit={handleSubmit}>
          <div className="border-b p-4">
            <h2 className="text-lg font-semibold">{title}</h2>
          </div>

          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {type === 'folder' ? 'Folder Name' : 'Title'}
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={placeholder}
                className="w-full px-3 py-2 border rounded bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-black"
                autoFocus
              />
            </div>

            {type === 'deliverable' && (
              <div>
                <label className="block text-sm font-medium mb-1">Content Type</label>
                <select
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  className="w-full px-3 py-2 border rounded bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-black"
                >
                  {contentTypes.map((ct) => (
                    <option key={ct} value={ct}>
                      {ct.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {error && <div className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</div>}
          </div>

          <div className="border-t p-4 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm border rounded hover:bg-gray-100"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm bg-black text-white rounded hover:bg-gray-900 disabled:opacity-50"
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
