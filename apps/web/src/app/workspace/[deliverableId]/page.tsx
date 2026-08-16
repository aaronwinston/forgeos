'use client';
import { useEffect, useState } from 'react';
import WorkspaceLayout from '@/components/workspace/WorkspaceLayout';
import { getApiBase } from '@/lib/api';
import ErrorBoundary from '@/components/ErrorBoundary';

interface WorkspacePageProps {
  params: Promise<{ deliverableId: string }>;
}

export default function WorkspacePage({ params }: WorkspacePageProps) {
  const [deliverableId, setDeliverableId] = useState<number | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [deliverable, setDeliverable] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [brief, setBrief] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [projects, setProjects] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [folder, setFolder] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Handle params Promise in Next.js 15
  useEffect(() => {
    params.then(({ deliverableId: id }) => setDeliverableId(parseInt(id)));
  }, [params]);

  useEffect(() => {
    if (deliverableId === null) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch deliverable data
        const delivRes = await fetch(`${getApiBase()}/api/deliverables/${deliverableId}`);
        if (!delivRes.ok) throw new Error('Failed to fetch deliverable');
        const delivData = await delivRes.json();
        setDeliverable(delivData);

        // Fetch folder info for breadcrumb
        const folderRes = await fetch(`${getApiBase()}/api/folders/${delivData.folder_id}`);
        if (folderRes.ok) {
          const folderData = await folderRes.json();
          setFolder(folderData);
          // Get project info from folder
          const projRes = await fetch(`${getApiBase()}/api/projects/${folderData.project_id}`);
          if (projRes.ok) {
            const projData = await projRes.json();
            setProject(projData);
          }
        }

        // Fetch brief for this deliverable
        const briefRes = await fetch(`${getApiBase()}/api/deliverables/${deliverableId}/brief`);
        if (briefRes.ok) {
          const briefData = await briefRes.json();
          setBrief(briefData);
        }

        // Fetch all projects for the tree
        const projRes = await fetch(`${getApiBase()}/api/projects`);
        if (!projRes.ok) throw new Error('Failed to fetch projects');
        const projData = await projRes.json();
        setProjects(projData);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'An error occurred');
        console.error(e);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [deliverableId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen w-screen">
        <p className="text-sm text-gray-500">Loading workspace...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen w-screen">
        <p className="text-sm text-red-500">Error: {error}</p>
      </div>
    );
  }

  if (!deliverable) {
    return (
      <div className="flex items-center justify-center h-screen w-screen">
        <p className="text-sm text-gray-500">Deliverable not found</p>
      </div>
    );
  }

  const workspaceFallback = (error: Error, reset: () => void) => (
    <div className="flex flex-col items-center justify-center h-screen gap-4 p-8">
      <h2 className="text-xl font-semibold text-red-600">Workspace failed to load</h2>
      <p className="text-sm text-gray-500">{error.message}</p>
      <div className="flex gap-3">
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Try again
        </button>
        <a
          href="/dashboard"
          className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
        >
          Back to dashboard
        </a>
      </div>
    </div>
  );

  return (
    <ErrorBoundary fallback={workspaceFallback}>
      <WorkspaceLayout
        deliverable={deliverable}
        brief={brief}
        projects={projects}
        folder={folder}
        project={project}
      />
    </ErrorBoundary>
  );
}
