import { redirect } from 'next/navigation';

export default function Home() {
  // Server-side redirect: this is safe during SSR/static generation
  redirect('/dashboard');
}
