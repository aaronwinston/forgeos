'use client';
import { useEffect, useState } from 'react';
import { api, getProjects, isApiError } from '@/lib/api';
import type { Project } from '@/lib/api';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import NewProjectModal from '@/components/projects/NewProjectModal';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false);
  
  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      console.debug('[Projects] Loading projects...');
      const data = await getProjects();
      setProjects(data);
      console.debug('[Projects] Loaded', data.length, 'projects');
    } catch (err) {
      const userMessage = 'Unable to load projects. Check that the API is running and try again.';
      setError(userMessage);
      console.error('[Projects] Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between gap-3 mb-6">
        <h1 className="text-2xl font-semibold text-fg-primary">Projects</h1>
        <Button onClick={() => setShowCreateProjectModal(true)}>+ New project</Button>
      </div>
      {error && (
        <div className="mb-6 border border-red-300 rounded-card p-4 bg-red-50">
          <p className="text-sm text-red-800 mb-2">{error}</p>
          <Button size="sm" onClick={load} variant="secondary">Retry</Button>
        </div>
      )}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : projects.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-fg-secondary text-sm mb-4">No projects yet. Create your first project to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {projects.map(p => (
            <Link key={p.id} href={`/projects/${p.id}`} className="block border border-border rounded-card p-4 bg-bg-secondary hover:border-brand-purple/30 transition-all group">
              <h3 className="text-sm font-semibold text-fg-primary group-hover:text-brand-purple transition-colors">{p.name}</h3>
              {p.description && <p className="text-xs text-fg-secondary mt-1">{p.description}</p>}
              {p.tracking && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  <span className="text-[11px] px-2 py-1 rounded-md bg-bg-tertiary text-fg-secondary">
                    {p.tracking.sites.length} sites
                  </span>
                  <span className="text-[11px] px-2 py-1 rounded-md bg-bg-tertiary text-fg-secondary">
                    {p.tracking.keywords.length} keywords
                  </span>
                  <span className="text-[11px] px-2 py-1 rounded-md bg-bg-tertiary text-fg-secondary">
                    {p.tracking.competitors.length} competitors
                  </span>
                  <span className="text-[11px] px-2 py-1 rounded-md bg-bg-tertiary text-fg-secondary">
                    {p.tracking.work_items.length} work items
                  </span>
                </div>
              )}
            </Link>
          ))}
        </div>
      )}

      <NewProjectModal
        isOpen={showCreateProjectModal}
        onClose={() => setShowCreateProjectModal(false)}
        onCreate={async (payload) => {
          const result = await api.createProject(payload);
          if (isApiError(result)) {
            throw new Error(result.details || 'Failed to create project');
          }
          await load();
          setShowCreateProjectModal(false);
        }}
      />
    </div>
  );
}
