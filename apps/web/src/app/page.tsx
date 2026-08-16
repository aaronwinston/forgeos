'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      // Check if we're in a browser
      if (typeof window !== 'undefined') {
        // Give a small delay to ensure client-side routing
        const timer = setTimeout(() => {
          router.push('/dashboard');
        }, 0);
        return () => clearTimeout(timer);
      }
    }
  }, [mounted, router]);

  return (
    <div className="flex items-center justify-center h-screen w-screen bg-bg-primary">
      <div className="text-center">
        <p className="text-sm text-gray-500">Loading ForgeOS...</p>
      </div>
    </div>
  );
}
