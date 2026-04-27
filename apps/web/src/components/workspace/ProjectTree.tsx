'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import TreeItemModal from './TreeItemModal';

export interface Deliverable {
  id: number;
  folder_id: number;
  content_type: string;
  title: string;
  status: 'draft' | 'active' | 'published';
  body_md?: string;
  metadata_json?: string;
  created_at: string;
  updated_at: string;
}

export interface Folder {
  id: number;
  project_id: number;
  parent_folder_id?: number;
  name: string;
  created_at: string;
  deliverables?: Deliverable[];
  subfolders?: Folder[];
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  folders?: Folder[];
}

type TreeItemType = 'project' | 'folder' | 'subfolder' | 'deliverable';

interface ContextMenuState {
  x: number;
  y: number;
  itemType: TreeItemType;
  itemId: number;
  itemParentId?: number;
}

interface SelectedItem {
  type: TreeItemType;
  id: number;
  parentId?: number;
}

export default function ProjectTree() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [expandedFolders, setExpandedFolders] = useState<Set<number>>(new Set());
  const [selectedItem, setSelectedItem] = useState<SelectedItem | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalState, setModalState] = useState<{
    isOpen: boolean;
    type: TreeItemType;
    parentId?: number;
  }>({ isOpen: false, type: 'project' });

  const contextMenuRef = useRef<HTMLDivElement>(null);
  const treeRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Build flat list of all visible tree items for keyboard navigation
  const getVisibleItems = useCallback(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const items: Array<{ type: TreeItemType; id: number; parentId?: number; object?: any }> = [];

    projects.forEach((project) => {
      items.push({ type: 'project', id: project.id, object: project });

      if (expandedFolders.has(project.id)) {
        project.folders?.forEach((folder) => {
          items.push({ type: 'folder', id: folder.id, parentId: project.id, object: folder });

          if (expandedFolders.has(folder.id)) {
            folder.subfolders?.forEach((subfolder) => {
              items.push({ type: 'subfolder', id: subfolder.id, parentId: folder.id, object: subfolder });

              if (expandedFolders.has(subfolder.id)) {
                subfolder.deliverables?.forEach((deliv) => {
                  items.push({ type: 'deliverable', id: deliv.id, parentId: subfolder.id, object: deliv });
                });
              }
            });

            folder.deliverables?.forEach((deliv) => {
              items.push({ type: 'deliverable', id: deliv.id, parentId: folder.id, object: deliv });
            });
          }
        });
      }
    });

    return items;
  }, [projects, expandedFolders]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!treeRef.current?.contains(document.activeElement as Node) && document.activeElement !== searchInputRef.current) {
        return;
      }

      const visibleItems = getVisibleItems();
      const currentIndex = selectedItem
        ? visibleItems.findIndex((item) => item.type === selectedItem.type && item.id === selectedItem.id)
        : -1;

      switch (e.key) {
        case 'ArrowUp': {
          e.preventDefault();
          if (currentIndex > 0) {
            const item = visibleItems[currentIndex - 1];
            setSelectedItem({ type: item.type, id: item.id, parentId: item.parentId });
          } else if (visibleItems.length > 0) {
            const item = visibleItems[visibleItems.length - 1];
            setSelectedItem({ type: item.type, id: item.id, parentId: item.parentId });
          }
          break;
        }
        case 'ArrowDown': {
          e.preventDefault();
          if (currentIndex < visibleItems.length - 1) {
            const item = visibleItems[currentIndex + 1];
            setSelectedItem({ type: item.type, id: item.id, parentId: item.parentId });
          } else if (visibleItems.length > 0) {
            const item = visibleItems[0];
            setSelectedItem({ type: item.type, id: item.id, parentId: item.parentId });
          }
          break;
        }
        case 'ArrowLeft': {
          e.preventDefault();
          if (selectedItem && (selectedItem.type === 'project' || selectedItem.type === 'folder' || selectedItem.type === 'subfolder')) {
            if (expandedFolders.has(selectedItem.id)) {
              toggleFolder(selectedItem.id);
            }
          }
          break;
        }
        case 'ArrowRight': {
          e.preventDefault();
          if (selectedItem && (selectedItem.type === 'project' || selectedItem.type === 'folder' || selectedItem.type === 'subfolder')) {
            if (!expandedFolders.has(selectedItem.id)) {
              toggleFolder(selectedItem.id);
            }
          }
          break;
        }
        case 'Enter': {
          e.preventDefault();
          if (selectedItem) {
            if (selectedItem.type === 'deliverable') {
              handleDeliverableClick(visibleItems.find((i) => i.id === selectedItem.id)?.object as Deliverable);
            } else if (selectedItem.type === 'project' || selectedItem.type === 'folder' || selectedItem.type === 'subfolder') {
              toggleFolder(selectedItem.id);
            }
          }
          break;
        }
        case 'Escape': {
          e.preventDefault();
          if (searchTerm) {
            setSearchTerm('');
          } else {
            setSelectedItem(null);
          }
          break;
        }
        case 'n': {
          if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
            e.preventDefault();
            openCreateModal('project');
            setSelectedItem(null);
          }
          break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedItem, expandedFolders, projects, searchTerm, getVisibleItems]);

  // Load projects with nested structure
  const loadProjects = useCallback(async () => {
    setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result: any = await api.getProjects();
      if (Array.isArray(result)) {
        // Enrich projects with folder and deliverable data
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const enrichedProjects: any[] = await Promise.all(
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          result.map(async (project: any) => {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const foldersResult: any = await api.getFolders(project.id);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const folders: any[] = Array.isArray(foldersResult) ? foldersResult : [];

            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const enrichedFolders: any[] = await Promise.all(
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              folders.map(async (folder: any) => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const deliverableResult: any = await api.getDeliverables(folder.id);
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const deliverables: any[] = Array.isArray(deliverableResult) ? deliverableResult : [];
                return { ...folder, deliverables };
              })
            );

            return { ...project, folders: enrichedFolders };
          })
        );
        setProjects(enrichedProjects);
      }
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  // Close context menu on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (contextMenuRef.current && !contextMenuRef.current.contains(e.target as Node)) {
        setContextMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const toggleFolder = (folderId: number) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(folderId)) {
        next.delete(folderId);
      } else {
        next.add(folderId);
      }
      return next;
    });
  };

  const handleDeliverableClick = useCallback((deliverable: Deliverable) => {
    router.push(`/deliverables/${deliverable.id}`);
  }, [router]);

  const handleContextMenu = (
    e: React.MouseEvent,
    itemType: TreeItemType,
    itemId: number,
    parentId?: number
  ) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({ x: e.clientX, y: e.clientY, itemType, itemId, itemParentId: parentId });
  };

  const handleDeleteProject = async (projectId: number) => {
    if (confirm('Delete this project and all its contents?')) {
      try {
        const deleteApi = api.deleteProject || (async (id: number) => {
          const result = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
          return result.ok;
        });
        await deleteApi(projectId);
        await loadProjects();
      } catch (error) {
        console.error('Error deleting project:', error);
      }
    }
  };

  const handleDeleteFolder = async (folderId: number) => {
    if (confirm('Delete this folder and all its contents?')) {
      try {
        const deleteApi = api.deleteFolder || (async (id: number) => {
          const result = await fetch(`/api/folders/${id}`, { method: 'DELETE' });
          return result.ok;
        });
        await deleteApi(folderId);
        await loadProjects();
      } catch (error) {
        console.error('Error deleting folder:', error);
      }
    }
  };

  const handleDeleteDeliverable = async (deliverableId: number) => {
    if (confirm('Delete this deliverable?')) {
      try {
        const deleteApi = api.deleteDeliverable || (async (id: number) => {
          const result = await fetch(`/api/deliverables/${id}`, { method: 'DELETE' });
          return result.ok;
        });
        await deleteApi(deliverableId);
        await loadProjects();
      } catch (error) {
        console.error('Error deleting deliverable:', error);
      }
    }
  };

  const openCreateModal = (type: TreeItemType, parentId?: number) => {
    setModalState({ isOpen: true, type, parentId });
    setContextMenu(null);
  };

  const handleCreateItem = async (itemData: {
    name: string;
    contentType?: string;
    description?: string;
  }) => {
    try {
      if (modalState.type === 'project') {
        await api.createProject({ name: itemData.name, description: itemData.description });
      } else if (modalState.type === 'folder' && modalState.parentId) {
        await api.createFolder({
          project_id: modalState.parentId,
          name: itemData.name,
          parent_folder_id: null,
        });
      } else if (modalState.type === 'subfolder' && modalState.parentId) {
        const parentProject = projects.find((p) =>
          p.folders?.some((f) => f.id === modalState.parentId)
        );
        await api.createFolder({
          project_id: parentProject?.id,
          name: itemData.name,
          parent_folder_id: modalState.parentId,
        });
      } else if (modalState.type === 'deliverable' && modalState.parentId) {
        await api.createDeliverable({
          folder_id: modalState.parentId,
          content_type: itemData.contentType || 'blog',
          title: itemData.name,
        });
      }

      await loadProjects();
      setModalState({ isOpen: false, type: 'project' });
    } catch (error) {
      console.error('Error creating item:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return '#999';
      case 'active':
        return '#22c55e';
      case 'published':
        return '#3b82f6';
      default:
        return '#999';
    }
  };

  const getContentTypeBadgeColor = (contentType: string) => {
    const colors: Record<string, string> = {
      blog: 'bg-blue-100 text-blue-800',
      email: 'bg-purple-100 text-purple-800',
      'press-release': 'bg-red-100 text-red-800',
      'case-study': 'bg-green-100 text-green-800',
      whitepaper: 'bg-gray-100 text-gray-800',
    };
    return colors[contentType] || 'bg-gray-100 text-gray-800';
  };

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderDeliverable = (deliverable: Deliverable) => {
    const statusColor = getStatusColor(deliverable.status);
    const badgeColor = getContentTypeBadgeColor(deliverable.content_type);
    const isSelected = selectedItem?.type === 'deliverable' && selectedItem?.id === deliverable.id;

    return (
      <div
        key={`del-${deliverable.id}`}
        className={`ml-12 py-1 px-2 text-sm rounded cursor-pointer flex items-center justify-between group ${
          isSelected ? 'bg-primary/20 border-l-2 border-primary' : 'hover:bg-accent/50'
        }`}
        onClick={() => {
          handleDeliverableClick(deliverable);
          setSelectedItem({ type: 'deliverable', id: deliverable.id, parentId: deliverable.folder_id });
        }}
        onContextMenu={(e) => handleContextMenu(e, 'deliverable', deliverable.id, deliverable.folder_id)}
      >
        <span className="flex items-center gap-2 flex-1">
          <span
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: statusColor }}
            title={deliverable.status}
          />
          <span className="truncate">{deliverable.title}</span>
          <span className={`text-xs px-2 py-0.5 rounded font-medium ${badgeColor}`}>
            {deliverable.content_type}
          </span>
        </span>
        <button
          className="opacity-0 group-hover:opacity-100 text-xs text-muted-foreground hover:text-foreground"
          onClick={(e) => {
            e.stopPropagation();
            handleContextMenu(e, 'deliverable', deliverable.id, deliverable.folder_id);
          }}
        >
          ⋮
        </button>
      </div>
    );
  };

  const renderFolder = (folder: Folder, depth: number = 1) => {
    const isExpanded = expandedFolders.has(folder.id);
    const marginLeft = depth * 12;
    const folderType = depth === 1 ? 'folder' : 'subfolder';
    const isSelected = selectedItem?.type === folderType && selectedItem?.id === folder.id;

    return (
      <div key={`folder-${folder.id}`}>
        <div
          className={`py-1 px-2 text-sm rounded flex items-center gap-2 group cursor-pointer ${
            isSelected ? 'bg-primary/20 border-l-2 border-primary' : 'hover:bg-accent/50'
          }`}
          style={{ marginLeft: `${marginLeft}px` }}
          onClick={() => setSelectedItem({ type: folderType, id: folder.id, parentId: folder.project_id })}
          onContextMenu={(e) => handleContextMenu(e, folderType, folder.id, folder.project_id)}
        >
          <span
            className="text-xs cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              toggleFolder(folder.id);
            }}
          >
            {isExpanded ? '▼' : '▶'}
          </span>
          <span>{folder.name}</span>
          <button
            className="opacity-0 group-hover:opacity-100 text-xs text-muted-foreground hover:text-foreground"
            onClick={(e) => {
              e.stopPropagation();
              handleContextMenu(e, folderType, folder.id, folder.project_id);
            }}
          >
            ⋮
          </button>
        </div>

        {isExpanded && (
          <>
            {folder.subfolders?.map((subfolder) => renderFolder(subfolder, depth + 1))}
            {folder.deliverables?.map((deliverable) => renderDeliverable(deliverable))}
          </>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-background" ref={treeRef}>
      {/* Search input */}
      <div className="p-3 border-b">
        <input
          ref={searchInputRef}
          type="text"
          placeholder="Search projects..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-2 py-1 text-sm border rounded bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Projects list */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-sm text-muted-foreground">Loading...</div>
        ) : filteredProjects.length === 0 ? (
          <div className="p-4 text-sm text-muted-foreground">No projects found</div>
        ) : (
          filteredProjects.map((project) => {
            const isExpanded = expandedFolders.has(project.id);
            const isSelected = selectedItem?.type === 'project' && selectedItem?.id === project.id;

            return (
              <div key={`proj-${project.id}`}>
                <div
                  className={`py-1 px-2 text-sm rounded flex items-center gap-2 group cursor-pointer mx-2 mt-1 ${
                    isSelected ? 'bg-primary/20 border-l-2 border-primary' : 'hover:bg-accent/50'
                  }`}
                  onClick={() => setSelectedItem({ type: 'project', id: project.id })}
                  onContextMenu={(e) => handleContextMenu(e, 'project', project.id)}
                >
                  <span
                    className="text-xs cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFolder(project.id);
                    }}
                  >
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span className="font-medium">{project.name}</span>
                  <button
                    className="opacity-0 group-hover:opacity-100 text-xs text-muted-foreground hover:text-foreground"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleContextMenu(e, 'project', project.id);
                    }}
                  >
                    ⋮
                  </button>
                </div>

                {isExpanded && (
                  <>
                    {project.folders?.map((folder) => renderFolder(folder))}
                    {(!project.folders || project.folders.length === 0) && (
                      <div className="ml-6 py-1 px-2 text-xs text-muted-foreground">
                        No folders yet
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* New project button */}
      <div className="p-3 border-t">
        <button
          className="w-full text-left px-2 py-1.5 text-xs text-muted-foreground hover:text-foreground hover:bg-accent/50 rounded"
          onClick={() => openCreateModal('project')}
        >
          + New project
        </button>
      </div>

      {/* Context menu */}
      {contextMenu && (
        <div
          ref={contextMenuRef}
          className="fixed bg-popover border rounded shadow-lg z-50"
          style={{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }}
        >
          {contextMenu.itemType === 'project' && (
            <>
              <button
                className="block w-full text-left px-4 py-2 text-sm hover:bg-accent cursor-pointer whitespace-nowrap"
                onClick={() => openCreateModal('folder', contextMenu.itemId)}
              >
                New folder
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm hover:bg-accent cursor-pointer whitespace-nowrap text-destructive"
                onClick={() => {
                  handleDeleteProject(contextMenu.itemId);
                  setContextMenu(null);
                }}
              >
                Delete
              </button>
            </>
          )}

          {(contextMenu.itemType === 'folder' || contextMenu.itemType === 'subfolder') && (
            <>
              <button
                className="block w-full text-left px-4 py-2 text-sm hover:bg-accent cursor-pointer whitespace-nowrap"
                onClick={() => openCreateModal('subfolder', contextMenu.itemId)}
              >
                New subfolder
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm hover:bg-accent cursor-pointer whitespace-nowrap"
                onClick={() => openCreateModal('deliverable', contextMenu.itemId)}
              >
                New deliverable
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm hover:bg-accent cursor-pointer whitespace-nowrap text-destructive"
                onClick={() => {
                  handleDeleteFolder(contextMenu.itemId);
                  setContextMenu(null);
                }}
              >
                Delete
              </button>
            </>
          )}

          {contextMenu.itemType === 'deliverable' && (
            <>
              <button
                className="block w-full text-left px-4 py-2 text-sm hover:bg-accent cursor-pointer whitespace-nowrap"
                onClick={() => {
                  const deliverableId = contextMenu.itemId;
                  router.push(`/deliverables/${deliverableId}`);
                  setContextMenu(null);
                }}
              >
                Open
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm hover:bg-accent cursor-pointer whitespace-nowrap text-destructive"
                onClick={() => {
                  handleDeleteDeliverable(contextMenu.itemId);
                  setContextMenu(null);
                }}
              >
                Delete
              </button>
            </>
          )}
        </div>
      )}

      {/* Modal */}
      <TreeItemModal
        isOpen={modalState.isOpen}
        type={modalState.type}
        onClose={() => setModalState({ isOpen: false, type: 'project' })}
        onCreate={handleCreateItem}
      />
    </div>
  );
}
