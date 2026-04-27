'use client';
import { useState } from 'react';

export type UploadDestination =
  | 'messaging'
  | 'strategy'
  | 'voice'
  | 'project'
  | 'reference';

interface Option {
  value: UploadDestination;
  label: string;
  description: string;
  path: string;
}

const OPTIONS: Option[] = [
  {
    value: 'messaging',
    label: 'Company-wide messaging',
    description: 'Appended to messaging-framework.md',
    path: 'context/02_narrative/messaging-framework.md',
  },
  {
    value: 'strategy',
    label: 'Company-wide content strategy',
    description: 'Appended to content-strategy.md',
    path: 'context/03_strategy/content-strategy.md',
  },
  {
    value: 'voice',
    label: 'Voice / tone document',
    description: 'Appended to core/VOICE.md',
    path: 'core/VOICE.md',
  },
  {
    value: 'project',
    label: 'Project-specific',
    description: 'Saved to context/projects/<project>/<filename>.md',
    path: 'context/projects/...',
  },
  {
    value: 'reference',
    label: 'Just store as reference',
    description: 'Saved to context/uploads/<filename>.md',
    path: 'context/uploads/...',
  },
];

interface UploadDestinationModalProps {
  filename: string;
  onConfirm: (destination: UploadDestination, projectId?: string) => void;
  onCancel: () => void;
  uploading?: boolean;
}

export default function UploadDestinationModal({
  filename,
  onConfirm,
  onCancel,
  uploading = false,
}: UploadDestinationModalProps) {
  const [selected, setSelected] = useState<UploadDestination>('reference');
  const [projectId, setProjectId] = useState('');

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-bg-secondary border border-border rounded-card shadow-xl w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        <div className="p-6 border-b border-border">
          <h2 className="text-base font-semibold text-fg-primary">Where should this go?</h2>
          <p className="text-xs text-fg-tertiary mt-1 truncate">
            <span className="font-mono">{filename}</span>
          </p>
        </div>

        <div className="p-4 space-y-2">
          {OPTIONS.map((opt) => (
            <label
              key={opt.value}
              className={`flex gap-3 p-3 rounded-input cursor-pointer border transition-colors ${
                selected === opt.value
                  ? 'border-accent bg-accent/5'
                  : 'border-border hover:border-border/80 hover:bg-bg-tertiary'
              }`}
            >
              <input
                type="radio"
                name="destination"
                value={opt.value}
                checked={selected === opt.value}
                onChange={() => setSelected(opt.value)}
                className="mt-0.5 accent-[var(--accent)]"
              />
              <div className="min-w-0">
                <p className="text-sm font-medium text-fg-primary">{opt.label}</p>
                <p className="text-xs text-fg-tertiary">{opt.path}</p>
              </div>
            </label>
          ))}

          {selected === 'project' && (
            <div className="mt-2 pl-1">
              <label className="block text-xs text-fg-secondary mb-1">Project ID or slug</label>
              <input
                type="text"
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                placeholder="e.g. series-x-launch"
                className="w-full text-sm border border-border rounded-input px-3 py-2 bg-bg-tertiary text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:border-accent"
              />
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border flex justify-end gap-2">
          <button
            onClick={onCancel}
            disabled={uploading}
            className="px-4 py-2 text-sm text-fg-secondary bg-bg-tertiary border border-border rounded-input hover:bg-bg-tertiary/80 font-medium disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={() => onConfirm(selected, selected === 'project' ? projectId : undefined)}
            disabled={uploading || (selected === 'project' && !projectId.trim())}
            className="px-4 py-2 text-sm text-white bg-accent rounded-input hover:bg-accent/90 font-medium disabled:opacity-50"
          >
            {uploading ? 'Uploading…' : 'Upload'}
          </button>
        </div>
      </div>
    </div>
  );
}
