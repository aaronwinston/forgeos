'use client';
import { useState } from 'react';
import { getApiBase } from '@/lib/api';

interface WorkspaceProjectTreeProps {
  projects: Array<{
    id: number;
    name: string;
  }>;
  selectedDeliverableId?: number;
}

export default function WorkspaceProjectTree({ projects, selectedDeliverableId }: WorkspaceProjectTreeProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [folders, setFolders] = useState<Record<number, any[]>>({});

  const toggleProject = (projectId: number) => {
    const key = `project-${projectId}`;
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
    if (!expanded[key]) {
      fetchFolders(projectId);
    }
  };

  const fetchFolders = async (projectId: number) => {
    try {
      const res = await fetch(`${getApiBase()}/api/projects/${projectId}/folders`);
      if (res.ok) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const data: any = await res.json();
        setFolders(prev => ({ ...prev, [projectId]: data }));
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        data.forEach((f: any) => fetchDeliverables(f.id));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDeliverables = async (folderId: number) => {
    try {
      const res = await fetch(`${getApiBase()}/api/folders/${folderId}/deliverables`);
      if (res.ok) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const data: any = await res.json();
        setFolders(prev => {
          const updated = { ...prev };
          Object.keys(updated).forEach(projectId => {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            updated[parseInt(projectId)] = updated[parseInt(projectId)].map((f: any) =>
              f.id === folderId ? { ...f, deliverables: data } : f
            );
          });
          return updated;
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  const toggleFolder = (projectId: number, folderId: number) => {
    const key = `folder-${projectId}-${folderId}`;
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="h-full overflow-auto text-sm">
      {projects.map(project => (
        <div key={project.id} className="space-y-0">
          <button
            onClick={() => toggleProject(project.id)}
            className="w-full text-left px-2 py-2 hover:bg-gray-100 flex items-center gap-1 rounded transition-colors duration-150"
          >
            <span className="text-gray-400 select-none w-4 text-center flex-shrink-0">
              {expanded[`project-${project.id}`] ? '▼' : '▶'}
            </span>
            <span className="font-medium text-gray-900 flex-1 min-w-0 truncate">{project.name}</span>
          </button>

          {expanded[`project-${project.id}`] && folders[project.id] && (
            <div className="pl-4 space-y-0">
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {folders[project.id].map((folder: any) => (
                <div key={folder.id}>
                  <button
                    onClick={() => toggleFolder(project.id, folder.id)}
                    className="w-full text-left px-2 py-2 hover:bg-gray-100 flex items-center gap-1 rounded transition-colors duration-150"
                  >
                    <span className="text-gray-400 select-none w-4 text-center flex-shrink-0">
                      {expanded[`folder-${project.id}-${folder.id}`] ? '▼' : '▶'}
                    </span>
                    <span className="text-gray-700 flex-1 min-w-0 truncate">{folder.name}</span>
                  </button>

                  {expanded[`folder-${project.id}-${folder.id}`] && folder.deliverables && (
                    <div className="pl-4 space-y-0">
                      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                      {folder.deliverables.map((deliv: any) => (
                        <div
                          key={deliv.id}
                          className={`w-full text-left px-2 py-1.5 rounded flex items-center gap-2 transition-all duration-150 ${
                            selectedDeliverableId === deliv.id
                              ? 'bg-blue-100 text-blue-900 font-medium'
                              : 'hover:bg-gray-100 text-gray-700'
                          }`}
                        >
                          <span className="inline-block border rounded px-1 text-[10px] font-mono bg-gray-100 text-gray-700 flex-shrink-0">
                            {deliv.content_type}
                          </span>
                          <span className="flex-1 min-w-0 truncate">{deliv.title}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
