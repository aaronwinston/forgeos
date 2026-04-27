'use client';
import { useState } from 'react';
import WorkspaceProjectTree from './WorkspaceProjectTree';
import ChatTab from './ChatTab';
import EditorTab from './EditorTab';
import BriefTab from './BriefTab';
import TogglesPanel from './TogglesPanel';
import ContextInUsePanel from './ContextInUsePanel';

interface WorkspaceLayoutProps {
  deliverable: {
    id: number;
    title: string;
    content_type: string;
    status: string;
    body_md?: string;
    updated_at?: string;
    folder_id: number;
  };
  brief?: {
    id: number;
    brief_md: string;
    toggles_json?: string;
  };
  projects: Array<{
    id: number;
    name: string;
  }>;
  folder?: {
    id: number;
    name: string;
    project_id: number;
  };
  project?: {
    id: number;
    name: string;
  };
}

export default function WorkspaceLayout({ 
  deliverable, 
  brief, 
  projects, 
  folder, 
  project 
}: WorkspaceLayoutProps) {
  const [activeTab, setActiveTab] = useState<'chat' | 'editor' | 'brief'>('chat');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const formatTime = (date: string | undefined) => {
    if (!date) return null;
    return new Date(date).toLocaleTimeString();
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Left Pane: Project Tree */}
      <div className={`${sidebarCollapsed ? 'w-12' : 'w-[220px]'} border-r border-gray-200 bg-gray-50 overflow-hidden flex flex-col transition-all duration-200`}>
        <div className="p-3 border-b border-gray-200 flex items-center justify-between gap-2">
          {!sidebarCollapsed && (
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Projects</p>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="ml-auto p-1 hover:bg-gray-200 rounded transition-colors"
            title={sidebarCollapsed ? 'Expand' : 'Collapse'}
          >
            <span className="text-sm text-gray-600">{sidebarCollapsed ? '▶' : '◀'}</span>
          </button>
        </div>
        {!sidebarCollapsed && (
          <WorkspaceProjectTree
            projects={projects}
            selectedDeliverableId={deliverable.id}
          />
        )}
      </div>

      {/* Center Pane: Tabs */}
      <div className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Breadcrumb and Toolbar */}
        <div className="border-b border-gray-200 bg-gray-50 px-4 py-3 space-y-2">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-xs text-gray-600">
            {project && <span className="font-medium text-gray-700 hover:text-gray-900 cursor-pointer">{project.name}</span>}
            {project && folder && <span className="text-gray-400">/</span>}
            {folder && <span className="font-medium text-gray-700 hover:text-gray-900 cursor-pointer">{folder.name}</span>}
            {folder && <span className="text-gray-400">/</span>}
            <span className="font-bold text-gray-900">{deliverable.title}</span>
          </div>

          {/* Toolbar */}
          <div className="flex items-center justify-between gap-3">
            <div className="flex-1 min-w-0">
              <h1 className="text-base font-semibold text-gray-900 truncate">{deliverable.title}</h1>
              <p className="text-xs text-gray-500 mt-0.5">
                {deliverable.content_type.charAt(0).toUpperCase() + deliverable.content_type.slice(1)}
              </p>
            </div>
            <div className="flex items-center gap-2 whitespace-nowrap">
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium capitalize border ${
                deliverable.status === 'draft' ? 'bg-yellow-50 border-yellow-300 text-yellow-700' :
                deliverable.status === 'active' ? 'bg-blue-50 border-blue-300 text-blue-700' :
                'bg-green-50 border-green-300 text-green-700'
              }`}>
                {deliverable.status}
              </span>
              {deliverable.updated_at && (
                <span className="text-xs text-gray-500">
                  Saved {formatTime(deliverable.updated_at)}
                </span>
              )}
              <button className="text-xs px-3 py-1.5 rounded bg-white border border-gray-300 text-gray-700 hover:bg-gray-100 hover:border-gray-400 transition-all duration-150">
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 bg-white flex">
          {(['chat', 'editor', 'brief'] as const).map((tab, idx) => (
            <div key={tab} className="flex items-stretch">
              <button
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-sm font-medium transition-all duration-150 ${
                  activeTab === tab
                    ? 'border-b-2 border-black text-gray-900'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
              {idx < 2 && <div className="w-px bg-gray-200" />}
            </div>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'chat' && <ChatTab deliverable={deliverable} brief={brief} />}
          {activeTab === 'editor' && <EditorTab deliverable={deliverable} />}
          {activeTab === 'brief' && <BriefTab deliverable={deliverable} brief={brief} />}
        </div>
      </div>

      {/* Right Pane: Toggles + Context */}
      <div className="w-[300px] border-l border-gray-200 bg-gray-50 overflow-hidden flex flex-col">
        <TogglesPanel brief={brief} onChange={() => window.location.reload()} />
        <ContextInUsePanel
          brief={brief}
          intelligenceItems={[]}
          onChange={() => window.location.reload()}
        />
      </div>
    </div>
  );
}
