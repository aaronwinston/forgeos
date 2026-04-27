'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getApiBase } from '@/lib/api';

interface RuntimeKey {
  runtime: string;
  is_valid: boolean;
  last_validated_at?: string;
}

export default function RuntimesSettings() {
  const [keys, setKeys] = useState<RuntimeKey[]>([]);
  const [apiKey, setApiKey] = useState('');
  const [selectedRuntime, setSelectedRuntime] = useState<string>('anthropic');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      const res = await fetch(`${getApiBase()}/api/runtimes`, {
        credentials: 'include'
      });
      if (res.ok) {
        setKeys(await res.json());
      }
    } catch (err) {
      setError('Failed to load runtime keys');
    }
  };

  const handleAddKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const res = await fetch(`${getApiBase()}/api/runtimes/${selectedRuntime}/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ api_key: apiKey })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to add key');
      }

      setSuccess(`${selectedRuntime} key added successfully`);
      setApiKey('');
      fetchKeys();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (runtime: string) => {
    try {
      const res = await fetch(`${getApiBase()}/api/runtimes/${runtime}/validate`, {
        method: 'POST',
        credentials: 'include'
      });
      const data = await res.json();
      
      if (data.status === 'valid') {
        setSuccess(`${runtime} key validated successfully`);
      } else {
        setError(`${runtime} key validation failed: ${data.error}`);
      }
      fetchKeys();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (runtime: string) => {
    if (!confirm(`Delete ${runtime} key?`)) return;

    try {
      const res = await fetch(`${getApiBase()}/api/runtimes/${runtime}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (res.ok) {
        setSuccess(`${runtime} key deleted`);
        fetchKeys();
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <Link href="/settings" className="text-blue-600 mb-4 inline-block">← Back to Settings</Link>
        
        <h1 className="text-3xl font-bold mb-2">Runtime Credentials</h1>
        <p className="text-gray-600 mb-8">Manage API keys for different LLM runtimes</p>

        {error && <div className="bg-red-50 text-red-700 p-4 rounded mb-4">{error}</div>}
        {success && <div className="bg-green-50 text-green-700 p-4 rounded mb-4">{success}</div>}

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Add Runtime Key</h2>
          <form onSubmit={handleAddKey} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Runtime</label>
              <select
                value={selectedRuntime}
                onChange={(e) => setSelectedRuntime(e.target.value)}
                className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="anthropic">Anthropic</option>
                <option value="openai">OpenAI</option>
                <option value="copilot">Copilot</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={`sk-ant-... for ${selectedRuntime}`}
                className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Keys are encrypted and stored securely</p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Adding...' : 'Add Key'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <h2 className="text-lg font-semibold p-6 border-b">Configured Keys</h2>
          {keys.length === 0 ? (
            <p className="p-6 text-gray-500">No runtime keys configured</p>
          ) : (
            <div className="divide-y">
              {keys.map((key) => (
                <div key={key.runtime} className="p-6 flex justify-between items-start">
                  <div>
                    <h3 className="font-medium capitalize">{key.runtime}</h3>
                    <p className="text-sm text-gray-500">
                      {key.is_valid ? '✓ Valid' : '✗ Invalid'} {key.last_validated_at && `• Last validated: ${new Date(key.last_validated_at).toLocaleDateString()}`}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleValidate(key.runtime)}
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      Test
                    </button>
                    <button
                      onClick={() => handleDelete(key.runtime)}
                      className="text-red-600 hover:text-red-700 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
