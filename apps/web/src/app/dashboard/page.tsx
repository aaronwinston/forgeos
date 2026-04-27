'use client';
import { QuoteCallout } from '@/components/dashboard/QuoteCallout';
import { HeroSection } from '@/components/dashboard/HeroSection';
import { BriefingBook } from '@/components/dashboard/BriefingBook';
import { ActiveSessions } from '@/components/dashboard/ActiveSessions';
import { NewSessionModal } from '@/components/dashboard/NewSessionModal';
import LetsBuildModal from '@/components/LetsBuildModal';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [showLetsBuildModal, setShowLetsBuildModal] = useState(false);
  const router = useRouter();
  
  const handleLetsBuildSuccess = (deliverable: any) => {
    router.push(`/workspace/${deliverable.id}`);
  };
  
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-4">
          <HeroSection />
          <QuoteCallout />
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowLetsBuildModal(true)} className="bg-blue-600 hover:bg-blue-700">
            ✨ Let's Build
          </Button>
          <Button onClick={() => setShowSessionModal(true)}>+ New Session</Button>
        </div>
      </div>
      
      <ActiveSessions />
      <BriefingBook />
      
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
