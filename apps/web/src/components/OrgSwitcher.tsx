'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getApiBase } from '@/lib/api';

interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
}

export default function OrgSwitcher() {
  const router = useRouter();
  const [currentOrg, setCurrentOrg] = useState<Organization | null>(null);
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const personalMode = process.env.NEXT_PUBLIC_FORGEOS_MODE === 'personal';

  useEffect(() => {
    // Load current org from cookie
    const orgId = document.cookie.split('; ').find(row => row.startsWith('current_org_id='))?.split('=')[1];
    
    if (orgId) {
      // Set a placeholder name - in production, fetch full org details from API
      setCurrentOrg({ id: orgId, name: 'My Organization', slug: '', plan: 'free' });
    }
    
    // Fetch orgs from API (skip in personal mode)
    if (!personalMode) {
      fetchOrgs();
    } else {
      // In personal mode, show hardcoded Personal org
      setCurrentOrg({ id: 'personal', name: 'Personal', slug: 'personal', plan: 'pro' });
    }
  }, [personalMode]);

  async function fetchOrgs() {
    try {
      const API_BASE = getApiBase();
      const response = await fetch(`${API_BASE}/api/orgs`, {
        credentials: 'include', // Send cookies
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrgs(data);
      }
    } catch (error) {
      console.error('Failed to fetch orgs:', error);
    }
  }

  async function switchOrg(org: Organization) {
    // In cookie-based auth, org switching would be handled server-side
    // For now, just update the client-side state
    setCurrentOrg(org);
    setIsOpen(false);
    
    // Reload the page to refresh all data in new org context
    router.push('/dashboard');
  }

  async function createNewOrg() {
    const orgName = prompt('Organization name:');
    if (!orgName) return;
    
    setLoading(true);
    try {
      const API_BASE = getApiBase();
      const slug = orgName.toLowerCase().replace(/\s+/g, '-');
      
      const response = await fetch(`${API_BASE}/api/orgs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Send cookies
        body: JSON.stringify({ name: orgName, slug }),
      });
      
      if (response.ok) {
        const newOrg = await response.json();
        await switchOrg(newOrg);
        await fetchOrgs();
      }
    } catch (error) {
      console.error('Failed to create org:', error);
    } finally {
      setLoading(false);
    }
  }

  if (!currentOrg) {
    return <div className="p-2 text-slate-400 text-sm">Loading...</div>;
  }

  // In personal mode, show disabled org switcher
  if (personalMode) {
    return (
      <div className="relative">
        <button
          disabled
          className="w-full px-3 py-2 rounded bg-slate-700 text-white text-left font-medium cursor-not-allowed opacity-60"
          title="Organization switcher is disabled in personal mode"
        >
          {currentOrg.name}
        </button>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 rounded bg-slate-700 hover:bg-slate-600 text-white text-left font-medium transition"
      >
        {currentOrg.name}
        <span className="ml-2 text-xs">▼</span>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-1 w-full bg-slate-800 border border-slate-700 rounded shadow-lg z-50">
          <div className="max-h-48 overflow-auto">
            {orgs.map((org) => (
              <button
                key={org.id}
                onClick={() => switchOrg(org)}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-slate-700 transition ${
                  org.id === currentOrg.id ? 'bg-purple-600' : 'text-slate-300'
                }`}
              >
                {org.name}
                {org.id === currentOrg.id && ' ✓'}
              </button>
            ))}
          </div>

          <div className="border-t border-slate-700 p-2">
            <button
              onClick={createNewOrg}
              disabled={loading}
              className="w-full px-3 py-2 text-sm bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 text-white rounded transition font-medium"
            >
              {loading ? 'Creating...' : '+ New Organization'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
