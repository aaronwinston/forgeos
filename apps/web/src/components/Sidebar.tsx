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
    { href: '/settings', label: 'Settings' },
  ];

  return (
    <aside className="w-56 border-r bg-background flex flex-col h-screen">
      <div className="p-4 border-b">
        <h1 className="font-bold text-sm">ForgeOS</h1>
        <p className="text-xs text-muted-foreground">Marketing Command Center</p>
      </div>
      <nav className="p-2 space-y-1">
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`block px-3 py-2 rounded text-sm ${pathname === item.href ? 'bg-accent font-medium' : 'hover:bg-accent/50'}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="flex-1 border-t mt-2 flex flex-col min-h-0">
        <p className="text-xs text-muted-foreground px-3 py-2 uppercase font-semibold">Projects</p>
        <div className="flex-1 min-h-0 overflow-hidden">
          <ProjectTree />
        </div>
      </div>
    </aside>
  );
}

