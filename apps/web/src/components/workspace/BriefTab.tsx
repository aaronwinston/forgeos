'use client';

import BriefEditor from './BriefEditor';

interface BriefTabProps {
  deliverable: {
    id: number;
    title: string;
  };
  brief?: {
    id: number;
    title?: string;
    audience?: string;
    description?: string;
    brief_md: string;
    toggles_json?: string;
  };
}

export default function BriefTab({ deliverable, brief }: BriefTabProps) {
  const handleBriefChange = () => {
    window.location.reload();
  };

  if (!brief) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center">
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">📋 No brief yet</p>
          <p className="text-xs text-gray-500">Create a brief to get started</p>
        </div>
      </div>
    );
  }

  return (
    <BriefEditor
      brief={brief}
      deliverableId={deliverable.id}
      onChange={handleBriefChange}
    />
  );
}
