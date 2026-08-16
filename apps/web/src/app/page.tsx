import { redirect } from 'next/navigation';

// Make this route dynamic so redirect returns proper response
export const dynamic = 'force-dynamic';

export default function Home() {
  // Server-side redirect: returns 307 response at runtime
  redirect('/dashboard');
}
