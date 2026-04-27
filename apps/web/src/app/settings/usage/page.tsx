'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getApiBase } from '@/lib/api';

interface UsageData {
  period: string;
  total_cost_usd: number;
  total_cost_cents: number;
  events_by_type: {
    [key: string]: {
      count: number;
      cost_cents: number;
    };
  };
}

export default function UsageSettings() {
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsage();
  }, []);

  const fetchUsage = async () => {
    try {
      const res = await fetch(`${getApiBase()}/api/usage/current-month`, {
        credentials: 'include'
      });
      
      if (res.ok) {
        setUsage(await res.json());
      } else {
        setError('Failed to load usage data');
      }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err) {
      setError('Error loading usage data');
    } finally {
      setLoading(false);
    }
  };

  const formatCost = (cents: number) => `$${(cents / 100).toFixed(2)}`;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading usage data...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <Link href="/settings" className="text-blue-600 mb-4 inline-block">← Back to Settings</Link>
        
        <h1 className="text-3xl font-bold mb-2">Usage & Billing</h1>
        <p className="text-gray-600 mb-8">Track API usage and associated costs</p>

        {error && <div className="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>}

        {usage && (
          <>
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-sm font-medium text-gray-600 mb-2">{usage.period}</h2>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-gray-900">${usage.total_cost_usd.toFixed(2)}</span>
                <span className="text-gray-500">total cost</span>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow overflow-hidden">
              <h2 className="text-lg font-semibold p-6 border-b">Usage by Type</h2>
              {Object.keys(usage.events_by_type).length === 0 ? (
                <p className="p-6 text-gray-500">No usage this month</p>
              ) : (
                <div className="divide-y">
                  {Object.entries(usage.events_by_type).map(([type, data]) => (
                    <div key={type} className="p-6 flex justify-between items-center">
                      <div>
                        <h3 className="font-medium capitalize">{type}</h3>
                        <p className="text-sm text-gray-500">{data.count} events</p>
                      </div>
                      <span className="text-lg font-semibold">{formatCost(data.cost_cents)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-semibold text-blue-900 mb-2">Billing Information</h3>
              <p className="text-blue-800 text-sm mb-4">
                This dashboard shows current month usage. Billing cycles renew on the 1st of each month.
              </p>
              <Link href="/settings/billing" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                View billing settings →
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
