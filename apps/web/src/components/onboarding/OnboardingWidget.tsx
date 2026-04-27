'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface OnboardingState {
  completed_steps: string[];
  all_steps: string[];
}

const STEP_LABELS: Record<string, string> = {
  company_pitch: 'Company pitch',
  voice_examples: 'Voice examples',
  competitors: 'Competitors',
  claims_policy: 'Claims policy',
  runtime_key: 'Runtime key',
  starter_project: 'Starter project',
};

export default function OnboardingWidget() {
  const [state, setState] = useState<OnboardingState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchState();
  }, []);

  const fetchState = async () => {
    try {
      const res = await fetch('/api/onboarding/state', {
        credentials: 'include'
      });
      if (res.ok) {
        setState(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !state) return null;

  // Hide widget if all steps completed
  if (state.completed_steps.length === state.all_steps.length) {
    return null;
  }

  const progressPercent = (state.completed_steps.length / state.all_steps.length) * 100;
  const incompleteSteps = state.all_steps.filter(step => !state.completed_steps.includes(step));

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-blue-900">Complete your setup</h3>
          <p className="text-sm text-blue-700">{state.completed_steps.length} of {state.all_steps.length} steps done</p>
        </div>
        <Link href="/onboarding" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
          Continue →
        </Link>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-blue-200 rounded-full h-2 mb-4">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Incomplete steps */}
      <div className="space-y-2">
        {incompleteSteps.slice(0, 3).map((step) => (
          <div key={step} className="flex items-center gap-2 text-sm">
            <div className="w-5 h-5 rounded-full border-2 border-blue-300 flex items-center justify-center">
              <div className="w-2 h-2 bg-blue-300 rounded-full"></div>
            </div>
            <span className="text-blue-800">{STEP_LABELS[step] || step}</span>
          </div>
        ))}
      </div>

      {incompleteSteps.length > 3 && (
        <p className="text-xs text-blue-600 mt-2">+{incompleteSteps.length - 3} more steps</p>
      )}
    </div>
  );
}
