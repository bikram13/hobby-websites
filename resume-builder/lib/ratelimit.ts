import { Ratelimit } from "@upstash/ratelimit"
import { Redis } from "@upstash/redis"

// Free tier: 3 AI generations per day per user
// Falls back to a no-op limiter if Upstash env vars are not set (local dev)
function createRatelimiter() {
  if (!process.env.UPSTASH_REDIS_REST_URL || !process.env.UPSTASH_REDIS_REST_TOKEN) {
    // No-op limiter for local development
    return {
      limit: async (_key: string) => ({ success: true, remaining: 99, reset: 0, limit: 99 }),
    }
  }

  const redis = new Redis({
    url: process.env.UPSTASH_REDIS_REST_URL,
    token: process.env.UPSTASH_REDIS_REST_TOKEN,
  })

  return new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(3, "24 h"),
    analytics: false,
    prefix: "rl:ai",
  })
}

export const aiRatelimit = createRatelimiter()
