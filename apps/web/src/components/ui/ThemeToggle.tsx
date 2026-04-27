'use client';
import { useEffect, useState } from 'react';

export default function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    const saved = localStorage.getItem('theme') as 'dark' | 'light' | null;
    if (saved) {
      setTheme(saved);
      document.documentElement.setAttribute('data-theme', saved);
    }
  }, []);

  function toggle() {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  }

  return (
    <button
      onClick={toggle}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      className="fixed bottom-4 right-4 z-50 w-8 h-8 rounded-chip flex items-center justify-center text-sm bg-bg-secondary border border-border text-fg-secondary hover:text-fg-primary hover:border-accent transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? '☀' : '●'}
    </button>
  );
}
