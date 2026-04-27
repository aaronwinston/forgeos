'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

type OnboardingStep = 
  | 'company_pitch'
  | 'voice_examples'
  | 'competitors'
  | 'claims_policy'
  | 'runtime_key'
  | 'starter_project'
  | 'complete';

interface OnboardingState {
  completed_steps: string[];
  all_steps: string[];
}

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('company_pitch');
  const [state, setState] = useState<OnboardingState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchState();
  }, []);

  const fetchState = async () => {
    try {
      const res = await fetch('/api/onboarding/state', {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setState(data);
        // Skip to next incomplete step
        const nextIncomplete = data.all_steps.find((step: string) => !data.completed_steps.includes(step));
        if (nextIncomplete) {
          setCurrentStep(nextIncomplete);
        } else {
          setCurrentStep('complete');
        }
      }
    } catch (err) {
      setError('Failed to load onboarding state');
    } finally {
      setLoading(false);
    }
  };

  const completeStep = async (step: OnboardingStep) => {
    if (!state) return;
    try {
      const newCompleted = [...state.completed_steps, step];
      const res = await fetch('/api/onboarding/state', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          
        },
        credentials: 'include',
        body: JSON.stringify({ completed_steps: newCompleted })
      });
      if (res.ok) {
        await fetchState();
      }
    } catch (err) {
      setError('Failed to save progress');
    }
  };

  const goToNextStep = async () => {
    await completeStep(currentStep);
    const nextIndex = state!.all_steps.indexOf(currentStep) + 1;
    if (nextIndex < state!.all_steps.length) {
      setCurrentStep(state!.all_steps[nextIndex] as OnboardingStep);
    } else {
      setCurrentStep('complete');
      setTimeout(() => router.push('/dashboard'), 1000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-600">Loading onboarding...</p>
      </div>
    );
  }

  if (!state) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-red-600">{error || 'Failed to load onboarding'}</p>
      </div>
    );
  }

  const progressPercent = (state.completed_steps.length / state.all_steps.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <h1 className="text-3xl font-bold text-gray-900">Set up ForgeOS</h1>
            <span className="text-sm text-gray-600">{state.completed_steps.length} of {state.all_steps.length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {currentStep === 'company_pitch' && <CompanyPitchStep onNext={goToNextStep} />}
        {currentStep === 'voice_examples' && <VoiceExamplesStep onNext={goToNextStep} />}
        {currentStep === 'competitors' && <CompetitorsStep onNext={goToNextStep} />}
        {currentStep === 'claims_policy' && <ClaimsPolicyStep onNext={goToNextStep} />}
        {currentStep === 'runtime_key' && <RuntimeKeyStep onNext={goToNextStep} />}
        {currentStep === 'starter_project' && <StarterProjectStep onNext={goToNextStep} />}
        {currentStep === 'complete' && <CompleteStep />}
      </div>
    </div>
  );
}

// Step components
function CompanyPitchStep({ onNext }: { onNext: () => void }) {
  const [pitch, setPitch] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await fetch('/api/onboarding/extract-messaging', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          
        },
        credentials: 'include',
        body: JSON.stringify({ pitch })
      });
      onNext();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4">Tell us about your company</h2>
      <p className="text-gray-600 mb-6">Write a brief elevator pitch about your company. This helps us understand your business and tailor the engine.</p>
      
      <textarea
        value={pitch}
        onChange={(e) => setPitch(e.target.value)}
        placeholder="E.g., 'We build developer tools for machine learning teams...'"
        className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-6"
      />
      
      <button
        onClick={handleSubmit}
        disabled={!pitch.trim() || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
      >
        {loading ? 'Analyzing...' : 'Next'}
      </button>
    </div>
  );
}

function VoiceExamplesStep({ onNext }: { onNext: () => void }) {
  const [examples, setExamples] = useState(['', '', '']);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await fetch('/api/onboarding/analyze-voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          
        },
        credentials: 'include',
        body: JSON.stringify({ examples: examples.filter(e => e.trim()) })
      });
      onNext();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4">Upload your existing voice</h2>
      <p className="text-gray-600 mb-6">Paste 2-3 examples of your best writing to help us understand your tone and style.</p>
      
      {examples.map((example, i) => (
        <textarea
          key={i}
          value={example}
          onChange={(e) => {
            const newExamples = [...examples];
            newExamples[i] = e.target.value;
            setExamples(newExamples);
          }}
          placeholder={`Example ${i + 1} (optional)`}
          className="w-full h-24 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
        />
      ))}
      
      <button
        onClick={handleSubmit}
        disabled={!examples.some(e => e.trim()) || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
      >
        {loading ? 'Analyzing...' : 'Next'}
      </button>
    </div>
  );
}

function CompetitorsStep({ onNext }: { onNext: () => void }) {
  const [competitors, setCompetitors] = useState([
    { name: '', description: '' },
    { name: '', description: '' },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await fetch('/api/onboarding/analyze-competitors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          
        },
        credentials: 'include',
        body: JSON.stringify({ 
          competitors: competitors.filter(c => c.name.trim()) 
        })
      });
      onNext();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4">Who do you compete with?</h2>
      <p className="text-gray-600 mb-6">List 2-3 key competitors and what they do. This helps us understand your positioning.</p>
      
      {competitors.map((comp, i) => (
        <div key={i} className="mb-4">
          <input
            type="text"
            value={comp.name}
            onChange={(e) => {
              const newComps = [...competitors];
              newComps[i].name = e.target.value;
              setCompetitors(newComps);
            }}
            placeholder="Competitor name"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-2"
          />
          <input
            type="text"
            value={comp.description}
            onChange={(e) => {
              const newComps = [...competitors];
              newComps[i].description = e.target.value;
              setCompetitors(newComps);
            }}
            placeholder="What they do"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      ))}
      
      <button
        onClick={handleSubmit}
        disabled={!competitors.some(c => c.name.trim()) || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
      >
        {loading ? 'Analyzing...' : 'Next'}
      </button>
    </div>
  );
}

function ClaimsPolicyStep({ onNext }: { onNext: () => void }) {
  const [claims, setClaims] = useState('');

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4">What do you absolutely not say?</h2>
      <p className="text-gray-600 mb-6">List anti-claims, forbidden phrases, or sensitive topics to avoid.</p>
      
      <textarea
        value={claims}
        onChange={(e) => setClaims(e.target.value)}
        placeholder="E.g., 'Avoid marketing-speak, Never claim we are #1, Don't compare to X'"
        className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-6"
      />
      
      <button
        onClick={onNext}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-medium"
      >
        Next
      </button>
    </div>
  );
}

function RuntimeKeyStep({ onNext }: { onNext: () => void }) {
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/runtimes/anthropic/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          
        },
        credentials: 'include',
        body: JSON.stringify({ api_key: apiKey })
      });
      if (res.ok) {
        // Validate the key
        const validateRes = await fetch('/api/runtimes/anthropic/validate', {
          method: 'POST',
          credentials: 'include'
        });
        if (validateRes.ok) {
          onNext();
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4">Connect your first runtime</h2>
      <p className="text-gray-600 mb-6">We need an Anthropic API key to power the engine. Get one at <a href="https://console.anthropic.com" target="_blank" className="text-blue-600">console.anthropic.com</a></p>
      
      <input
        type="password"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="sk-ant-..."
        className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-6"
      />
      
      <button
        onClick={handleSubmit}
        disabled={!apiKey.trim() || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
      >
        {loading ? 'Validating...' : 'Next'}
      </button>
    </div>
  );
}

function StarterProjectStep({ onNext }: { onNext: () => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const templates = [
    { id: 'product-launch', name: 'Product Launch', desc: 'Marketing campaign' },
    { id: 'newsletter', name: 'Weekly Newsletter', desc: 'Recurring content' },
    { id: 'ar-program', name: 'ARR Growth', desc: 'Sales nurture' },
  ];

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await fetch('/api/onboarding/create-starter-project', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          
        },
        credentials: 'include',
        body: JSON.stringify({ template: selected })
      });
      onNext();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4">Pick a starter project</h2>
      <p className="text-gray-600 mb-6">Choose a template or start blank.</p>
      
      <div className="grid grid-cols-1 gap-4 mb-6">
        {templates.map((t) => (
          <div
            key={t.id}
            onClick={() => setSelected(t.id)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition ${
              selected === t.id
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <h3 className="font-semibold">{t.name}</h3>
            <p className="text-sm text-gray-600">{t.desc}</p>
          </div>
        ))}
      </div>

      <div
        onClick={() => setSelected(null)}
        className={`p-4 border-2 rounded-lg cursor-pointer transition ${
          selected === null
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        } mb-6`}
      >
        <h3 className="font-semibold">Start blank</h3>
        <p className="text-sm text-gray-600">Create a project from scratch</p>
      </div>
      
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
      >
        {loading ? 'Creating...' : 'Finish'}
      </button>
    </div>
  );
}

function CompleteStep() {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center">
      <div className="text-4xl mb-4">🎉</div>
      <h2 className="text-2xl font-bold mb-4">You're all set!</h2>
      <p className="text-gray-600">Redirecting to your dashboard...</p>
    </div>
  );
}
