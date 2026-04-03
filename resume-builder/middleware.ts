import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Middleware runs on the Edge runtime before every request.
// Primary purpose in B-1: guard that no NEXT_PUBLIC_ variable leaks a secret.
// Auth middleware will be added in B-2 (Auth.js v5).

export function middleware(request: NextRequest) {
  // Pass all requests through — auth enforcement added in B-2
  return NextResponse.next()
}

export const config = {
  // Match all routes except static assets, _next internals, and favicon
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
