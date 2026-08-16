'use client';
import { QuoteCallout } from '@/components/dashboard/QuoteCallout';
import { HeroSection } from '@/components/dashboard/HeroSection';
import { BriefingBook } from '@/components/dashboard/BriefingBook';
import { EngineHealthCard } from '@/components/dashboard/EngineHealthCard';
import { ActiveSessions } from '@/components/dashboard/ActiveSessions';
import { NewSessionModal } from '@/components/dashboard/NewSessionModal';
import { UpNext } from '@/components/dashboard/UpNext';
import { WelcomeBanner } from '@/components/WelcomeBanner';
import LetsBuildModal from '@/components/LetsBuildModal';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ErrorBoundary from '@/components/ErrorBoundary';

interface DeliverableResult {
  id?: number;
  folder_id?: number;
  content_type?: string;
  title?: string;
  status?: string;
}

export default function DashboardPage() {
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [showLetsBuildModal, setShowLetsBuildModal] = useState(false);
  const router = useRouter();

  const handleLetsBuildSuccess = (deliverable: DeliverableResult) => {
    if (deliverable.id) {
      router.push(`/workspace/${deliverable.id}`);
    }
  };

  const dashboardFallback = (error: Error, reset: () => void) => (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 p-8">
      <h2 className="text-xl font-semibold text-red-600">Dashboard failed to load</h2>
      <p className="text-sm text-gray-500">{error.message}</p>
      <div className="flex gap-3">
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Try again
        </button>
        <a
          href="/dashboard"
          className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
        >
          Reload dashboard
        </a>
      </div>
    </div>
  );

  return (
    <ErrorBoundary fallback={dashboardFallback}>
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Welcome banner */}
      <WelcomeBanner />

      {/* ── Hero + actions ── */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-4">
          <HeroSection />
          <QuoteCallout />
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowLetsBuildModal(true)} className="bg-blue-600 hover:bg-blue-700">
            ✨ Let&apos;s Build
          </Button>
          <Button onClick={() => setShowSessionModal(true)}>+ New session</Button>
        </div>
      </div>

      {/* ── Main content + sidebar ── */}
      <div className="flex gap-8 items-start">
        {/* Main column */}
        <div className="flex-1 min-w-0 space-y-8">
          <EngineHealthCard />
          <ActiveSessions />
          <BriefingBook />
        </div>

        {/* Sidebar: Up Next (7 days) */}
        <aside className="w-80 shrink-0">
          <UpNext />
        </aside>
      </div>

      {showSessionModal && (
        <NewSessionModal
          onClose={() => setShowSessionModal(false)}
          onCreated={() => setShowSessionModal(false)}
        />
      )}

      {showLetsBuildModal && (
        <LetsBuildModal
          isOpen={showLetsBuildModal}
          onClose={() => setShowLetsBuildModal(false)}
          onSuccess={handleLetsBuildSuccess}
        />
      )}
    </div>
    </ErrorBoundary>
  );
}
