'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Zap, Plus } from 'lucide-react';

interface Command {
  id: string;
  label: string;
  description: string;
  icon?: React.ReactNode;
  action: () => void | Promise<void>;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const commands: Command[] = [
    {
      id: 'new-session',
      label: 'New session',
      description: 'Start a new chat session',
      icon: <Plus size={16} />,
      action: () => {
        setOpen(false);
        // Trigger new session modal
        const event = new CustomEvent('open-new-session');
        window.dispatchEvent(event);
      },
    },
    {
      id: 'new-deliverable',
      label: 'New deliverable',
      description: 'Let\'s Build: create a new deliverable',
      icon: <Zap size={16} />,
      action: () => {
        setOpen(false);
        const event = new CustomEvent('open-lets-build');
        window.dispatchEvent(event);
      },
    },
    {
      id: 'go-dashboard',
      label: 'Go to dashboard',
      description: 'Jump to home page',
      action: () => {
        setOpen(false);
        router.push('/');
      },
    },
    {
      id: 'go-settings',
      label: 'Go to settings',
      description: 'Open settings & engine editor',
      action: () => {
        setOpen(false);
        router.push('/settings');
      },
    },
    {
      id: 'go-workspace',
      label: 'Go to recent workspace',
      description: 'Open most recent deliverable',
      action: () => {
        setOpen(false);
        // This would fetch recent deliverable ID
        const recentId = localStorage.getItem('recent-deliverable-id');
        if (recentId) {
          router.push(`/workspace/${recentId}`);
        }
      },
    },
  ];

  const filtered = commands.filter(
    cmd =>
      cmd.label.toLowerCase().includes(search.toLowerCase()) ||
      cmd.description.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Cmd+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(!open);
        setSearch('');
        setSelected(0);
      }

      // Escape to close
      if (e.key === 'Escape') {
        setOpen(false);
      }

      // Arrow keys to navigate
      if (open) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setSelected(prev => (prev + 1) % filtered.length);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setSelected(prev => (prev - 1 + filtered.length) % filtered.length);
        } else if (e.key === 'Enter' && filtered.length > 0) {
          e.preventDefault();
          filtered[selected].action();
          setOpen(false);
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, search, selected, filtered]);

  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus();
    }
  }, [open]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-12">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={() => setOpen(false)}
      />

      {/* Panel */}
      <div className="relative w-full max-w-2xl rounded-lg shadow-xl bg-bg-secondary border border-border overflow-hidden">
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-border px-4 py-3">
          <Search size={18} className="text-fg-tertiary flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={e => {
              setSearch(e.target.value);
              setSelected(0);
            }}
            placeholder="Search commands..."
            className="flex-1 bg-transparent text-fg-primary placeholder-fg-tertiary focus:outline-none"
          />
          <kbd className="text-xs text-fg-tertiary px-2 py-1 border border-border rounded bg-bg-primary">
            Esc
          </kbd>
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-auto">
          {filtered.length === 0 ? (
            <div className="px-4 py-8 text-center text-fg-tertiary text-sm">
              No commands found
            </div>
          ) : (
            filtered.map((cmd, idx) => (
              <button
                key={cmd.id}
                onClick={() => {
                  cmd.action();
                  setOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left transition ${
                  idx === selected
                    ? 'bg-accent/10 text-accent'
                    : 'text-fg-primary hover:bg-bg-tertiary'
                }`}
              >
                {cmd.icon && <div className="flex-shrink-0">{cmd.icon}</div>}
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{cmd.label}</div>
                  <div className="text-xs text-fg-tertiary">{cmd.description}</div>
                </div>
                {idx === selected && (
                  <kbd className="text-xs text-fg-tertiary px-2 py-1 border border-border rounded bg-bg-primary flex-shrink-0">
                    Enter
                  </kbd>
                )}
              </button>
            ))
          )}
        </div>

        {/* Footer hint */}
        <div className="border-t border-border px-4 py-2 text-xs text-fg-tertiary flex items-center justify-between bg-bg-primary">
          <span>Use ↑↓ to navigate</span>
          <kbd className="text-xs text-fg-tertiary px-2 py-1 border border-border rounded bg-bg-secondary">
            ⌘K
          </kbd>
        </div>
      </div>
    </div>
  );
}
