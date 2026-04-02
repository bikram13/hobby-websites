# AI-Powered Resume & Cover Letter Builder — Research

**Domain:** AI-assisted SaaS productivity tool (freemium, $9.99/month paid tier)
**Researched:** 2026-04-02
**Overall Confidence:** MEDIUM-HIGH (most claims verified across multiple sources; some implementation specifics LOW confidence where only one source found)

---

## 1. Next.js + Vercel Architecture for AI SaaS

### Recommended Architecture

**Use Next.js App Router (not Pages Router)** with Vercel's serverless deployment. The App Router enables per-route configuration of timeouts, streaming, and runtime — critical for AI workloads.

**Confidence:** HIGH (Vercel official docs, multiple 2025–2026 guides)

### Serverless Function Timeout Limits

| Plan | Default Timeout | Max Configurable |
|------|----------------|-----------------|
| Hobby | 10 seconds | 60 seconds |
| Pro | 15 seconds | 300 seconds (5 min) |
| Enterprise | 15 seconds | 900 seconds (15 min) |

**Critical:** Claude API calls generating a full resume can easily exceed 10–15 seconds on synchronous responses. You have two options:

**Option A — Streaming (recommended):** Use `streamText` from the Vercel AI SDK. Edge Functions begin streaming within 25 seconds and can continue for up to 300 seconds. Zero timeout issue for users because data flows continuously.

**Option B — Fluid Compute:** Vercel's newer pooled-compute model allows functions up to 800 seconds on Pro/Enterprise. Use this for batch PDF generation, not real-time generation.

For `vercel.json` per-route timeout configuration (Pro+):
```json
{
  "functions": {
    "app/api/generate/**": {
      "maxDuration": 60
    }
  }
}
```

### Rate Limiting Architecture

**Use Upstash Redis + `@upstash/ratelimit`** — the standard serverless rate limiting stack for Next.js. Runs at the Edge (Vercel Middleware), meaning requests are blocked before hitting AI API routes and incurring Claude costs.

Key design: implement rate limiting in `middleware.ts` at the edge, keyed by `userId` (from session) for authenticated users, not by IP. IP-based limits are trivially bypassed and penalize shared networks.

```
Free tier:  3 generations per 24-hour sliding window per userId
Paid tier:  Unlimited (bypass rate limiter, or set 1000/day as a soft cap)
```

Upstash free tier (2025): 500K commands/month — sufficient for early-stage production.

**Algorithm choice:** Use `slidingWindow` not `fixedWindow`. Fixed window allows burst abuse at window boundaries (e.g., 3 requests at 11:59pm + 3 requests at 12:00am = 6 in 2 minutes). Sliding window prevents this.

**Sources:**
- [Securing AI Apps with Rate Limiting — Vercel KB](https://vercel.com/kb/guide/securing-ai-app-rate-limiting)
- [Rate Limiting Next.js API Routes — Upstash Blog](https://upstash.com/blog/nextjs-ratelimiting)
- [Edge Rate Limiting — Upstash Blog](https://upstash.com/blog/edge-rate-limiting)
- [Vercel Functions Limitations](https://vercel.com/docs/functions/limitations)
- [Vercel AI SDK Streaming Guide — LogRocket](https://blog.logrocket.com/nextjs-vercel-ai-sdk-streaming/)

---

## 2. Claude API Prompt Engineering for Resume/Cover Letter Generation

### Structured Output (Native API Feature — HIGH Confidence)

Anthropic launched **Structured Outputs** in public beta on **November 14, 2025**. This is the correct approach for resume/cover letter generation — it compiles your JSON schema into a grammar and enforces it at token generation time, not post-hoc validation.

**Implementation:** Requires beta header `anthropic-beta: structured-outputs-2025-11-13`. Works with claude-sonnet-4-6.

Define schema in Zod (TypeScript):
```typescript
const resumeSchema = z.object({
  summary: z.string(),
  experience: z.array(z.object({
    company: z.string(),
    title: z.string(),
    bullets: z.array(z.string()).max(5),
  })),
  skills: z.array(z.string()),
  education: z.array(z.object({
    institution: z.string(),
    degree: z.string(),
    year: z.string(),
  })),
})
```

**Do not** use JSON mode via prompt instructions alone (e.g., "respond in JSON") — it is unreliable and not schema-enforced. Use native structured outputs.

**Sources:**
- [Structured Outputs — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Hands-On with Anthropic Structured Outputs — Towards Data Science](https://towardsdatascience.com/hands-on-with-anthropics-new-structured-output-capabilities/)
- [Claude Structured Outputs Launch — TechBytes](https://techbytes.app/posts/claude-structured-outputs-json-schema-api/)

### System Prompt Architecture

Claude is trained to receive instructions via the system prompt. Use a four-block structure (Anthropic-recommended):

```
INSTRUCTIONS — How to behave, tone, persona
CONTEXT — User's current resume data, target industry
TASK — What to generate (tailored resume vs cover letter)
OUTPUT FORMAT — Schema reference, length constraints
```

**Proven resume prompt patterns (MEDIUM confidence — multiple community sources, 2025–2026):**

For resume bullet points, use the **CAR framework** (Challenge-Action-Result). Instruct Claude to surface measurable outcomes early. Example system prompt excerpt:

```
You are a professional resume writer specializing in ATS-optimized resumes.
Rewrite the provided experience bullets using the CAR framework (Challenge, Action, Result).
Each bullet must begin with a strong action verb, include a quantifiable metric where possible,
and be no longer than 2 lines. Mirror keywords from the job description without stuffing.
```

For cover letters, instruct Claude to structure as: Hook (why this company) → Value proposition (2-3 specific achievements) → Forward-looking close.

**ATS keyword integration:** Pass both the user's raw resume and the job description in the same prompt. Claude's large context window (200K tokens on claude-sonnet-4-6) allows the entire job posting to be in context simultaneously.

**Token cost management:** For the free tier (3 generations/day), use the full prompt. For high-volume usage monitoring, track `input_tokens` + `output_tokens` from the API response metadata.

**Sources:**
- [Top 25 Claude Resume Prompts 2025 — The Interview Guys](https://blog.theinterviewguys.com/claude-resume-prompts/)
- [Claude AI Resume & Cover Letter Writing — Blockchain Council](https://www.blockchain-council.org/claude-ai/claude-ai-resume-cover-letter-writing-tailoring-ats-keywords-storytelling/)
- [Claude Prompt Engineering Best Practices 2026](https://promptbuilder.cc/blog/claude-prompt-engineering-best-practices-2026)
- [25+ Claude Resume Prompts — EasyFreeResume](https://easyfreeresume.com/blog/claude-resume-prompts)

### Vercel AI SDK Integration

Use `@ai-sdk/anthropic` with the Vercel AI SDK v6.0+ (released late 2025). This provides:
- Unified streaming interface
- Built-in error handling
- `streamText` / `generateObject` functions
- Works in App Router route handlers

```typescript
import { anthropic } from '@ai-sdk/anthropic'
import { streamText } from 'ai'

export async function POST(req: Request) {
  const { resume, jobDescription } = await req.json()

  const result = streamText({
    model: anthropic('claude-sonnet-4-6'),
    system: RESUME_SYSTEM_PROMPT,
    messages: [{ role: 'user', content: `Resume: ${resume}\n\nJob: ${jobDescription}` }],
  })

  return result.toDataStreamResponse()
}
```

**Sources:**
- [Vercel AI SDK Docs](https://ai-sdk.dev/docs/introduction)
- [How to Use Claude with Vercel AI SDK](https://developer.puter.com/tutorials/access-claude-using-vercel-ai-sdk/)

---

## 3. Stripe Checkout + Webhooks for Freemium Subscriptions

### Architecture Pattern

The full Stripe subscription lifecycle for this product:

```
User signs up (free) → hits generation limit →
Stripe Checkout → payment → webhook grants paid access →
Stripe Customer Portal for self-service management
```

**Never grant paid access from the Checkout success page redirect.** The success page can be hit via URL manipulation. Access must be granted only via webhook event `checkout.session.completed`.

### Webhook Events to Handle

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Create subscription record, mark user as paid |
| `customer.subscription.updated` | Handle plan changes, renewals |
| `customer.subscription.deleted` | Downgrade to free tier |
| `invoice.payment_failed` | Send email, lock paid features (grace period recommended) |
| `invoice.payment_succeeded` | Extend subscription period |

**Confidence:** HIGH (Stripe official docs + multiple 2025–2026 implementation guides)

### Implementation Notes

**Idempotency:** Stripe can send the same webhook event multiple times. Use the event `id` as an idempotency key in your database upsert — do not process the same event twice.

**Webhook signature verification:** Always verify `stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET)` before processing. Never trust raw request body without verification.

**Database field on user:** Store `stripe_customer_id`, `stripe_subscription_id`, `subscription_status` ('free' | 'active' | 'past_due' | 'canceled'), and `current_period_end` timestamp.

**Customer Portal:** Use `stripe.billingPortal.sessions.create` to generate a one-time portal URL. The portal handles cancellation, payment method updates, and plan changes without you building UI. By default, plan changes take effect at end of billing period — configure in Stripe Dashboard if you want immediate proration.

**Vercel reference implementation:** The `vercel/nextjs-subscription-payments` GitHub repo is the canonical starting template. It covers Checkout, webhooks, and Customer Portal.

### For $9.99/month Pricing

Create a Stripe Product with a recurring Price of `$9.99 USD / month`. Use `lookup_key` to reference the price in code rather than hardcoding the price ID (price IDs change between environments).

**Sources:**
- [Stripe Subscription Lifecycle in Next.js 2026 — DEV Community](https://dev.to/thekarlesi/stripe-subscription-lifecycle-in-nextjs-the-complete-developer-guide-2026-4l9d)
- [Stripe + Next.js 15 Complete Guide 2025 — Pedro Alonso](https://www.pedroalonso.net/blog/stripe-nextjs-complete-guide-2025/)
- [Vercel Next.js Subscription Payments Template](https://github.com/vercel/nextjs-subscription-payments)
- [Integrate Stripe Customer Portal — Stripe Docs](https://docs.stripe.com/customer-management/integrate-customer-portal)

---

## 4. Email Magic Link Authentication

### Recommended Approach: Auth.js v5 (NextAuth) + Resend

**Why Auth.js v5 over custom JWT:** Lower maintenance surface, handles token generation/expiry/verification, built-in database adapter (Prisma, Drizzle), and free. Custom JWT magic links are viable but require you to implement all edge cases manually (token rotation, expiry, one-time-use enforcement).

**Why Resend over SendGrid/SES for this scale:** Resend is built for developers, has a generous free tier (3,000 emails/month, 100/day), excellent Next.js integration, and is the Anthropic/Vercel ecosystem standard. At SaaS scale you can swap providers by changing one config line.

**Stack:** Auth.js v5 + Resend email provider + Prisma adapter + PostgreSQL (Supabase or Neon for serverless)

**Configuration:**
```typescript
// auth.ts
import NextAuth from 'next-auth'
import Resend from 'next-auth/providers/resend'
import { PrismaAdapter } from '@auth/prisma-adapter'

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    Resend({
      from: 'auth@yourdomain.com',
    }),
  ],
  session: { strategy: 'jwt' }, // or 'database' — see tradeoffs below
})
```

### JWT vs Database Sessions

| Concern | JWT | Database |
|---------|-----|----------|
| Scalability | No DB roundtrip per request | Requires DB query on every request |
| Revocation | Cannot revoke before expiry | Immediate revocation |
| Edge compatibility | Works in Edge Runtime | Requires DB connection (use Neon/PlanetScale) |
| Complexity | Simpler initially | Requires session table |

**Recommendation for this product:** Start with JWT sessions. The 24-hour token expiry is acceptable for a resume tool. Switch to database sessions if you need immediate revocation (e.g., when user cancels subscription, you want to force re-auth).

### Token Security Requirements

- Tokens must be one-time-use (Auth.js enforces this by deleting verification token after use)
- Default expiry: 24 hours (configurable)
- Verification logic must never leave the server — link only contains the token, validation happens server-side
- Store only the hashed token in the database (Auth.js does this by default)

**Sources:**
- [Auth.js — Configuring Resend](https://authjs.dev/guides/configuring-resend)
- [Simple Next.js Magic Link JWT Auth with Prisma and Resend — DEV](https://dev.to/diegocasmo/simple-nextjs-magic-link-jwt-authentication-with-prisma-postgresql-and-resend-21l)
- [NextAuth.js 2025 — Strapi Blog](https://strapi.io/blog/nextauth-js-secure-authentication-next-js-guide)
- [User Auth for Next.js 2025 — Clerk](https://clerk.com/articles/user-authentication-for-nextjs-top-tools-and-recommendations-for-2025)

---

## 5. PDF Export: Library Comparison

### Three Options Evaluated

**Option A: @react-pdf/renderer (RECOMMENDED)**

- Pure JavaScript PDF generation, no browser required
- Works in serverless (Vercel API routes) without extra binaries
- React component syntax for building PDF templates
- Embed selectable text (unlike html2pdf screenshot approach)
- Active maintenance (v4.3.2, updated 2025)
- Limitation: Must maintain separate PDF templates using `@react-pdf/renderer` JSX primitives — cannot reuse your HTML/Tailwind resume templates directly

```typescript
// Server-side in Next.js API route
import { renderToBuffer } from '@react-pdf/renderer'
import ResumePDF from '@/components/ResumePDF'

export async function GET(req: Request) {
  const buffer = await renderToBuffer(<ResumePDF data={resumeData} />)
  return new Response(buffer, {
    headers: { 'Content-Type': 'application/pdf' }
  })
}
```

**Option B: html2pdf.js (NOT recommended for this use case)**

- Client-side only (screenshot-to-PDF approach)
- Non-selectable text in output (image-based)
- Cannot run on the server
- Inconsistent CSS rendering
- Acceptable only as a fallback for simple one-page exports

**Option C: Puppeteer + @sparticuz/chromium-min (HIGH quality, HIGH complexity)**

- Pixel-perfect render of your exact HTML/CSS templates
- Selectable text
- Serverless-compatible via `@sparticuz/chromium-min` (minimized Chromium binary)
- Cold start penalty: ~3-5 seconds for Chromium initialization
- Binary size concern on Vercel (requires `@sparticuz/chromium-min` not full Puppeteer)
- Best for: premium PDF output matching your visual design exactly

**Confidence:** MEDIUM (multiple sources agree on capabilities; serverless Puppeteer complexity is real but the `@sparticuz/chromium-min` workaround is well-documented)

### Recommendation

**Phase 1:** Use `@react-pdf/renderer` for server-side generation. Lower complexity, no binary issues on Vercel.

**Phase 2 (if premium tier demands pixel-perfect exports):** Add Puppeteer-based generation as a premium export option using a dedicated API route with `@sparticuz/chromium-min`.

### ATS Compatibility Note

Both `@react-pdf/renderer` and Puppeteer generate PDFs with selectable, parseable text. This is required for ATS compatibility. Never use html2pdf.js for the primary export — the image-based output fails ATS parsing.

**Sources:**
- [6 Open-Source PDF Libraries for React — DEV Community](https://dev.to/ansonch/6-open-source-pdf-generation-and-modification-libraries-every-react-dev-should-know-in-2025-13g0)
- [Generating PDFs in React — LogRocket](https://blog.logrocket.com/generating-pdfs-react/)
- [Creating a Next.js API to Convert HTML to PDF with Puppeteer (Vercel-Compatible) — DEV](https://dev.to/harshvats2000/creating-a-nextjs-api-to-convert-html-to-pdf-with-puppeteer-vercel-compatible-16fc)
- [HTML to PDF in React with html2pdf.js — Nutrient](https://www.nutrient.io/blog/how-to-convert-html-to-pdf-using-html2df-and-react/)

---

## 6. Resume Template Design Patterns (ATS-Friendly)

### Layout Rules

| Rule | Rationale |
|------|-----------|
| Single-column layout | Multi-column confuses legacy ATS parsers which read left-to-right, merging text across columns |
| Left-aligned text | Universal ATS compatibility |
| No tables for layout | ATS may parse table cells in wrong order |
| No text boxes, graphics, icons | Not parsed by ATS; invisible to automated screening |
| No headers/footers | Some ATS ignore header/footer regions |

**Confidence:** HIGH (consistent across jobscan.co, ATS vendors, career expert sources)

### Typography Constraints

- Body: Arial, Calibri, Cambria, Times New Roman, or Helvetica — 10–12pt
- Section headings: 12–14pt, bold
- Standard section names: "Work Experience" (not "Career Journey"), "Education", "Skills", "Summary"

### Section Order (Proven ATS + Human Reader Pattern)

1. Contact Information (name, email, phone, LinkedIn, location)
2. Professional Summary (3–4 lines)
3. Work Experience (reverse chronological)
4. Education
5. Skills
6. Optional: Certifications, Projects, Volunteer

### HTML/CSS Template Implementation

Use **Tailwind CSS with the `print:` modifier** to create templates that look great on-screen and print correctly. The `print:` variant applies styles only during print/PDF generation.

```html
<div class="max-w-4xl mx-auto p-8 print:p-0 print:max-w-none">
  <h1 class="text-3xl font-bold print:text-2xl">John Doe</h1>
  <div class="grid grid-cols-2 gap-4 print:block">
    <!-- On screen: 2-column, when printed: single column -->
  </div>
</div>
```

For `@react-pdf/renderer` templates, use `StyleSheet.create` with Flexbox — the library uses a subset of CSS/Flexbox properties.

### ATS-Optimized Bullet Point Patterns

```
[Action Verb] + [What You Did] + [Quantified Result]
"Increased sales pipeline by 40% by implementing automated lead scoring using Salesforce"
```

Avoid: passive voice, first person ("I"), buzzwords without specifics ("results-oriented").

**Sources:**
- [ATS Resume Templates — Resume.io](https://resume.io/resume-templates/ats)
- [ATS Resume Format Guide 2026 — IntelligentCV](https://www.intelligentcv.app/career/ats-resume-format-guide/)
- [HTML Resume Template (ATS-Friendly) — GitHub](https://github.com/owengretzinger/html-resume-template)
- [ATS Resume Examples 2026 — Enhancv](https://enhancv.com/resume-examples/ats/)

---

## 7. Competitor Analysis

### Resume.io

| Metric | Detail |
|--------|--------|
| Free tier | 1 resume + 1 cover letter, TXT or basic PDF (1 template only) |
| Trial | $2.95 for 7 days, auto-renews at $29.95 every 4 weeks |
| Quarterly | $49.95 (~$16.65/month) |
| PDF export | Paywalled (key conversion lever) |
| AI features | Built-in content suggestions |
| Complaint | Aggressive auto-renewal, billing transparency issues widely criticized |

**Key insight:** Resume.io locks PDF export behind paywall. Users only discover this after building their resume, which is effective but drives significant negative reviews ("bait and switch" complaints).

### Zety

| Metric | Detail |
|--------|--------|
| Free tier | Full resume creation, PDF download paywalled |
| Trial | $1.95 for 14 days, auto-renews at $25.95 every 4 weeks |
| Annual | $5.95/month ($71.40/year upfront) |
| Strength | Auto-suggestions for experience bullets, clean templates |
| Weakness | Cannot download without paying |

### Kickresume

| Metric | Detail |
|--------|--------|
| Free tier | 4 templates, full resume creation + download |
| Pricing | $9/week, $29/month, $179/year |
| AI features | GPT-4 powered (Forbes "best resume builder 2025") |
| Differentiator | LinkedIn import, 40+ templates, allows free download |
| Strength | More transparent freemium model than Resume.io/Zety |

### Market Positioning Gap

All three incumbents use aggressive free-to-paid friction: build everything, then lock downloads. This generates **significant negative press and user backlash**.

**Opportunity:** A builder that provides genuine value in the free tier (3 AI generations/day + basic PDF export of 1 template) with paid converting on unlimited generations and premium templates will win trust-based acquisition in a market polluted by dark patterns.

**Your $9.99/month price point:** Undercuts Resume.io's effective ~$30/month and Zety's $26/month. Directly competitive with Kickresume's $29/month but positioned as better value. The flat monthly price is cleaner than "weekly" pricing (Kickresume's $9/week = $36/month, deceptive).

**Sources:**
- [Resume.io Pricing — PitchMeAI](https://pitchmeai.com/blog/resume-io-pricing-free-version)
- [Resume.io Full Review 2026](https://pitchmeai.com/blog/resume-io-full-review-pros-cons)
- [Best Zety Alternatives 2026 — PitchMeAI](https://pitchmeai.com/blog/best-zety-alternatives)
- [Kickresume vs Zety Comparison](https://www.kickresume.com/en/help-center/alternative-to-zety/)
- [Top 10 Resume Builders 2026 — LinkedIn](https://www.linkedin.com/pulse/top-10-resume-builders-2025-pros-cons-pricing-tomas-ondrejka-4og3e)

---

## 8. Freemium Conversion Best Practices for AI Tools

### Benchmark Conversion Rates

| Metric | Value | Source |
|--------|-------|--------|
| Average freemium → paid | 2–5% | First Page Sage 2026 report |
| Top-quartile products | 8–15% | First Page Sage 2026 report |
| Organic freemium baseline | ~2.6% | Industry benchmark |
| Interactive demo impact | +65% trial conversion | AMRA & Elma 2025 stats |

**Confidence:** MEDIUM (sourced from research firms, specific numbers vary by product type)

### What Drives Conversion in AI Tools

**1. Time-to-value is the primary lever.** Users who experience a meaningful result within 7–14 days of signup are dramatically more likely to convert. For a resume builder: the first AI-generated resume must feel impressive within the first session.

**2. AI features must be integral, not addons.** If AI is seen as an optional "polish" feature, conversion uplift is muted. Position it as the core mechanism: the product _does not work without AI_, therefore paid = more AI.

**3. Smart usage-based triggers beat time-based trials.** Don't show a paywall after 7 days unconditionally. Show it when a user hits the generation limit mid-session (frustration → high conversion intent). Show it when they try to download a premium template.

**4. The free tier must prove product worth keeping.** Users must experience the AI quality before hitting a limit. 3 generations/day is enough to generate one tailored resume, which is the "aha moment." Do not make the free tier too restrictive (no export at all = abandoned product).

**5. Soft paywall over hard gate.** Show premium templates as visible but locked (blur/lock icon). Let users edit a premium template but require upgrade to download. This is "soft paywall" — users invest time, then upgrade rather than leaving.

### Recommended Conversion Architecture for This Product

```
Free tier "aha moment" funnel:
1. User pastes job description + uploads existing resume
2. Claude generates tailored resume instantly (generation #1 used)
3. User sees quality — they're impressed
4. User wants to try cover letter (generation #2)
5. User hits template they like but it's "Premium"
6. User has 1 generation left — show "You're on the free plan" notice
7. User edits, tries to download in high-quality PDF → upgrade modal
8. Price anchor: "$9.99/month, cancel anytime" vs "you used 3/3 today"
```

**Don't do:** Lock PDF export entirely on free. Let users export basic PDF free (1 template, watermarked is okay). The value demonstration requires them to see the finished product.

**Do:** Lock premium templates, unlimited generations, Word export, and cover letter + resume "matching" (job-specific tailoring) behind paid.

### Email Nurture Sequence (Post-Signup, Pre-Conversion)

Day 0: Welcome + "Here's your resume, share it!" (social proof hook)
Day 2: "Your resume got viewed X times" (engagement metric, even if simulated from profile)
Day 5: "You have 3 generations left today — tailor your resume for [company from job board]"
Day 7: Direct offer email: "$9.99/month — unlimited tailoring for every application"
Day 14: Last-chance discount consideration (test: 1 month for $7.99 for early adopters)

**Sources:**
- [SaaS Freemium Conversion Rates 2026 — First Page Sage](https://firstpagesage.com/seo-blog/saas-freemium-conversion-rates/)
- [Freemium to Paid Conversion Benchmarks — Guru Startups 2025](https://www.gurustartups.com/reports/freemium-to-paid-conversion-rate-benchmarks)
- [Freemium to Premium: Smart Billing Triggers — Kinde](https://www.kinde.com/learn/billing/conversions/freemium-to-premium-converting-free-ai-tool-users-with-smart-billing-triggers/)
- [Freemium Conversion Rate Guide — UserPilot](https://userpilot.com/blog/freemium-conversion-rate/)
- [Freemium Pricing Explained — Stripe](https://stripe.com/resources/more/freemium-pricing-explained)
- [Monetize a Resume Builder App — Local AI Master](https://localaimaster.com/blog/monetize-resume-builder-app)

---

## Recommended Full Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Framework | Next.js 15 (App Router) | SSR + API routes in one deploy, Vercel-native |
| Deployment | Vercel Pro | Required for >10s function timeouts |
| AI | Claude claude-sonnet-4-6 via `@ai-sdk/anthropic` | Specified; large context for full job description |
| AI SDK | Vercel AI SDK v6+ | Streaming, structured output, provider abstraction |
| Auth | Auth.js v5 + Resend (magic links) | Zero-password, developer-friendly, free tier sufficient |
| Database | PostgreSQL via Neon or Supabase | Serverless-compatible, Auth.js adapter support |
| ORM | Prisma | Auth.js adapters, type-safe |
| Payments | Stripe (Checkout + Customer Portal + Webhooks) | Industry standard, good Next.js docs |
| Rate Limiting | Upstash Redis + @upstash/ratelimit | Edge-native, serverless, free tier sufficient |
| PDF Export | @react-pdf/renderer (server-side) | No binaries, selectable text, Vercel-compatible |
| Styling | Tailwind CSS + shadcn/ui | Rapid UI, print modifier for PDF-matching |
| Email (transactional) | Resend | Already used for auth; consistent provider |

### Installation

```bash
# Core
npm install next@latest react react-dom
npm install @anthropic-ai/sdk ai @ai-sdk/anthropic
npm install @auth/prisma-adapter next-auth@beta
npm install @stripe/stripe-js stripe
npm install @react-pdf/renderer

# Database
npm install @prisma/client
npm install -D prisma

# Rate limiting
npm install @upstash/ratelimit @upstash/redis

# UI
npm install tailwindcss @tailwindcss/typography
npx shadcn@latest init

# Email
npm install resend
```

---

## Key Pitfalls to Avoid

### Critical

**1. Granting paid access from Checkout success redirect**
Stripe success page URLs can be manually navigated. Always gate paid features behind webhook-confirmed subscription status in your database. This is the #1 billing exploit in SaaS apps.

**2. Synchronous Claude API calls without streaming on Vercel Hobby**
On Vercel Hobby (10s timeout), a synchronous Claude response for a full resume will likely timeout. Either upgrade to Pro or implement streaming before first public launch. Streaming also provides better UX (user sees text appearing).

**3. Using html2pdf.js for the primary PDF export**
The output is image-based and fails ATS parsing. Users submitting ATS-unreadable resumes will blame your product. Use @react-pdf/renderer or Puppeteer.

**4. Rate limiting by IP address**
Shared networks (offices, universities) will have multiple legitimate users blocked under the same IP. Key rate limits to authenticated userId. For unauthenticated pre-signup exploration, IP is acceptable but set limits generously.

**5. Free tier too restrictive (no export at all)**
Users who cannot see the final product cannot justify upgrading. Let free users export at least one basic PDF. The "paywall at download" model drives negative reviews. Use the generation limit (3/day) as your primary conversion mechanism instead.

### Moderate

**6. Not handling Stripe webhook idempotency**
Stripe retries failed webhooks. Without idempotency checks, you may grant paid access multiple times, send multiple welcome emails, or corrupt subscription state.

**7. Storing raw API keys in Next.js client components**
`ANTHROPIC_API_KEY` and `STRIPE_SECRET_KEY` must only live in server-side code (API routes, Server Actions, Server Components). Never expose to client bundle. Use `NEXT_PUBLIC_` prefix only for genuinely public keys.

**8. Blocking ATS features for "premium templates" only**
ATS optimization (single column, proper sections) should be available on free templates. Differentiating on visual design, not ATS safety, is more ethical and reduces churn from users who got hired.

**9. Ignoring `customer.subscription.deleted` webhook**
If you only handle successful checkout, users who cancel via the Customer Portal will retain paid access indefinitely until you manually check Stripe. Handle subscription lifecycle events from day one.

---

## Open Questions / Gaps

- **Structured Output + Streaming:** Anthropic's structured outputs API (Nov 2025 beta) — verify whether it supports streaming responses simultaneously. If not, you must choose between real-time streaming (better UX) or guaranteed JSON schema (easier parsing). May require a two-pass approach: stream for display, parse structured output on completion.

- **@sparticuz/chromium-min on Vercel:** The exact bundle size limits and cold start times for Puppeteer in Vercel serverless should be verified before committing to it for premium PDF export. May require an external microservice (Fly.io, Railway) for PDF generation rather than Vercel functions.

- **Resend pricing at scale:** Resend free tier is 3,000 emails/month. With magic link auth (1 email per login session) + transactional emails, a 1,000 active user base could exceed this. Verify Resend Pro pricing ($20/month for 50K emails) fits the unit economics.

- **Neon vs Supabase for Prisma + Auth.js:** Both are serverless PostgreSQL options. Neon has better cold-start latency in testing (single-digit ms vs Supabase's ~50ms on hobby tier). Worth benchmarking before production.

- **claude-sonnet-4-6 input token costs at 3 free generations/day:** With a full job description (1,500 tokens) + existing resume (1,000 tokens) + system prompt (500 tokens) = ~3,000 input tokens per generation. At 3/day free × 1,000 free users = 9M input tokens/day. Verify this cost is covered by paid tier revenue at $9.99/month.
