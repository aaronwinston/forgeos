'use client';

import { ReactNode, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    // Check if user has auth cookie by looking for current_org_id cookie
    const checkAuth = () => {
      const orgId = document.cookie.split('; ').find(row => row.startsWith('current_org_id='));
      
      if (orgId) {
        setIsAuthorized(true);
      } else {
        router.push('/auth/signin');
      }
    };
    
    checkAuth();
  }, [router]);

  if (!isAuthorized) {
    return null; // or a loading spinner
  }
  
  return <>{children}</>;
}
