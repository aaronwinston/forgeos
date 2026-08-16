import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 p-8">
      <h1 className="text-4xl font-bold text-gray-800">404</h1>
      <p className="text-lg text-gray-600">Page not found</p>
      <p className="text-sm text-gray-500">The page you&apos;re looking for doesn&apos;t exist.</p>
      <Link
        href="/dashboard"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >
        Back to dashboard
      </Link>
    </div>
  );
}
