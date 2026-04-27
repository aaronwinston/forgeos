'use client';
import { useState } from 'react';

export function DocumentEditor({ output }: { output?: string }) {
  const [content, setContent] = useState(output || '');
  
  if (!output && !content) {
    return (
      <div className="border border-border rounded-card p-6 bg-bg-secondary text-center">
        <p className="text-sm text-fg-tertiary">Output will appear here once agents complete.</p>
      </div>
    );
  }
  
  return (
    <div className="border border-border rounded-card overflow-hidden bg-bg-secondary">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <h3 className="text-sm font-semibold text-fg-primary">Document</h3>
        <button
          onClick={() => navigator.clipboard.writeText(content)}
          className="text-xs text-fg-tertiary hover:text-fg-primary transition-colors"
        >
          Copy
        </button>
      </div>
      <textarea
        value={content}
        onChange={e => setContent(e.target.value)}
        className="w-full p-4 font-mono text-xs text-fg-primary bg-bg-secondary resize-none focus:outline-none min-h-64"
        rows={20}
        placeholder="Content will appear here..."
      />
    </div>
  );
}
