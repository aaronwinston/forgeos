'use client';

import ChatInterface from './ChatInterface';

interface ChatTabProps {
  deliverable: {
    id: number;
    title: string;
    folder_id: number;
  };
  brief?: {
    id: number;
    brief_md: string;
    toggles_json?: string;
  };
}

export default function ChatTab({ deliverable, brief }: ChatTabProps) {
  return (
    <ChatInterface
      deliverableId={deliverable.id}
      briefId={brief?.id}
      briefData={brief}
    />
  );
}
