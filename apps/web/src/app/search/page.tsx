'use client';
import { useState } from 'react';
import { getApiBase } from '@/lib/api';
import { getHeadersWithCSRF } from '@/lib/csrf';
import { Button } from '@/components/ui/Button';
import OpportunitiesSection from '@/components/search/OpportunitiesSection';
import DefendingPositionSection from '@/components/search/DefendingPositionSection';
import ConversationalPulseSection from '@/components/search/ConversationalPulseSection';

export default function SearchPage() {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefreshAll = async () => {
    setRefreshing(true);
    try {
      const response = await fetch(`${getApiBase()}/api/intelligence/scrape`, { 
        method: 'POST',
        headers: getHeadersWithCSRF(),
      });
      if (!response.ok) throw new Error('Scrape failed');
      await new Promise(resolve => setTimeout(resolve, 2000));
      window.location.reload();
    } catch (err) {
      console.error('Refresh failed:', err);
      alert('Failed to refresh search intelligence. Check the API.');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="p-6 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Search Intelligence</h1>
          <p className="text-sm text-fg-secondary mt-1">Content opportunities, position defense, and conversation signals</p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={handleRefreshAll}
          loading={refreshing}
        >
          Refresh now ↻
        </Button>
      </div>

      <OpportunitiesSection />
      <DefendingPositionSection />
      <ConversationalPulseSection />
    </div>
  );
}
