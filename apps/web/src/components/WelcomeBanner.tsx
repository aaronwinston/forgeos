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
    <div className="mx-6 mb-6 rounded-lg border border-accent/30 bg-accent/5 p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <Lightbulb size={20} className="text-accent mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="font-bold text-fg-primary mb-1">Welcome to ForgeOS</h3>
            <p className="text-sm text-fg-secondary mb-3">
              Here's how to get the most out of your personal writing assistant:
            </p>
            <ul className="text-sm text-fg-secondary space-y-1 list-disc list-inside">
              <li><strong className="text-fg-primary">Daily briefing:</strong> Check your inbox each morning for curated topics</li>
              <li><strong className="text-fg-primary">Let's Build:</strong> Press Cmd+K → "New deliverable" to start writing</li>
              <li><strong className="text-fg-primary">Expand engine:</strong> Go to Settings to strengthen your doctrine files</li>
              <li><strong className="text-fg-primary">Cmd+K:</strong> Universal command palette available everywhere</li>
            </ul>
          </div>
        </div>
        <button
          onClick={handleDismiss}
          className="text-fg-tertiary hover:text-fg-secondary flex-shrink-0"
        >
          <X size={18} />
        </button>
      </div>
    </div>
  );
}
