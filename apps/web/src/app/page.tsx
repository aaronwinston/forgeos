'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  // Only run on client side
  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (isClient) {
      // Redirect to dashboard
      router.replace('/dashboard');
    }
  }, [isClient, router]);

  if (!isClient) {
    return (
      <div className="flex items-center justify-center h-screen w-screen">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold">ForgeOS</h1>
          <p className="text-sm text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center h-screen w-screen">
      <div className="text-center space-y-4">
        <h1 className="text-2xl font-bold">ForgeOS</h1>
        <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
      </div>
    </div>
  );
}
