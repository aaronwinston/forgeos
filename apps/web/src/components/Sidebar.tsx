'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import ProjectTree from '@/components/workspace/ProjectTree';
import OrgSwitcher from '@/components/OrgSwitcher';
import { useState } from 'react';

export default function Sidebar() {
  const pathname = usePathname();
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', tooltip: 'Home: briefing, health, recent work' },
    { href: '/sessions', label: 'Sessions', tooltip: 'Saved chat conversations' },
    { href: '/intelligence', label: 'Intelligence', tooltip: 'Source scraping and search' },
    { href: '/search', label: 'Search Intelligence', tooltip: 'Full-text search across all content' },
    { href: '/calendar', label: 'Calendar', tooltip: 'Synced calendar events' },
    { href: '/settings', label: 'Settings', tooltip: 'Engine editor and integrations' },
  ];

  return (
    <aside className="w-64 border-r border-border/80 bg-bg-secondary/85 backdrop-blur-md flex flex-col h-full">
      <div className="p-4 border-b border-border/80 space-y-3">
        <div className="space-y-1">
          <h1 className="font-semibold text-[15px] tracking-tight text-fg-primary">ForgeOS</h1>
          <p className="text-xs text-fg-tertiary">Editorial command center</p>
        </div>
        <OrgSwitcher />
      </div>
      <nav className="p-3 space-y-1">
        {navItems.map(item => (
          <div key={item.href} className="relative group">
            <Link
              href={item.href}
              onMouseEnter={() => setHoveredItem(item.href)}
              onMouseLeave={() => setHoveredItem(null)}
              className={`block px-3 py-2 rounded-lg text-sm transition-colors relative ${
                pathname === item.href
                  ? 'bg-bg-tertiary text-fg-primary font-medium border border-border'
                  : 'text-fg-secondary hover:text-fg-primary hover:bg-bg-tertiary/70 border border-transparent'
              }`}
            >
              {pathname === item.href && <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-full bg-accent" />}
              {item.label}
            </Link>
            {hoveredItem === item.href && (
              <div className="absolute left-full ml-2 top-0 z-50 rounded-md bg-bg-tertiary border border-border px-2 py-1 text-xs text-fg-tertiary whitespace-nowrap pointer-events-none shadow-lg">
                {item.tooltip}
              </div>
            )}
          </div>
        ))}
      </nav>
      <div className="flex-1 border-t border-border/80 mt-2 flex flex-col min-h-0">
        <p className="text-xs px-3 py-3 font-semibold text-fg-tertiary uppercase tracking-[0.08em]">Projects</p>
        <div className="flex-1 min-h-0 overflow-hidden">
          <ProjectTree />
        </div>
      </div>
    </aside>
  );
}
