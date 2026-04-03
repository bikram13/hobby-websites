import { NextResponse } from 'next/server'
import { db } from '@/lib/prisma'

// Force Node.js runtime (not Edge) — Prisma requires Node.js
export const runtime = 'nodejs'

export async function GET() {
  try {
    // Ping the database to confirm connectivity.
    // If DATABASE_URL is wrong or Neon is unreachable, this throws.
    await db.$queryRaw`SELECT 1`

    return NextResponse.json(
      {
        status: 'ok',
        timestamp: new Date().toISOString(),
        database: 'connected',
      },
      { status: 200 }
    )
  } catch (error) {
    // Do NOT expose raw error message in production — it may contain DATABASE_URL details
    const message = process.env.NODE_ENV === 'development'
      ? String(error)
      : 'Database connectivity check failed'

    return NextResponse.json(
      {
        status: 'error',
        timestamp: new Date().toISOString(),
        database: 'unreachable',
        detail: message,
      },
      { status: 503 }
    )
  }
}
