'use client';

import { useEffect, useState } from 'react';
import EngineTree from '@/components/settings/EngineTree';
import EngineEditor from '@/components/settings/EngineEditor';
import SettingsConfig from '@/components/settings/SettingsConfig';
import { AlertCircle } from 'lucide-react';

type Tab = 'engine' | 'settings';

export default function SettingsPage() {
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('engine');
  const [showUnsavedWarning, setShowUnsavedWarning] = useState(false);
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null);

  // Handle navigation with unsaved changes warning
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  function handleTabChange(tab: Tab) {
    if (isDirty && activeTab === 'engine') {
      setShowUnsavedWarning(true);
      setPendingNavigation(`tab:${tab}`);
    } else {
      setActiveTab(tab);
      setIsDirty(false);
    }
  }

  function handleSelectFile(path: string) {
    if (isDirty && selectedPath !== null) {
      setShowUnsavedWarning(true);
      setPendingNavigation(`file:${path}`);
    } else {
      setSelectedPath(path);
      setIsDirty(false);
    }
  }

  function handleNavigateToFile(path: string) {
    handleSelectFile(path);
  }

  function confirmUnsavedNavigation() {
    setShowUnsavedWarning(false);
    if (pendingNavigation?.startsWith('tab:')) {
      const tab = pendingNavigation.split(':')[1] as Tab;
      setActiveTab(tab);
      setIsDirty(false);
    } else if (pendingNavigation?.startsWith('file:')) {
      const path = pendingNavigation.split(':').slice(1).join(':');
      setSelectedPath(path);
      setIsDirty(false);
    }
    setPendingNavigation(null);
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Unsaved changes warning modal */}
      {showUnsavedWarning && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-md p-6 space-y-4">
            <div className="flex gap-3">
              <AlertCircle size={20} className="text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-gray-900">Unsaved changes</h3>
                <p className="text-sm text-gray-600 mt-1">You have unsaved changes in {selectedPath?.split('/').pop() || 'the file'}. Do you want to leave without saving?</p>
              </div>
            </div>
            <div className="flex gap-2 justify-end pt-4">
              <button
                onClick={() => setShowUnsavedWarning(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200 font-medium text-sm"
              >
                Cancel
              </button>
              <button
                onClick={confirmUnsavedNavigation}
                className="px-4 py-2 text-white bg-orange-600 rounded hover:bg-orange-700 font-medium text-sm"
              >
                Leave without saving
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b bg-gray-50 sticky top-0 z-10">
        <div className="flex">
          <button
            onClick={() => handleTabChange('engine')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition ${
              activeTab === 'engine'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Engine files
          </button>
          <button
            onClick={() => handleTabChange('settings')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition ${
              activeTab === 'settings'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Settings & integrations
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex">
        {activeTab === 'engine' ? (
          <>
            <EngineTree selectedPath={selectedPath} onSelect={handleSelectFile} />
            <EngineEditor
              filePath={selectedPath}
              isDirty={isDirty}
              onDirtyChange={setIsDirty}
            />
          </>
        ) : (
          <SettingsConfig onNavigateTo={handleNavigateToFile} />
        )}
      </div>
    </div>
  );
}
