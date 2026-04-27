'use client';
import { useState } from 'react';
import ProjectTree from './ProjectTree';
import ChatTab from './ChatTab';
import EditorTab from './EditorTab';
import BriefTab from './BriefTab';

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

  const formatTime = (date: string | undefined) => {
    if (!date) return null;
    return new Date(date).toLocaleTimeString();
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Left Pane: Project Tree */}
      <div className="w-[220px] border-r border-gray-200 bg-gray-50 overflow-hidden flex flex-col">
        <div className="p-3 border-b border-gray-200">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Projects</p>
        </div>
        <ProjectTree
          projects={projects}
          selectedDeliverableId={deliverable.id}
        />
      </div>

      {/* Center Pane: Tabs */}
      <div className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Breadcrumb and Toolbar */}
        <div className="border-b border-gray-200 bg-gray-50 px-4 py-3 space-y-2">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-xs text-gray-600">
            {project && <span>{project.name}</span>}
            {project && folder && <span className="text-gray-400">/</span>}
            {folder && <span>{folder.name}</span>}
            {folder && <span className="text-gray-400">/</span>}
            <span className="font-medium text-gray-900">{deliverable.title}</span>
          </div>

          {/* Toolbar */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Deliverable</p>
              <h1 className="text-lg font-semibold text-gray-900">{deliverable.title}</h1>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs px-2.5 py-1 rounded-full bg-white border border-gray-300 text-gray-700 font-medium capitalize">
                {deliverable.status}
              </span>
              {deliverable.updated_at && (
                <span className="text-xs text-gray-500">
                  Saved {formatTime(deliverable.updated_at)}
                </span>
              )}
              <button className="text-xs px-3 py-1.5 rounded bg-white border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors">
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 bg-white flex">
          {(['chat', 'editor', 'brief'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-black text-black'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'chat' && <ChatTab deliverable={deliverable} />}
          {activeTab === 'editor' && <EditorTab deliverable={deliverable} />}
          {activeTab === 'brief' && <BriefTab deliverable={deliverable} brief={brief} />}
        </div>
      </div>

      {/* Right Pane: Toggles + Context */}
      <div className="w-[300px] border-l border-gray-200 bg-gray-50 overflow-auto flex flex-col">
        <div className="p-3 border-b border-gray-200 space-y-3">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Brief Toggle</p>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" defaultChecked className="w-4 h-4 rounded" />
              <span className="text-gray-700">Brief first</span>
            </label>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Audience</label>
            <input
              type="text"
              defaultValue="AI engineers"
              className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Voice</label>
            <select className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white">
              <option>thoughtful</option>
              <option>opinionated</option>
              <option>objective</option>
              <option>technical</option>
              <option>founder</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Skills</label>
            <input
              type="text"
              placeholder="comma-separated"
              className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Playbook</label>
            <input
              type="text"
              defaultValue="auto"
              className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">Content Type</label>
            <select className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 bg-white">
              <option>blog</option>
              <option>article</option>
              <option>guide</option>
              <option>whitepaper</option>
              <option>tutorial</option>
            </select>
          </div>
        </div>

        <div className="p-3 border-t border-gray-200">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Context in Use</p>
          <div className="space-y-2">
            <p className="text-xs text-gray-500 italic">No context added yet</p>
          </div>
        </div>
      </div>
    </div>
  );
}
