'use client';

import { useState, useEffect } from 'react';
import { X, Lightbulb } from 'lucide-react';

export function WelcomeBanner() {
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Check if user has dismissed banner before
    const wasDismissed = localStorage.getItem('forgeos-welcome-dismissed');
    if (wasDismissed) {
      setDismissed(true);
    }
  }, []);

  if (dismissed) return null;

  const handleDismiss = () => {
    setDismissed(true);
    localStorage.setItem('forgeos-welcome-dismissed', 'true');
  };

  return (
    <div className="surface-card p-4 sm:p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <div className="h-9 w-9 rounded-lg border border-accent/30 bg-accent/10 flex items-center justify-center flex-shrink-0">
            <Lightbulb size={18} className="text-accent" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-fg-primary mb-1 tracking-tight">Welcome to ForgeOS</h3>
            <p className="text-sm text-fg-secondary mb-3 leading-relaxed">
              Here&apos;s how to get the most out of your personal writing assistant:
            </p>
            <ul className="text-sm text-fg-secondary space-y-1.5 list-disc list-inside">
              <li><strong className="text-fg-primary">Daily briefing:</strong> Check your inbox each morning for curated topics</li>
              <li><strong className="text-fg-primary">Let&apos;s Build:</strong> Press Cmd+K → &quot;New deliverable&quot; to start writing</li>
              <li><strong className="text-fg-primary">Expand engine:</strong> Go to Settings to strengthen your doctrine files</li>
              <li><strong className="text-fg-primary">Cmd+K:</strong> Universal command palette available everywhere</li>
            </ul>
          </div>
        </div>
        <button
          onClick={handleDismiss}
          className="text-fg-tertiary hover:text-fg-secondary hover:bg-bg-tertiary border border-transparent hover:border-border rounded-md p-1.5 flex-shrink-0 transition-colors"
        >
          <X size={18} />
        </button>
      </div>
    </div>
  );
}
