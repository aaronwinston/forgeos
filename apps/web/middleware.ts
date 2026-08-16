import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  
  // Allow public paths without middleware
  const publicPaths = ['/', '/_not-found'];
  
  if (publicPaths.includes(pathname)) {
    return NextResponse.next();
  }

  // Check if running in personal mode
  const personalMode = process.env.NEXT_PUBLIC_FORGEOS_MODE === 'personal';

  // In personal mode, redirect signin/signup to dashboard
  if (personalMode) {
    if (pathname === '/auth/signin' || pathname === '/auth/signup') {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
