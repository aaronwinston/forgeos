'use client';

import { useState } from 'react';
import { BookOpen, Zap, X } from 'lucide-react';

interface SkillPlaybookChipProps {
  type: 'skill' | 'playbook';
  name: string;
}

export default function SkillPlaybookChip({ type, name }: SkillPlaybookChipProps) {
  const [showPreview, setShowPreview] = useState(false);
  const [previewContent, setPreviewContent] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const handleClick = async () => {
    if (!showPreview && !previewContent) {
      setPreviewLoading(true);
      try {
        // In a real implementation, this would fetch the skill/playbook content
        // For now, we'll just show a placeholder
        setPreviewContent(`# ${name}\n\nLoading ${type} content...`);
      } catch {
        setPreviewContent(`Error loading ${type}: ${name}`);
      } finally {
        setPreviewLoading(false);
      }
    }
    setShowPreview(!showPreview);
  };

  const bgColor = type === 'skill' ? 'bg-purple-100 hover:bg-purple-200' : 'bg-blue-100 hover:bg-blue-200';
  const textColor = type === 'skill' ? 'text-purple-700' : 'text-blue-700';
  const icon = type === 'skill' ? <Zap className="w-3 h-3" /> : <BookOpen className="w-3 h-3" />;

  return (
    <>
      <button
        onClick={handleClick}
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-colors cursor-pointer ${bgColor} ${textColor} hover:shadow-sm`}
        title={`Click to view ${type}: ${name}`}
      >
        {icon}
        <span>{name}</span>
      </button>

      {showPreview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowPreview(false)}>
          <div
            className="bg-bg-secondary rounded-card shadow-xl max-w-2xl w-full max-h-96 overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-gray-500 font-semibold">{type}</p>
                <h3 className="text-lg font-bold text-gray-900 mt-1">{name}</h3>
              </div>
              <button
                onClick={() => setShowPreview(false)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6">
              {previewLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : previewContent ? (
                <div className="prose prose-sm max-w-none">
                  <pre className="bg-gray-50 p-4 rounded border border-gray-200 overflow-auto text-xs">
                    <code>{previewContent}</code>
                  </pre>
                </div>
              ) : (
                <p className="text-sm text-gray-600">No content available</p>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
