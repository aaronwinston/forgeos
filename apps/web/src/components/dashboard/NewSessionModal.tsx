'use client';
import { useState } from 'react';
import { createSession } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { useRouter } from 'next/navigation';

interface NewSessionModalProps {
  onClose: () => void;
  onCreated?: () => void;
}

export function NewSessionModal({ onClose, onCreated }: NewSessionModalProps) {
  const router = useRouter();
  const [form, setForm] = useState({ title: '', type: 'blog', audience: '', description: '' });
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setLoading(true);
    const result = await createSession(form);
    setLoading(false);
    if ('id' in result) {
      onCreated?.();
      router.push(`/sessions/${result.id}`);
    }
    onClose();
  };
  
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-bg-secondary border border-border rounded-2xl w-full max-w-md shadow-xl" onClick={e => e.stopPropagation()}>
        <div className="p-6 border-b border-border">
          <h2 className="text-lg font-semibold text-fg-primary">New session</h2>
          <p className="text-sm text-fg-secondary mt-1">Start a new AI-powered content session</p>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="text-xs font-medium text-fg-secondary block mb-1.5">Title *</label>
            <input
              type="text"
              required
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              placeholder="e.g. Q3 launch blog post"
              className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-bg-primary text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-2 focus:ring-brand-purple/30 focus:border-brand-purple/50"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-fg-secondary block mb-1.5">Type</label>
            <select
              value={form.type}
              onChange={e => setForm(f => ({ ...f, type: e.target.value }))}
              className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-bg-primary text-fg-primary focus:outline-none focus:ring-2 focus:ring-brand-purple/30"
            >
              <option value="blog">Blog post</option>
              <option value="email">Email</option>
              <option value="social">Social</option>
              <option value="launch">Launch</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-fg-secondary block mb-1.5">Audience</label>
            <input
              type="text"
              value={form.audience}
              onChange={e => setForm(f => ({ ...f, audience: e.target.value }))}
              placeholder="e.g. ML engineers, marketing leaders"
              className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-bg-primary text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-2 focus:ring-brand-purple/30"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-fg-secondary block mb-1.5">Description / Brief</label>
            <textarea
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              placeholder="What should this content accomplish?"
              rows={3}
              className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-bg-primary text-fg-primary placeholder:text-fg-tertiary focus:outline-none focus:ring-2 focus:ring-brand-purple/30 resize-none"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={onClose} className="flex-1">Cancel</Button>
            <Button type="submit" loading={loading} className="flex-1">Create Session</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
