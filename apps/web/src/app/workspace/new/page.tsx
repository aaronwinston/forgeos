'use client';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function WorkspaceNewInner() {
  const router = useRouter();
  const params = useSearchParams();

  const contextItemId = params.get('context_item');
  const title = params.get('title') ?? 'New workspace';
  const sourceUrl = params.get('source_url');

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!contextItemId) {
      // No context item — just go to workspace root
      router.replace('/workspace');
      return;
    }

    async function createAndNavigate() {
      try {
        const res = await fetch(`${API_BASE}/api/workspace/from-briefing-item`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scrape_item_id: parseInt(contextItemId!),
            title: decodeURIComponent(title),
            content_type: 'blog',
          }),
        });

        if (!res.ok) {
          const msg = await res.text();
          throw new Error(`API error ${res.status}: ${msg}`);
        }

        const data = await res.json();
        router.replace(`/workspace/${data.deliverable_id}`);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to create workspace');
      }
    }

    createAndNavigate();
  }, [contextItemId, title, router]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4 bg-bg-primary">
        <p className="text-sm text-error max-w-md text-center">{error}</p>
        {sourceUrl && (
          <a
            href={decodeURIComponent(sourceUrl)}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-accent underline"
          >
            Open source article instead →
          </a>
        )}
        <button
          onClick={() => router.push('/dashboard')}
          className="text-xs text-fg-tertiary hover:text-fg-secondary mt-2"
        >
          ← Back to dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-screen gap-3 bg-bg-primary">
      <div className="w-5 h-5 rounded-full border-2 border-accent border-t-transparent animate-spin" />
      <p className="text-sm text-fg-secondary">Opening workspace…</p>
      {title && (
        <p className="text-xs text-fg-tertiary max-w-xs text-center truncate">
          {decodeURIComponent(title)}
        </p>
      )}
    </div>
  );
}

export default function WorkspaceNewPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen bg-bg-primary">
        <div className="w-5 h-5 rounded-full border-2 border-accent border-t-transparent animate-spin" />
      </div>
    }>
      <WorkspaceNewInner />
    </Suspense>
  );
}
