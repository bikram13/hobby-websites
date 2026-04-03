import { PrismaClient } from '@prisma/client'

// Prevent multiple PrismaClient instances during hot reload in development.
// In production (Vercel), each function invocation gets its own instance,
// which is acceptable for serverless — do NOT attempt connection pooling here.
// Use Neon's built-in connection pooler via DATABASE_URL if pool exhaustion occurs.
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const db =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db
