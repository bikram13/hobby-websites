---
phase: B-1
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - resume-builder/package.json
  - resume-builder/tsconfig.json
  - resume-builder/next.config.ts
  - resume-builder/tailwind.config.ts
  - resume-builder/postcss.config.mjs
  - resume-builder/app/layout.tsx
  - resume-builder/app/page.tsx
  - resume-builder/.env.local
  - resume-builder/.env.example
  - resume-builder/.gitignore
  - resume-builder/vercel.json
  - resume-builder/prisma/schema.prisma
  - resume-builder/lib/prisma.ts
  - resume-builder/app/api/health/route.ts
  - resume-builder/middleware.ts
autonomous: false
requirements:
  - B-INFRA-01
  - B-INFRA-02
  - B-INFRA-03

must_haves:
  truths:
    - "Pushing to main triggers an automatic Vercel deploy and produces a live HTTPS URL"
    - "The /api/health route returns HTTP 200 JSON on that live URL with no cold-start errors"
    - "ANTHROPIC_API_KEY, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, DATABASE_URL, and AUTH_SECRET are present as Vercel environment variables and absent from the client-side JS bundle"
    - "Prisma schema defines User, Resume, Subscription, and VerificationToken models"
    - "prisma migrate deploy runs cleanly against Neon PostgreSQL with no errors"
  artifacts:
    - path: "resume-builder/prisma/schema.prisma"
      provides: "Database schema with all four required models"
      contains: "model User"
    - path: "resume-builder/lib/prisma.ts"
      provides: "Singleton PrismaClient for serverless (prevents connection exhaustion)"
    - path: "resume-builder/app/api/health/route.ts"
      provides: "Health check endpoint — verifies serverless API routes work"
      exports: ["GET"]
    - path: "resume-builder/.env.example"
      provides: "Documented required env vars — never contains real secrets"
    - path: "resume-builder/middleware.ts"
      provides: "Server-only guard ensuring NEXT_PUBLIC_ keys contain nothing sensitive"
  key_links:
    - from: "resume-builder/lib/prisma.ts"
      to: "Neon PostgreSQL"
      via: "DATABASE_URL environment variable"
      pattern: "globalThis\\.prisma"
    - from: "resume-builder/app/api/health/route.ts"
      to: "resume-builder/lib/prisma.ts"
      via: "db.$queryRaw"
      pattern: "SELECT 1"
    - from: "Vercel project settings"
      to: "resume-builder/.env.local (local only)"
      via: "Vercel CLI pull or manual dashboard entry"
      pattern: "ANTHROPIC_API_KEY"

user_setup:
  - service: neon
    why: "Serverless PostgreSQL — provides DATABASE_URL for Prisma"
    steps:
      - "Go to https://neon.tech, create a free account"
      - "Create a new project named 'resume-builder'"
      - "Copy the connection string from the Dashboard (format: postgresql://user:password@host/dbname?sslmode=require)"
      - "This becomes DATABASE_URL"
  - service: vercel
    why: "Deployment platform — hosts the Next.js app"
    steps:
      - "Go to https://vercel.com, import the GitHub repo containing the resume-builder directory"
      - "Set Root Directory to 'resume-builder' in project settings"
      - "Add these env vars in Vercel Dashboard > Settings > Environment Variables (all environments):"
      - "  ANTHROPIC_API_KEY — from https://console.anthropic.com"
      - "  RAZORPAY_KEY_ID — from https://dashboard.razorpay.com > Settings > API Keys"
      - "  RAZORPAY_KEY_SECRET — from same Razorpay location"
      - "  DATABASE_URL — the Neon connection string from above"
      - "  AUTH_SECRET — generate with: openssl rand -base64 32"
      - "Trigger a redeploy after adding env vars"
  - service: anthropic
    why: "Claude API key for AI generation (needed in Vercel env, not used until B-4)"
    env_vars:
      - name: ANTHROPIC_API_KEY
        source: "https://console.anthropic.com > API Keys"
  - service: razorpay
    why: "Payment gateway (key stored now, integrated in B-8)"
    env_vars:
      - name: RAZORPAY_KEY_ID
        source: "Razorpay Dashboard > Settings > API Keys"
      - name: RAZORPAY_KEY_SECRET
        source: "Razorpay Dashboard > Settings > API Keys"
---

<objective>
Bootstrap the AI Resume Builder as a Next.js 15 App Router project, connect it to Neon PostgreSQL via Prisma, configure all secret environment variables on Vercel, and verify the live deployment returns a healthy API response.

Purpose: Everything in phases B-2 through B-9 builds on this foundation. Auth, AI generation, payments, and PDF export all require a live Vercel deployment, server-only API routes, and a running database. Getting this right now means every subsequent phase can assume the platform is stable.

Output:
- A deployable Next.js 15 App Router project in the `resume-builder/` directory
- Four Prisma models (User, Resume, Subscription, VerificationToken) migrated to Neon
- Five secret environment variables stored in Vercel (never in source control)
- A live `/api/health` route returning 200 on the Vercel deployment URL
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/Users/bikram/Documents/Claude/.planning/workstreams/resume-builder/ROADMAP.md
@/Users/bikram/Documents/Claude/.planning/workstreams/milestone/REQUIREMENTS.md
@/Users/bikram/Documents/Claude/.planning/research/resume-builder-research.md

<interfaces>
<!-- Key contracts established in this plan that B-2 and later plans consume. -->

From resume-builder/lib/prisma.ts (singleton pattern — MUST use this, not new PrismaClient()):
```typescript
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient }
export const db = globalForPrisma.prisma || new PrismaClient()
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db
```

From resume-builder/prisma/schema.prisma (model shapes used by B-2 Auth.js adapter):
```prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  emailVerified DateTime?
  name          String?
  image         String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  resumes       Resume[]
  subscription  Subscription?
  accounts      Account[]
  sessions      Session[]
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}
```

Environment variables available server-side (never NEXT_PUBLIC_ prefixed):
- process.env.ANTHROPIC_API_KEY
- process.env.RAZORPAY_KEY_ID
- process.env.RAZORPAY_KEY_SECRET
- process.env.DATABASE_URL
- process.env.AUTH_SECRET
</interfaces>
</context>

<tasks>

<!-- ============================================================
     WAVE 1 — Local project scaffold (no external services yet)
     All four tasks are independent and touch different files.
     ============================================================ -->

<task type="auto">
  <name>Task 1: Initialise Next.js 15 App Router project with TypeScript and Tailwind</name>
  <files>
    resume-builder/package.json
    resume-builder/tsconfig.json
    resume-builder/next.config.ts
    resume-builder/tailwind.config.ts
    resume-builder/postcss.config.mjs
    resume-builder/app/layout.tsx
    resume-builder/app/page.tsx
    resume-builder/.gitignore
  </files>
  <action>
    From the repo root, run:

    ```bash
    npx create-next-app@latest resume-builder \
      --typescript \
      --tailwind \
      --eslint \
      --app \
      --src-dir=false \
      --import-alias "@/*" \
      --no-turbopack
    ```

    After scaffold completes, make these targeted edits:

    1. `next.config.ts` — add `output: 'standalone'` is NOT needed for Vercel. However, do add:
       ```typescript
       const nextConfig: NextConfig = {
         experimental: {
           // Required for @react-pdf/renderer in API routes (Phase B-5)
           serverComponentsExternalPackages: ['@react-pdf/renderer'],
         },
       }
       ```
       Do NOT set `runtime: 'edge'` globally — only individual routes will opt in.

    2. `app/layout.tsx` — set metadata title to "AI Resume Builder" and description to "Build ATS-optimised resumes and cover letters with AI in minutes."

    3. `app/page.tsx` — replace the default Next.js boilerplate with a minimal placeholder:
       ```tsx
       export default function HomePage() {
         return (
           <main className="min-h-screen flex items-center justify-center">
             <h1 className="text-2xl font-bold">AI Resume Builder — coming soon</h1>
           </main>
         )
       }
       ```

    4. `.gitignore` — confirm `.env.local` is listed (create-next-app adds it; verify it is there).

    Do NOT install shadcn/ui yet — that belongs in B-3 when the UI is actually built.
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude/resume-builder && npm run build 2>&1 | tail -5</automated>
  </verify>
  <done>
    `npm run build` exits 0 with no TypeScript errors. The `resume-builder/` directory exists with `app/`, `public/`, `package.json`, `tsconfig.json`, `tailwind.config.ts`, and `next.config.ts`.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create environment variable files (.env.local and .env.example)</name>
  <files>
    resume-builder/.env.local
    resume-builder/.env.example
  </files>
  <action>
    Create `resume-builder/.env.example` with placeholder values (this file IS committed to git):

    ```
    # ================================================================
    # AI Resume Builder — Environment Variables
    # Copy this file to .env.local and fill in real values.
    # NEVER commit .env.local to git.
    # ================================================================

    # Anthropic Claude API (server-side only — never NEXT_PUBLIC_)
    ANTHROPIC_API_KEY=sk-ant-...

    # Razorpay Payment Gateway (server-side only)
    # Get from: https://dashboard.razorpay.com > Settings > API Keys
    RAZORPAY_KEY_ID=rzp_test_...
    RAZORPAY_KEY_SECRET=...

    # Neon PostgreSQL connection string (server-side only)
    # Get from: https://neon.tech > Project Dashboard > Connection String
    DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

    # Auth.js secret — generate with: openssl rand -base64 32
    AUTH_SECRET=...

    # Auth.js URL (set to your Vercel deployment URL in production)
    NEXTAUTH_URL=http://localhost:3000
    ```

    Create `resume-builder/.env.local` with the same keys but leave values as empty strings (user fills them in after Neon and Vercel setup):

    ```
    ANTHROPIC_API_KEY=
    RAZORPAY_KEY_ID=
    RAZORPAY_KEY_SECRET=
    DATABASE_URL=
    AUTH_SECRET=
    NEXTAUTH_URL=http://localhost:3000
    ```

    Verify `.gitignore` contains `.env.local` — do NOT add `.env.example` to `.gitignore` because it is safe to commit (contains no real secrets).

    Critical rule enforced here (per B-INFRA-03): No variable carrying a secret may use the `NEXT_PUBLIC_` prefix. `NEXT_PUBLIC_` variables are embedded in the client bundle at build time.
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude/resume-builder && grep -n "NEXT_PUBLIC_" .env.example && echo "FAIL: NEXT_PUBLIC_ found" || echo "PASS: no NEXT_PUBLIC_ secrets"</automated>
  </verify>
  <done>
    `.env.example` is committed to git. `.env.local` exists locally but is git-ignored. Neither file contains a `NEXT_PUBLIC_` prefixed secret. All five required variable names are present in both files.
  </done>
</task>

<task type="auto">
  <name>Task 3: Install Prisma and define the database schema</name>
  <files>
    resume-builder/prisma/schema.prisma
    resume-builder/lib/prisma.ts
    resume-builder/package.json
  </files>
  <action>
    From `resume-builder/`:

    ```bash
    npm install @prisma/client
    npm install -D prisma
    npx prisma init --datasource-provider postgresql
    ```

    Replace the generated `prisma/schema.prisma` entirely with:

    ```prisma
    generator client {
      provider = "prisma-client-js"
    }

    datasource db {
      provider  = "postgresql"
      url       = env("DATABASE_URL")
      // directUrl is used by Prisma Migrate (bypasses connection pooling)
      directUrl = env("DATABASE_URL")
    }

    // -------------------------------------------------------
    // Auth.js v5 required models (PrismaAdapter contract)
    // Do NOT rename or remove fields — adapter depends on them
    // -------------------------------------------------------
    model Account {
      id                String  @id @default(cuid())
      userId            String
      type              String
      provider          String
      providerAccountId String
      refresh_token     String? @db.Text
      access_token      String? @db.Text
      expires_at        Int?
      token_type        String?
      scope             String?
      id_token          String? @db.Text
      session_state     String?

      user User @relation(fields: [userId], references: [id], onDelete: Cascade)

      @@unique([provider, providerAccountId])
    }

    model Session {
      id           String   @id @default(cuid())
      sessionToken String   @unique
      userId       String
      expires      DateTime

      user User @relation(fields: [userId], references: [id], onDelete: Cascade)
    }

    model User {
      id            String    @id @default(cuid())
      email         String    @unique
      emailVerified DateTime?
      name          String?
      image         String?
      createdAt     DateTime  @default(now())
      updatedAt     DateTime  @updatedAt

      accounts     Account[]
      sessions     Session[]
      resumes      Resume[]
      subscription Subscription?
    }

    model VerificationToken {
      identifier String
      token      String   @unique
      expires    DateTime

      @@unique([identifier, token])
    }

    // -------------------------------------------------------
    // Application models
    // -------------------------------------------------------
    model Resume {
      id        String   @id @default(cuid())
      userId    String
      title     String   @default("Untitled Resume")
      content   Json     // Stores the full structured resume data
      template  String   @default("classic") // "classic" | "modern"
      createdAt DateTime @default(now())
      updatedAt DateTime @updatedAt

      user User @relation(fields: [userId], references: [id], onDelete: Cascade)
    }

    model Subscription {
      id                   String    @id @default(cuid())
      userId               String    @unique
      razorpayCustomerId   String?
      razorpaySubId        String?
      status               String    @default("free") // "free" | "active" | "halted" | "cancelled"
      currentPeriodEnd     DateTime?
      createdAt            DateTime  @default(now())
      updatedAt            DateTime  @updatedAt

      user User @relation(fields: [userId], references: [id], onDelete: Cascade)
    }
    ```

    Note on Razorpay fields: The research and REQUIREMENTS both specify Razorpay (not Stripe). The Subscription model uses `razorpayCustomerId` and `razorpaySubId` accordingly. The status values mirror Razorpay subscription lifecycle: `created`, `authenticated`, `active`, `pending`, `halted`, `cancelled`, `completed`, `expired`. For this product only `free`, `active`, `halted`, and `cancelled` are actionable.

    Then create `resume-builder/lib/prisma.ts` with the serverless-safe singleton:

    ```typescript
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
    ```

    Export is named `db` (not `prisma`) to avoid shadowing the `prisma` CLI tool in import statements. All subsequent phases must import from `@/lib/prisma` as `import { db } from '@/lib/prisma'`.
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude/resume-builder && npx prisma validate 2>&1</automated>
  </verify>
  <done>
    `npx prisma validate` exits 0 with no errors. `prisma/schema.prisma` contains all four required models: `User`, `Resume`, `Subscription`, `VerificationToken` (plus `Account` and `Session` required by Auth.js adapter). `lib/prisma.ts` exports `db`.
  </done>
</task>

<task type="auto">
  <name>Task 4: Create the /api/health route and vercel.json configuration</name>
  <files>
    resume-builder/app/api/health/route.ts
    resume-builder/vercel.json
  </files>
  <action>
    Create `resume-builder/app/api/health/route.ts`:

    ```typescript
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
    ```

    Create `resume-builder/vercel.json`:

    ```json
    {
      "functions": {
        "app/api/generate/**": {
          "maxDuration": 60
        },
        "app/api/resume/export": {
          "maxDuration": 30
        }
      }
    }
    ```

    The `maxDuration` overrides apply only on Vercel Pro+. On Hobby tier (10s default), the streaming approach used in B-4 avoids timeout issues. The health route itself always completes well under 10s.

    Do NOT set `maxDuration` on the health route — the 10s default is sufficient and adding it wastes function budget.
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude/resume-builder && npm run build 2>&1 | grep -E "(error|Error|compiled|Route)" | head -20</automated>
  </verify>
  <done>
    `npm run build` includes `/api/health` in the route list with no TypeScript errors. `vercel.json` is valid JSON (verify with `node -e "require('./vercel.json')" && echo valid`).
  </done>
</task>

<!-- ============================================================
     WAVE 2 — Vercel deploy + human setup (requires external accounts)
     Blocked until Task 1-4 are committed and pushed to GitHub.
     ============================================================ -->

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 5: Provision Neon database and add all environment variables to Vercel</name>
  <what-automated>
    Tasks 1-4 have created the full project scaffold locally. The code is ready. This checkpoint handles the external service setup that Claude cannot do (browser-based dashboards, secret key retrieval).
  </what-automated>
  <how-to-complete>
    Complete these steps in order. Do not skip any — the migration in Task 6 and the live check in Task 7 both depend on all env vars being set.

    **Step 1 — Push code to GitHub**
    ```bash
    cd /Users/bikram/Documents/Claude
    git add resume-builder/
    git commit -m "feat(B-1): scaffold Next.js 15 project with Prisma schema"
    git push origin main
    ```

    **Step 2 — Create Neon PostgreSQL database**
    1. Go to https://neon.tech and sign in (or create a free account)
    2. Click "New Project", name it `resume-builder`, choose the region closest to you (or `ap-south-1` for India)
    3. Copy the connection string from the Dashboard — it looks like:
       `postgresql://resume_builder_owner:abc123@ep-xxxx.ap-south-1.aws.neon.tech/resume_builder?sslmode=require`
    4. Save this as `DATABASE_URL`

    **Step 3 — Import project to Vercel**
    1. Go to https://vercel.com/new
    2. Import your GitHub repo
    3. Set "Root Directory" to `resume-builder`
    4. Framework Preset: Next.js (auto-detected)
    5. Do NOT deploy yet — add env vars first

    **Step 4 — Add environment variables in Vercel Dashboard**
    Go to: Project Settings > Environment Variables > Add
    Add ALL FIVE of these (select "All Environments" for each):

    | Key | Value | Where to get it |
    |-----|-------|-----------------|
    | `DATABASE_URL` | your Neon connection string | Step 2 above |
    | `ANTHROPIC_API_KEY` | `sk-ant-...` | https://console.anthropic.com > API Keys |
    | `RAZORPAY_KEY_ID` | `rzp_test_...` | https://dashboard.razorpay.com > Settings > API Keys |
    | `RAZORPAY_KEY_SECRET` | the secret key | same Razorpay location |
    | `AUTH_SECRET` | run `openssl rand -base64 32` in your terminal | generated locally |

    **Step 5 — Deploy**
    Click "Deploy" in Vercel. Wait for the build to succeed.
    Note the deployment URL (e.g., `https://resume-builder-abc.vercel.app`).

    **Step 6 — Update .env.local with your real values**
    Fill in `resume-builder/.env.local` with the same values as above so local development works.
    This file is git-ignored and stays local only.
  </how-to-complete>
  <resume-signal>
    Type "done" when all five env vars are set in Vercel, the deploy has succeeded, and you have the live Vercel URL ready.
    Also paste the Vercel deployment URL so Task 7 can verify it.
  </resume-signal>
</task>

<task type="auto">
  <name>Task 6: Run Prisma migration against Neon PostgreSQL</name>
  <files>
    resume-builder/prisma/migrations/
  </files>
  <action>
    With `DATABASE_URL` now set in `.env.local`, run the initial migration from `resume-builder/`:

    ```bash
    cd /Users/bikram/Documents/Claude/resume-builder

    # Generate Prisma client from schema
    npx prisma generate

    # Create and apply the initial migration
    # The migration name is descriptive and permanent — choose carefully
    npx prisma migrate dev --name initial_schema
    ```

    Expected output: Prisma will print the SQL it is applying, ending with:
    ```
    Your database is now in sync with your schema.
    Generated Prisma Client ...
    ```

    If `DATABASE_URL` is not yet set in `.env.local`, the command fails with a connection error. In that case, complete Task 5 first.

    After migration succeeds, verify the tables were created:

    ```bash
    npx prisma db execute --stdin <<EOF
    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
    EOF
    ```

    Expected tables: `Account`, `Resume`, `Session`, `Subscription`, `User`, `VerificationToken`, `_prisma_migrations`.

    Commit the generated migration:

    ```bash
    git add prisma/migrations/ prisma/schema.prisma
    git commit -m "feat(B-1): add initial Prisma migration against Neon"
    git push origin main
    ```

    On Vercel, subsequent deploys will run `prisma migrate deploy` (not `dev`) automatically if you add it to the build command. Update `package.json` scripts:

    ```json
    "scripts": {
      "build": "prisma generate && next build",
      "postinstall": "prisma generate"
    }
    ```

    The `prisma generate` in build ensures the Prisma client is always regenerated from the schema on every Vercel deploy. `postinstall` covers local `npm install` runs.
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude/resume-builder && npx prisma migrate status 2>&1</automated>
  </verify>
  <done>
    `npx prisma migrate status` shows "Database schema is up to date!" with no pending migrations. All seven expected tables exist in the Neon database. The `prisma/migrations/` directory is committed to git.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 7: Verify live Vercel deployment — health route, HTTPS, and bundle safety</name>
  <what-built>
    Tasks 1-6 have created:
    - A live Next.js 15 App Router deployment on Vercel
    - Five env vars stored as Vercel secrets (never in source)
    - A Prisma schema with four models migrated to Neon
    - A /api/health route that pings the database
  </what-built>
  <how-to-verify>
    Run all three checks. All must pass.

    **Check 1 — Health route returns 200 with DB connected**
    ```bash
    # Replace YOUR_VERCEL_URL with the actual URL from Task 5
    curl -s https://YOUR_VERCEL_URL/api/health | python3 -m json.tool
    ```
    Expected response:
    ```json
    {
      "status": "ok",
      "timestamp": "2026-04-02T...",
      "database": "connected"
    }
    ```
    If you see `"database": "unreachable"`, the DATABASE_URL env var is missing or wrong in Vercel.

    **Check 2 — No secret keys in client bundle**
    ```bash
    # Download the main JS bundle and grep for secret key patterns
    curl -s https://YOUR_VERCEL_URL | grep -o 'src="[^"]*_app[^"]*"' | head -3
    # Then for each JS bundle URL found:
    curl -s https://YOUR_VERCEL_URL/_next/static/chunks/main-*.js | grep -c "sk-ant\|rzp_\|AUTH_SECRET"
    ```
    Expected: `0` — none of the secret values appear in any JS file served to the browser.

    Alternatively, use browser DevTools:
    1. Open the Vercel URL in Chrome
    2. DevTools > Network > Filter: JS
    3. Search (Ctrl+F) in any bundle for: `sk-ant`, `rzp_live`, `rzp_test`, `AUTH_SECRET`
    4. Confirm zero matches

    **Check 3 — HTTPS is active and redirect works**
    ```bash
    curl -I http://YOUR_VERCEL_URL 2>&1 | grep -E "HTTP|Location"
    ```
    Expected: HTTP 308 redirect to the HTTPS URL (Vercel enforces this automatically).

    **Check 4 — Auto-deploy on push (smoke test)**
    Make a trivial change (e.g., update the placeholder text in `app/page.tsx`), push to main, and confirm Vercel triggers a new deployment in the dashboard within 60 seconds.
  </how-to-verify>
  <resume-signal>
    Type "approved" if all four checks pass.
    If any check fails, describe which one and paste the error output — Claude will diagnose and fix.
  </resume-signal>
</task>

</tasks>

<verification>
Phase B-1 is complete when ALL of the following are verifiably true:

1. `curl https://YOUR_VERCEL_URL/api/health` returns HTTP 200 with `"database": "connected"` in the JSON body
2. `npx prisma migrate status` in `resume-builder/` shows no pending migrations
3. `git log --oneline resume-builder/prisma/migrations/` shows at least one committed migration
4. Vercel Dashboard > Project Settings > Environment Variables shows exactly these five keys: `ANTHROPIC_API_KEY`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `DATABASE_URL`, `AUTH_SECRET`
5. Searching any JS bundle served by the Vercel URL for `sk-ant`, `rzp_`, or `AUTH_SECRET` returns zero matches
6. `npm run build` in `resume-builder/` exits 0 with no TypeScript errors
</verification>

<success_criteria>
The phase is done when a developer can:

1. Push any commit to `main` and see it deploy automatically to the live Vercel HTTPS URL
2. Hit `GET /api/health` on that URL and receive `{ "status": "ok", "database": "connected" }`
3. Confirm in Vercel's Environment Variables UI that all five secrets are stored server-side
4. Run `npx prisma migrate status` locally and see "Database schema is up to date!"

These four conditions, taken together, mean the platform is ready for B-2 (Auth) to be built on top.
</success_criteria>

<output>
After completing all tasks, create:
`.planning/workstreams/resume-builder/phases/B-1/B-1-01-SUMMARY.md`

Include:
- Vercel deployment URL
- Which tasks completed automatically vs which required human action
- Any deviations from this plan (e.g., if Neon had a different connection string format)
- Prisma model names confirmed in the database
- Confirmation that all five env vars are set in Vercel
- Any issues encountered and how they were resolved
</output>
