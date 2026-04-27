'use client';
import { useState, useRef, DragEvent, ChangeEvent } from 'react';

interface UploadZoneProps {
  onUpload: (file: File) => void;
}

const ACCEPTED = ['.md', '.txt', '.pdf', '.docx'];
const ACCEPTED_MIME = [
  'text/markdown',
  'text/plain',
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

function isAccepted(file: File) {
  const name = file.name.toLowerCase();
  return ACCEPTED.some(ext => name.endsWith(ext)) || ACCEPTED_MIME.includes(file.type);
}

export default function UploadZone({ onUpload }: UploadZoneProps) {
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    if (!isAccepted(file)) {
      setError(`Unsupported file type. Accepted: ${ACCEPTED.join(', ')}`);
      return;
    }
    setError(null);
    onUpload(file);
  }

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!isAccepted(file)) {
      setError(`Unsupported file type. Accepted: ${ACCEPTED.join(', ')}`);
      return;
    }
    setError(null);
    onUpload(file);
    // Reset so the same file can be re-uploaded
    e.target.value = '';
  }

  return (
    <div className="space-y-2">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex flex-col items-center justify-center gap-2 border-2 border-dashed rounded-card p-8 cursor-pointer transition-colors ${
          dragging
            ? 'border-accent bg-accent/5'
            : 'border-border hover:border-accent/50 hover:bg-bg-tertiary'
        }`}
      >
        <span className="text-2xl">📄</span>
        <p className="text-sm text-fg-primary font-medium">Drop a file here, or click to browse</p>
        <p className="text-xs text-fg-tertiary">{ACCEPTED.join(', ')} supported</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED.join(',')}
          onChange={handleChange}
          className="sr-only"
        />
      </div>
      {error && <p className="text-xs text-error">{error}</p>}
    </div>
  );
}
