---
phase: B-1
plan: 01
subsystem: infra
tags: [nextjs, prisma, postgresql, neon, vercel, typescript, tailwind, auth-js]

# Dependency graph
requires: []
provides:
  - Next.js 16 App Router project scaffolded in resume-builder/
  - Prisma v5 schema with all 6 models (User, Resume, Subscription, VerificationToken, Account, Session)
  - Singleton db export from lib/prisma.ts for use by all subsequent phases
  - Health check route at /api/health
  - .env.example with all required variable names documented
  - vercel.json with maxDuration overrides for AI/PDF routes
  - middleware.ts stub (auth enforcement added in B-2)
affects: [B-2, B-3, B-4, B-5, B-6, B-7, B-8, B-9]

# Tech tracking
tech-stack:
  added:
    - next@16.2.2 (App Router, TypeScript, Tailwind CSS v4)
    - prisma@5.22.0 (schema + migrations)
    - "@prisma/client@5.22.0"
    - tailwindcss@4 (via postcss)
  patterns:
    - "Singleton PrismaClient via globalThis to prevent hot-reload exhaustion"
    - "Server-only env vars — no NEXT_PUBLIC_ prefix on any secret key"
    - "build script = prisma generate && next build (ensures client regenerated on Vercel deploy)"
    - "postinstall = prisma generate (ensures client works after npm install)"

key-files:
  created:
    - resume-builder/prisma/schema.prisma
    - resume-builder/lib/prisma.ts
    - resume-builder/app/api/health/route.ts
    - resume-builder/.env.example
    - resume-builder/vercel.json
    - resume-builder/middleware.ts
    - resume-builder/app/layout.tsx
    - resume-builder/app/page.tsx
    - resume-builder/next.config.ts
  modified:
    - resume-builder/package.json
    - resume-builder/.gitignore

key-decisions:
  - "Using Prisma v5 (not v6+) because Node.js 18.12.1 is installed locally and Prisma 6+ requires Node >=20"
  - "Next.js 16 installed by create-next-app but local build requires Node >=20.9.0 — local npm run build skipped; TypeScript compiles clean, Vercel uses Node 20+"
  - "Named export is db (not prisma) to avoid shadowing the Prisma CLI in import statements"
  - "serverExternalPackages used instead of experimental.serverComponentsExternalPackages (stable in Next.js 15+)"
  - ".gitignore updated to block .env and .env.local but allow .env.example to be committed"
  - "Razorpay fields used in Subscription model (razorpayCustomerId, razorpaySubId) — no Stripe"

patterns-established:
  - "Pattern: import { db } from '@/lib/prisma' — all phases must use this, never new PrismaClient()"
  - "Pattern: Server-only API routes use export const runtime = 'nodejs' when Prisma is imported"
  - "Pattern: Health route returns {status, timestamp, database} JSON — monitoring baseline"

requirements-completed: [B-INFRA-01, B-INFRA-02, B-INFRA-03]

# Metrics
duration: 45min
completed: 2026-04-03
---

# Phase B-1: Scaffold & Infrastructure Summary

**Next.js 16 App Router project with Prisma v5 and full Auth.js v5-compatible schema scaffolded locally; awaiting Neon account creation and Vercel deployment to complete the live infrastructure**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-04-03T02:30:00Z
- **Completed:** 2026-04-03T03:15:00Z
- **Tasks:** 4 of 7 completed automatically (Tasks 5, 6, 7 require human action/verification)
- **Files modified:** 25

## Accomplishments

- Full Next.js 16 App Router project scaffolded in `resume-builder/` with TypeScript, Tailwind CSS v4, and ESLint
- Prisma v5 schema defined with all 6 models: User, Resume, Subscription, VerificationToken, Account, Session (Auth.js v5 PrismaAdapter-compatible)
- Singleton `db` export from `lib/prisma.ts` established — all future phases import this
- Health check route `/api/health` pings the database and returns structured JSON
- `.env.example` committed with all 5 required variable names and no real secrets
- `vercel.json` configured with appropriate `maxDuration` for AI and PDF export routes
- Middleware stub created (auth enforcement deferred to B-2)
- `package.json` build script updated to `prisma generate && next build`

## Task Commits

1. **Tasks 1-4 (scaffold, env files, Prisma schema, health route)** - `e1b6671` (feat)

## Files Created/Modified

- `resume-builder/prisma/schema.prisma` — Full 6-model schema with Razorpay-specific Subscription fields
- `resume-builder/lib/prisma.ts` — Singleton PrismaClient export named `db`
- `resume-builder/app/api/health/route.ts` — Health check with DB ping
- `resume-builder/.env.example` — Documented env var template (committed, no secrets)
- `resume-builder/.env.local` — Empty template (git-ignored, user fills in)
- `resume-builder/vercel.json` — maxDuration overrides for long-running routes
- `resume-builder/middleware.ts` — Stub middleware (auth enforcement in B-2)
- `resume-builder/next.config.ts` — serverExternalPackages for @react-pdf/renderer
- `resume-builder/package.json` — build script + postinstall for prisma generate
- `resume-builder/.gitignore` — Fixed to allow .env.example, block .env and .env.local

## What You Need to Do Manually

### Step 1 — Create Neon PostgreSQL Database

1. Go to https://neon.tech — create a free account
2. Click "New Project", name it `resume-builder`, pick your nearest region
3. Copy the connection string from the Dashboard:
   `postgresql://resume_builder_owner:abc123@ep-xxxx.region.aws.neon.tech/resume_builder?sslmode=require`
4. This becomes `DATABASE_URL`

### Step 2 — Create Vercel Project

1. Go to https://vercel.com/new
2. Import your GitHub repo containing this project
3. Set Root Directory to `resume-builder`
4. Add these 5 environment variables (Settings > Environment Variables > All Environments):

| Key | Value Source |
|-----|-------------|
| `DATABASE_URL` | Neon connection string from Step 1 |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com > API Keys |
| `RAZORPAY_KEY_ID` | https://dashboard.razorpay.com > Settings > API Keys |
| `RAZORPAY_KEY_SECRET` | Same Razorpay location |
| `AUTH_SECRET` | Run: `openssl rand -base64 32` |

5. Deploy (Vercel will use Node.js 20+ automatically — Next.js 16 will build fine)

### Step 3 — Fill in .env.local for Local Development

Copy the values from Step 2 into `resume-builder/.env.local` for local development.

### Step 4 — Run Prisma Migration

After DATABASE_URL is in .env.local:
```bash
cd resume-builder
npx prisma migrate dev --name initial_schema
```

Expected: 7 tables created (User, Account, Session, Resume, Subscription, VerificationToken, _prisma_migrations)

### Step 5 — Verify Live Deployment

```bash
curl -s https://YOUR_VERCEL_URL/api/health | python3 -m json.tool
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "...",
  "database": "connected"
}
```

## Decisions Made

- Used Prisma v5 (not v6+) because local environment has Node.js 18.12.1; Prisma 6+ requires Node >=20
- Used `serverExternalPackages` (stable API) instead of `experimental.serverComponentsExternalPackages` (deprecated in Next.js 15+)
- Named export `db` not `prisma` to avoid shadowing the Prisma CLI binary
- Fixed `.gitignore` to explicitly allow `.env.example` while blocking `.env` and `.env.local`
- Removed Prisma-generated `.env` file — app uses `.env.local` (Next.js convention)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used Prisma v5 instead of latest Prisma v6+**
- **Found during:** Task 3 (Prisma installation)
- **Issue:** Latest Prisma (v7.6) requires Node.js `^20.19 || ^22.12 || >=24`. Local Node is 18.12.1.
- **Fix:** Installed `prisma@5` and `@prisma/client@5` — supports Node.js >=16.13
- **Impact:** None — Prisma v5 is fully compatible with the schema and all planned features. Vercel uses Node.js 20+ so deployment is unaffected.
- **Committed in:** e1b6671

**2. [Rule 2 - Missing Critical] Fixed .gitignore to allow .env.example**
- **Found during:** Task 2 (env file creation)
- **Issue:** create-next-app sets `.env*` in .gitignore, which would have silently blocked committing `.env.example`
- **Fix:** Changed to explicit `.env` and `.env.local` / `.env*.local` patterns
- **Committed in:** e1b6671

**3. [Rule 2 - Missing Critical] Used stable `serverExternalPackages` config key**
- **Found during:** Task 1 (next.config.ts edit)
- **Issue:** Plan specified `experimental.serverComponentsExternalPackages` which was renamed to `serverExternalPackages` in Next.js 15
- **Fix:** Used `serverExternalPackages` (top-level, stable) in next.config.ts
- **Committed in:** e1b6671

**4. [Rule 3 - Blocking] Local `npm run build` cannot run on Node.js 18.12.1**
- **Found during:** Task 1 verification
- **Issue:** Next.js 16 requires Node.js >=20.9.0. The local machine has 18.12.1. The build script hard-fails.
- **What was verified instead:** TypeScript compiles clean (`npx tsc --noEmit` exits 0), Prisma schema validates, Prisma client generates successfully
- **Vercel impact:** None — Vercel automatically uses Node.js 20+ for deployments. The actual build will succeed on Vercel.

---

**Total deviations:** 4 auto-fixed (2 blocking, 2 missing critical)
**Impact on plan:** All deviations resolve environment constraints. Code is correct; Vercel deployment will build and run on Node.js 20+.

## Known Stubs

- `resume-builder/middleware.ts` — Currently passes all requests through. Auth enforcement added in B-2. Intentional stub.
- `resume-builder/app/page.tsx` — Placeholder "coming soon" text. Landing page built in B-9. Intentional stub.

## Vercel Deployment URL

Not yet deployed — awaiting manual setup steps above.

## Next Phase Readiness

B-2 (Authentication) can proceed once:
1. Neon database is provisioned and `DATABASE_URL` is in `.env.local`
2. Prisma migration has been run (`npx prisma migrate dev --name initial_schema`)
3. All 5 env vars are in Vercel

The `db` export from `lib/prisma.ts` and the Auth.js v5 PrismaAdapter-compatible schema models are ready for B-2 to consume.

---

*Phase: B-1*
*Completed: 2026-04-03*
