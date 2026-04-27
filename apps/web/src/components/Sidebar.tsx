'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import ProjectTree from '@/components/workspace/ProjectTree';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/sessions', label: 'Sessions' },
    { href: '/intelligence', label: 'Intelligence' },
    { href: '/search', label: 'Search Intelligence' },
    { href: '/calendar', label: 'Calendar' },
    { href: '/settings', label: 'Settings' },
  ];

  return (
    <aside className="w-56 border-r border-border bg-bg-secondary flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <h1 className="font-bold text-sm text-fg-primary">ForgeOS</h1>
        <p className="text-xs text-fg-tertiary">Marketing command center</p>
      </div>
      <nav className="p-2 space-y-1">
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`block px-3 py-2 rounded-input text-sm transition-colors ${pathname === item.href ? 'bg-accent/10 text-accent font-medium' : 'text-fg-secondary hover:text-fg-primary hover:bg-bg-tertiary'}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="flex-1 border-t border-border mt-2 flex flex-col min-h-0">
        <p className="text-xs px-3 py-2 font-semibold text-fg-tertiary">Projects</p>
        <div className="flex-1 min-h-0 overflow-hidden">
          <ProjectTree />
        </div>
      </div>
    </aside>
  );
}

