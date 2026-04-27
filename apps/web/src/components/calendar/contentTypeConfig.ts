/**
 * Content-type colour palette and display labels.
 * Single source of truth used by EventPill, MonthView, AgendaView, and NewEventModal.
 */
import type { ContentType } from '@/lib/api';

interface ContentTypeConfig {
  label: string;
  /** Tailwind bg + text classes for the pill */
  pillClass: string;
  /** Hex for inline styles when Tailwind purge is uncertain */
  color: string;
}

export const CONTENT_TYPE_CONFIG: Record<ContentType, ContentTypeConfig> = {
  blog:           { label: 'Blog',          pillClass: 'bg-blue-100 text-blue-800 border-blue-300',     color: '#3b82f6' },
  email:          { label: 'Email',         pillClass: 'bg-purple-100 text-purple-800 border-purple-300', color: '#8b5cf6' },
  'press-release':{ label: 'Press Release', pillClass: 'bg-orange-100 text-orange-800 border-orange-300', color: '#f97316' },
  'case-study':   { label: 'Case Study',    pillClass: 'bg-teal-100 text-teal-800 border-teal-300',      color: '#14b8a6' },
  whitepaper:     { label: 'Whitepaper',    pillClass: 'bg-indigo-100 text-indigo-800 border-indigo-300', color: '#6366f1' },
  launch:         { label: 'Launch',        pillClass: 'bg-red-100 text-red-800 border-red-300',          color: '#ef4444' },
};

export const CONTENT_TYPES = Object.keys(CONTENT_TYPE_CONFIG) as ContentType[];
