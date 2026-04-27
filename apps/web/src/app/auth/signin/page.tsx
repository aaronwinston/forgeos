'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getCSRFToken, getHeadersWithCSRF } from '@/lib/csrf';

export default function SignIn() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [csrfToken, setCSRFToken] = useState('');

  // Initialize CSRF token on component mount
  useEffect(() => {
    setCSRFToken(getCSRFToken());
  }, []);

  async function handleSignIn(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
      const response = await fetch(`${API_BASE}/api/auth/signin`, {
        method: 'POST',
        headers: getHeadersWithCSRF({
          'Content-Type': 'application/json',
        }),
        credentials: 'include', // Important: allows cookies to be set
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Sign in failed' }));
        throw new Error(errorData.detail || 'Sign in failed');
      }

      // Token is now stored in httpOnly cookie, redirect to dashboard
      router.push('/dashboard');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Sign in failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800 rounded-lg shadow-xl p-8 border border-slate-700">
          <h1 className="text-3xl font-bold text-white mb-2">ForgeOS</h1>
          <p className="text-slate-400 mb-8">AI-native editorial platform</p>

          <form onSubmit={handleSignIn} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-2 rounded bg-slate-700 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2 rounded bg-slate-700 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                required
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/50 rounded text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !csrfToken}
              className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 text-white font-medium rounded transition"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-slate-400 text-sm mt-6">
            Don&apos;t have an account?{' '}
            <a href="/auth/signup" className="text-purple-400 hover:text-purple-300">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
