# Project State: Hobby Websites Portfolio

**Last updated:** 2026-04-02
**Status:** Roadmap created — ready to plan first phases

---

## Project Reference

**Core value:** Each website must deliver immediate, no-signup utility to visitors so they return and share — traffic is the foundation of all revenue.

**Workstreams:**
- A1: Everyday Tools Site (Vanilla JS + 11ty, Cloudflare Pages, AdSense)
- A2: SEO/Writing Tools Site (Astro 5.x + Vanilla JS, Cloudflare Pages, AdSense + affiliates)
- B: AI Resume & Cover Letter Builder (Next.js App Router, Vercel, Claude API, Stripe, Auth.js v5)

---

## Current Position

**Active phases:** None started

| Workstream | Current Phase | Status | Next Phase |
|------------|---------------|--------|------------|
| A1 | — | Not started | A1-1: Scaffold & Deploy |
| A2 | — | Not started | A2-1: Scaffold & Deploy |
| B | — | Not started | B-1: Scaffold & Infrastructure |

**Overall progress:** 0/24 phases complete

```
A1 [                    ] 0/7
A2 [                    ] 0/8
B  [                    ] 0/9
```

---

## Performance Metrics

| Metric | A1 | A2 | B |
|--------|----|----|---|
| Phases complete | 0/7 | 0/8 | 0/9 |
| Requirements delivered | 0/21 | 0/24 | 0/21 |
| Plans complete | — | — | — |

---

## Accumulated Context

### Key Decisions Locked In

**A1:**
- Stack: Vanilla JS + 11ty (zero framework runtime shipped to browser)
- Host: Cloudflare Pages (unlimited bandwidth free tier)
- CSS: Hand-crafted plain CSS, inline critical CSS, system font stack
- Ads: Manual ad slot placement with CSS `min-height` reservation before load
- YMYL: Finance (tip, EMI, percentage) and health (BMI, age) tools need disclaimers + formula citations

**A2:**
- Stack: Astro 5.x (Islands Architecture), Tailwind CSS v4, Cloudflare Pages
- Interactivity: Vanilla JS for all tools EXCEPT the diff tool (Preact island, `client:load`)
- Diff: jsdiff (Myers algorithm), Web Worker for inputs > 10K words
- Affiliate: Semrush on SEO tools (keyword density, meta tag, OG, robots.txt, slug); Grammarly on writing tools (word counter, readability, character counter); Writesonic on all pages
- Placement: Contextual affiliate links triggered by tool result, never banner-style

**B:**
- Framework: Next.js 15 App Router (not Pages Router)
- AI: Claude claude-sonnet-4-6 via `@ai-sdk/anthropic` + Vercel AI SDK v6 streaming
- Auth: Auth.js v5 + Resend email provider + Prisma adapter + JWT sessions
- DB: Prisma ORM + Neon PostgreSQL (serverless-compatible)
- PDF: @react-pdf/renderer server-side API route (NOT html2pdf.js — image-based, ATS-incompatible)
- Rate limiting: Upstash Redis `slidingWindow`, keyed by `userId` in Next.js Middleware
- Payments: Stripe Checkout + webhooks only (never grant access from success redirect URL)
- Pricing: $9.99/month flat (undercuts Resume.io ~$30/month, Zety ~$26/month)

### Open Questions

- Verify Ahrefs affiliate program status before including in A2 affiliate links (conflicting sources — check ahrefs.com/affiliates directly)
- Confirm whether Anthropic Structured Outputs supports simultaneous streaming (or requires two-pass: stream for UX, parse structured output on completion)
- Benchmark Neon vs Supabase cold-start latency before B goes to production
- Verify Resend free tier (3,000 emails/month, 100/day) is sufficient at early user counts

### Blockers

None currently.

### Todos

- [ ] Register domains for A1, A2, B
- [ ] Create Cloudflare Pages accounts for A1 and A2
- [ ] Create Vercel project for B
- [ ] Set up Neon PostgreSQL instance for B
- [ ] Apply for Semrush affiliate (Impact platform) before A2 launch
- [ ] Apply for Grammarly affiliate before A2 launch
- [ ] Apply for Writesonic affiliate before A2 launch
- [ ] Verify Ahrefs affiliate status directly

---

## Session Continuity

**To resume work:**
1. Check this file for current phase status
2. Run `/gsd:plan-phase [phase-id]` to plan the next phase in any workstream
3. Workstreams are independent — start any of A1-1, A2-1, or B-1 first

**Suggested start order** (based on value delivered and complexity):
1. A1-1 (simplest scaffold, validates Cloudflare Pages workflow)
2. A2-1 (parallel, validates Astro on Cloudflare Pages)
3. B-1 (most complex, start infrastructure early to unblock B-2 through B-9)

---

*State initialized: 2026-04-02*
