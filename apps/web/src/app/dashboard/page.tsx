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

  return (
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
  );
}
