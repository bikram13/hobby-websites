# Roadmap: Hobby Websites Portfolio

**Generated:** 2026-04-02
**Granularity:** Fine
**Workstreams:** A1 (Everyday Tools), A2 (SEO/Writing Tools), B (AI Resume Builder)
**Total Phases:** 24 (7 × A1, 8 × A2, 9 × B)
**Coverage:** 47/47 v1 requirements mapped

---

## Phases

### Workstream A1 — Everyday Tools Site

- [ ] **A1-1: Scaffold & Deploy** — Vanilla JS + 11ty project on Cloudflare Pages, homepage shell, category URL architecture
- [ ] **A1-2: Finance Tools** — Tip calculator, percentage calculator, loan/EMI calculator with YMYL disclaimers
- [ ] **A1-3: Health & Conversion Tools** — BMI calculator, age calculator, unit converter with YMYL disclaimers
- [ ] **A1-4: Utility Tools** — Time zone converter, random number / password generator
- [ ] **A1-5: SEO Foundation** — Unique meta tags, JSON-LD (WebApplication + FAQPage + BreadcrumbList), sitemap.xml, robots.txt, canonical tags
- [ ] **A1-6: AdSense Integration** — Ad slots with CSS-reserved dimensions (CLS prevention), hybrid manual + auto placement
- [ ] **A1-7: UI Polish & Performance** — Dark/light mode, mobile refinement, Lighthouse ≥ 85 verification, inline critical CSS

### Workstream A2 — SEO / Writing Tools Site

- [ ] **A2-1: Scaffold & Deploy** — Astro 5.x project on Cloudflare Pages, Tailwind CSS v4, homepage with category filters
- [ ] **A2-2: Writing Tools Batch 1** — Word counter, character counter (with/without spaces), readability checker (Flesch-Kincaid)
- [ ] **A2-3: Writing Tools Batch 2** — Case converter, lorem ipsum generator
- [ ] **A2-4: Text Diff Tool** — Preact island, jsdiff Myers algorithm, Web Worker for large inputs, side-by-side / unified view
- [ ] **A2-5: SEO Tools Batch 1** — Keyword density checker (stopword filtering, TF-IDF context), meta tag generator, URL slug generator
- [ ] **A2-6: SEO Tools Batch 2** — Open Graph tag generator (live preview), robots.txt generator (disallow-all warning)
- [ ] **A2-7: SEO & Revenue Layer** — JSON-LD per page, sitemap.xml, AdSense slots (CLS prevention), contextual affiliate links (Semrush, Grammarly, Writesonic)
- [ ] **A2-8: UI Polish & Performance** — Dark/light mode, real-time processing UX, copy-to-clipboard, Lighthouse ≥ 85 verification

### Workstream B — AI Resume & Cover Letter Builder

- [ ] **B-1: Scaffold & Infrastructure** — Next.js 15 App Router on Vercel, environment variable management, Prisma + Neon PostgreSQL schema
- [ ] **B-2: Authentication** — Auth.js v5 with Resend magic link, JWT sessions, session persistence across refresh
- [ ] **B-3: Resume Builder UI** — Structured form (contact, summary, experience, education, skills), live preview, 2 ATS-friendly templates
- [ ] **B-4: AI Resume Generation** — Claude claude-sonnet-4-6 via Vercel AI SDK streaming, structured outputs (Zod schema), CAR-framework bullet generation
- [ ] **B-5: PDF Export** — @react-pdf/renderer server-side API route, selectable text (ATS-compatible), downloadable PDF
- [ ] **B-6: Cover Letter Builder** — Job input form (title, company, description, background), AI generation with streaming, inline editing, PDF + plain text export
- [ ] **B-7: Freemium & Rate Limiting** — Upstash Redis sliding window (3 generations/day free, userId-keyed), localStorage free-tier tracking, paywall trigger UX
- [ ] **B-8: Stripe Payments** — $9.99/month Stripe Checkout, webhook lifecycle (completed, updated, deleted, payment_failed), Customer Portal, idempotency
- [ ] **B-9: Landing Page & SEO** — Value proposition landing page, CTA, meta + OG tags on all public pages, About/Privacy Policy/Contact (AdSense-ready signals)

---

## Phase Details

### Phase A1-1: Scaffold & Deploy
**Goal**: The A1 site is live on Cloudflare Pages with a homepage, category URL architecture, and automated deploys from git
**Depends on**: Nothing
**Requirements**: A1-INFRA-01, A1-INFRA-02, A1-INFRA-03
**Success Criteria** (what must be TRUE):
  1. Pushing to main deploys automatically to a live Cloudflare Pages URL with HTTPS
  2. The homepage renders a list of tool categories with working links
  3. Each tool has its own clean URL slug (e.g., `/tip-calculator`) that returns a 200
  4. The site uses 11ty (or plain HTML with shared header/footer) and ships zero framework runtime JavaScript
**Plans**: TBD
**UI hint**: yes

### Phase A1-2: Finance Tools
**Goal**: Users can perform tip, percentage, and loan/EMI calculations instantly in the browser, with YMYL disclaimers and formula explanations
**Depends on**: A1-1
**Requirements**: A1-TOOL-01, A1-TOOL-05, A1-TOOL-06
**Success Criteria** (what must be TRUE):
  1. Tip calculator accepts bill amount, tip percentage, and split count, then shows per-person amount
  2. Percentage calculator handles three modes: X% of Y, X is what % of Y, percentage change
  3. Loan/EMI calculator accepts principal, rate, and tenure and shows the correct monthly payment using the standard amortization formula
  4. Each finance tool page includes a disclaimer ("Results are estimates only") and cites the formula source
  5. All calculations run client-side with no page reload
**Plans**: TBD

### Phase A1-3: Health & Conversion Tools
**Goal**: Users can calculate BMI, exact age, and unit conversions, with health tools carrying YMYL disclaimers
**Depends on**: A1-1
**Requirements**: A1-TOOL-02, A1-TOOL-03, A1-TOOL-04
**Success Criteria** (what must be TRUE):
  1. BMI calculator accepts height and weight (metric and imperial) and returns BMI score, category, and healthy weight range
  2. Age calculator accepts a date of birth and returns exact age in years, months, and days as of today
  3. Unit converter handles length, weight, temperature, and volume with bidirectional input
  4. BMI calculator displays a disclaimer: "This tool provides general information only and is not medical advice"
**Plans**: TBD
**UI hint**: yes

### Phase A1-4: Utility Tools
**Goal**: Users can convert times across time zones and generate random numbers or secure passwords
**Depends on**: A1-1
**Requirements**: A1-TOOL-07, A1-TOOL-08
**Success Criteria** (what must be TRUE):
  1. Time zone converter lets a user pick a source time and zone and see the equivalent in multiple major target zones simultaneously
  2. Random number generator produces a number within a user-specified min/max range
  3. Password generator produces a random password with configurable length, and options for uppercase, numbers, and symbols
  4. All outputs update immediately on input change with no submit button required
**Plans**: TBD

### Phase A1-5: SEO Foundation
**Goal**: Every tool page is fully indexed by Google with unique metadata, structured data, sitemap, and correct robots configuration
**Depends on**: A1-2, A1-3, A1-4
**Requirements**: A1-SEO-01, A1-SEO-02, A1-SEO-03, A1-SEO-04
**Success Criteria** (what must be TRUE):
  1. Every tool page has a unique `<title>` (under 60 chars), `<meta description>` (150–160 chars), and Open Graph tags
  2. Every tool page has valid WebApplication, FAQPage, and BreadcrumbList JSON-LD that passes Google's Rich Results Test
  3. `/sitemap.xml` is present, lists all tool pages, and is submitted to Google Search Console
  4. `robots.txt` blocks no valid tool pages and is accessible at `/robots.txt`
  5. A `<link rel="canonical">` is present on every page to prevent duplicate URL indexing
**Plans**: TBD

### Phase A1-6: AdSense Integration
**Goal**: AdSense ad slots are live on all tool pages with CSS-reserved dimensions that prevent Cumulative Layout Shift
**Depends on**: A1-5
**Requirements**: A1-REV-01
**Success Criteria** (what must be TRUE):
  1. Each tool page has 2–3 manually placed ad slots (below tool result, mid-content, pre-footer) with `min-height` CSS reservation before ad load
  2. CLS score remains below 0.05 after AdSense scripts load (verified in Lighthouse)
  3. AdSense script loads with `async` and ad slots below the fold use lazy loading
  4. No ad slot appears above the tool on mobile; the tool is always the first interactive element visible
**Plans**: TBD

### Phase A1-7: UI Polish & Performance
**Goal**: The site passes Lighthouse ≥ 85 on mobile, has a working dark/light mode, and every page uses the system font stack with inline critical CSS
**Depends on**: A1-6
**Requirements**: A1-INFRA-04, A1-UI-01, A1-UI-02, A1-UI-03, A1-UI-04
**Success Criteria** (what must be TRUE):
  1. Lighthouse mobile performance score is ≥ 85 on every tool page (measured after AdSense is active)
  2. Dark/light mode toggle persists user preference across sessions via localStorage
  3. All pages are usable on a 375px-wide screen with one-thumb operation of every tool
  4. No login prompt, cookie consent banner, or signup wall appears anywhere on the site
  5. Pages use system font stack; no Google Fonts CDN request is made
**Plans**: TBD
**UI hint**: yes

---

### Phase A2-1: Scaffold & Deploy
**Goal**: The A2 site is live on Cloudflare Pages built with Astro 5.x, Tailwind CSS v4, a homepage with tool categories and filters, and automated git deploys
**Depends on**: Nothing
**Requirements**: A2-INFRA-01, A2-INFRA-02, A2-INFRA-03
**Success Criteria** (what must be TRUE):
  1. Pushing to main deploys automatically to a Cloudflare Pages URL with HTTPS
  2. The homepage renders a filterable directory of tools by category (Writing, SEO)
  3. Each tool has its own clean URL slug that returns pre-rendered static HTML (verified via view-source)
  4. `astro build` output contains zero framework runtime JS on non-interactive pages
**Plans**: TBD
**UI hint**: yes

### Phase A2-2: Writing Tools Batch 1
**Goal**: Users can count words and characters and check readability of any pasted text with real-time results and no page reload
**Depends on**: A2-1
**Requirements**: A2-WRITE-01, A2-WRITE-02, A2-WRITE-03
**Success Criteria** (what must be TRUE):
  1. Word counter shows word count, character count, sentence count, paragraph count, and estimated reading time as the user types
  2. Character counter displays count both with and without spaces, updating in real-time
  3. Readability checker returns Flesch Reading Ease score, Flesch-Kincaid Grade Level, and a plain-language interpretation (e.g., "8th grade — Standard journalism")
  4. All three tools process a 5,000-word paste without visible lag (INP < 200ms)
**Plans**: TBD
**UI hint**: yes

### Phase A2-3: Writing Tools Batch 2
**Goal**: Users can convert text case and generate lorem ipsum placeholder text
**Depends on**: A2-1
**Requirements**: A2-WRITE-04, A2-WRITE-06
**Success Criteria** (what must be TRUE):
  1. Case converter transforms input text into UPPER CASE, lower case, Title Case, camelCase, and snake_case with one click each
  2. Lorem ipsum generator produces configurable output by paragraphs, words, or sentences
  3. Both tools have a copy-to-clipboard button on their output
**Plans**: TBD
**UI hint**: yes

### Phase A2-4: Text Diff Tool
**Goal**: Users can compare two texts side-by-side with word-level differences highlighted, powered by a Preact island and jsdiff running in a Web Worker for large inputs
**Depends on**: A2-1
**Requirements**: A2-WRITE-05
**Success Criteria** (what must be TRUE):
  1. User pastes two texts and sees added words highlighted green and removed words highlighted red with strikethrough
  2. A statistics bar shows: X words added, Y words removed, Z words unchanged
  3. View toggles between side-by-side (desktop) and unified (mobile) layouts
  4. A 10,000-word diff completes without blocking the UI (Web Worker offloads processing)
  5. The diff tool is a Preact island (`client:load`); no Preact runtime loads on other A2 pages
**Plans**: TBD
**UI hint**: yes

### Phase A2-5: SEO Tools Batch 1
**Goal**: Users can analyze keyword density in their content, generate optimized meta tags, and create SEO-friendly URL slugs
**Depends on**: A2-1
**Requirements**: A2-SEO-TOOL-01, A2-SEO-TOOL-02, A2-SEO-TOOL-03
**Success Criteria** (what must be TRUE):
  1. Keyword density checker strips stopwords and shows the top meaningful keywords with frequency percentage, flagging over- or under-optimized terms
  2. Meta tag generator produces a `<title>` and `<meta description>` preview with character counters and a live SERP snippet preview
  3. URL slug generator converts any input text into an SEO-friendly lowercase-hyphenated slug, stripping special characters
  4. All three tools have copy-to-clipboard on their outputs
**Plans**: TBD
**UI hint**: yes

### Phase A2-6: SEO Tools Batch 2
**Goal**: Users can generate Open Graph meta tags with a live social preview and create a robots.txt file with a safety warning for destructive rules
**Depends on**: A2-1
**Requirements**: A2-SEO-TOOL-04, A2-SEO-TOOL-05
**Success Criteria** (what must be TRUE):
  1. Open Graph generator produces all required `og:` tags and renders a live CSS-styled preview showing how the link will appear on Twitter/X and Facebook
  2. Robots.txt generator detects `Disallow: /` patterns and displays a prominent warning before the user copies the output
  3. Both tools produce copy-to-clipboard output
**Plans**: TBD
**UI hint**: yes

### Phase A2-7: SEO & Revenue Layer
**Goal**: Every tool page is fully indexed, has structured data, and carries contextual affiliate links and AdSense slots with CLS prevention
**Depends on**: A2-2, A2-3, A2-4, A2-5, A2-6
**Requirements**: A2-SEO-01, A2-SEO-02, A2-SEO-03, A2-REV-01, A2-REV-02
**Success Criteria** (what must be TRUE):
  1. Every tool page has a unique meta title, description, and Open Graph tags (distinct from the OG generator tool itself)
  2. Every tool page has valid JSON-LD (WebApplication + FAQPage + BreadcrumbList) passing Google's Rich Results Test
  3. `/sitemap.xml` lists all tool pages and is submitted to Google Search Console
  4. AdSense ad slots are live with CSS `min-height` reservation; CLS remains < 0.05 after ads load
  5. Contextual affiliate recommendations appear below tool results (Grammarly on writing tools, Semrush on SEO tools, Writesonic on content tools) — never inside the tool interface
**Plans**: TBD

### Phase A2-8: UI Polish & Performance
**Goal**: The site passes Lighthouse ≥ 85 on mobile, has dark/light mode, real-time UX on all text tools, and copy-to-clipboard on all outputs
**Depends on**: A2-7
**Requirements**: A2-INFRA-04, A2-UI-01, A2-UI-02, A2-UI-03, A2-UI-04
**Success Criteria** (what must be TRUE):
  1. Lighthouse mobile performance score is ≥ 85 on every tool page (measured after AdSense is active)
  2. Dark/light mode toggle persists across sessions via localStorage
  3. All counter and converter tools update output as the user types — no submit button required
  4. Every tool output has a working copy-to-clipboard button with visual confirmation ("Copied!")
  5. All pages are usable on a 375px-wide screen
**Plans**: TBD
**UI hint**: yes

---

### Phase B-1: Scaffold & Infrastructure
**Goal**: The Next.js App Router project is live on Vercel, environment variables are managed, and the Prisma schema with Neon PostgreSQL is provisioned and migrated
**Depends on**: Nothing
**Requirements**: B-INFRA-01, B-INFRA-02, B-INFRA-03
**Success Criteria** (what must be TRUE):
  1. Pushing to main deploys to a live Vercel URL with HTTPS and serverless API routes active
  2. `ANTHROPIC_API_KEY`, `STRIPE_SECRET_KEY`, `DATABASE_URL`, and `AUTH_SECRET` are stored as Vercel environment variables and never appear in the client bundle
  3. Prisma schema is defined with `User`, `Resume`, `Subscription`, and `VerificationToken` models and migration runs cleanly against Neon PostgreSQL
  4. A test API route (`/api/health`) returns 200 with no cold-start errors on Vercel Hobby tier
**Plans**: TBD

### Phase B-2: Authentication
**Goal**: Users can sign in via email magic link, stay signed in across browser refresh, and have their session correctly identify them in server components and API routes
**Depends on**: B-1
**Requirements**: B-AUTH-01, B-AUTH-02, B-AUTH-03
**Success Criteria** (what must be TRUE):
  1. User enters their email on the sign-in page and receives a magic link email from Resend within 30 seconds
  2. Clicking the magic link signs the user in and redirects to their dashboard; the link cannot be used a second time
  3. Refreshing the browser preserves the session (JWT strategy, 24-hour expiry)
  4. User's saved resumes are associated with their account and inaccessible to unauthenticated requests
**Plans**: TBD
**UI hint**: yes

### Phase B-3: Resume Builder UI
**Goal**: Authenticated users can fill a structured resume form and see a live preview update in real-time, with two selectable ATS-friendly templates
**Depends on**: B-2
**Requirements**: B-RES-01, B-RES-03, B-RES-05
**Success Criteria** (what must be TRUE):
  1. The resume form has clearly labeled sections: contact info, professional summary, work experience (multi-entry), education (multi-entry), and skills
  2. The live preview panel updates instantly as the user types into any form field
  3. The user can toggle between at least two visual templates (Classic and Modern) and the preview re-renders immediately
  4. The form state persists in the database when the user navigates away and returns
**Plans**: TBD
**UI hint**: yes

### Phase B-4: AI Resume Generation
**Goal**: Users can trigger AI improvement of any resume section and see the result stream in real-time via the Vercel AI SDK, with Claude generating structured, ATS-optimized content
**Depends on**: B-3
**Requirements**: B-RES-02
**Success Criteria** (what must be TRUE):
  1. Clicking "Improve with AI" on any section sends the existing content to Claude claude-sonnet-4-6 and streams the improved text into the preview in real-time (text appears progressively, not all at once)
  2. Experience bullet points generated by Claude use the CAR framework (Challenge-Action-Result) and begin with action verbs
  3. The Claude API key is never exposed to the browser — all calls go through a Next.js API route
  4. A failed or timed-out generation shows a user-friendly error message and does not corrupt the existing form state
**Plans**: TBD

### Phase B-5: PDF Export
**Goal**: Users can download their resume as an ATS-compatible PDF with selectable text, generated server-side via @react-pdf/renderer
**Depends on**: B-3
**Requirements**: B-RES-04
**Success Criteria** (what must be TRUE):
  1. Clicking "Download PDF" triggers a server-side render via `@react-pdf/renderer` and downloads a `.pdf` file
  2. The PDF contains selectable, copy-pasteable text (not an image) — verified by selecting text in a PDF viewer
  3. The PDF accurately reflects the current template and form content
  4. The API route `/api/resume/export` handles the generation without timing out on Vercel Hobby (under 10 seconds)
**Plans**: TBD

### Phase B-6: Cover Letter Builder
**Goal**: Users can input a job description and their background, receive a tailored AI-generated cover letter via streaming, edit it inline, and export it as PDF or plain text
**Depends on**: B-4, B-5
**Requirements**: B-CVR-01, B-CVR-02, B-CVR-03, B-CVR-04
**Success Criteria** (what must be TRUE):
  1. The cover letter form accepts job title, company name, job description text, and a summary of the user's background
  2. Clicking "Generate" streams the cover letter text in real-time using the same Vercel AI SDK pattern as resume generation
  3. The generated text is editable inline (contenteditable or a textarea that pre-fills with the output)
  4. User can regenerate with one click to get a new variation
  5. "Download PDF" and "Copy as Plain Text" both work on the final cover letter content
**Plans**: TBD
**UI hint**: yes

### Phase B-7: Freemium & Rate Limiting
**Goal**: Free users are limited to 3 AI generations per 24-hour sliding window (keyed by userId via Upstash Redis), and the paywall triggers at the right moment in the user journey
**Depends on**: B-2
**Requirements**: B-PAY-01
**Success Criteria** (what must be TRUE):
  1. An authenticated free-tier user who makes 3 AI generation requests within 24 hours receives a 429 response on the fourth request
  2. The rate limit uses a sliding window (not fixed window) via `@upstash/ratelimit`, keyed by `userId`, evaluated in Next.js Middleware before the Claude API route is reached
  3. The paywall modal appears mid-session at the generation limit — not as a separate page — showing "$9.99/month, cancel anytime"
  4. Paid users bypass the rate limiter entirely
  5. An unauthenticated user attempting generation is redirected to sign in (not rate-limited to 0)
**Plans**: TBD

### Phase B-8: Stripe Payments
**Goal**: Users can upgrade to the $9.99/month paid tier via Stripe Checkout, manage their subscription via the Customer Portal, and paid access is granted/revoked exclusively via webhook events
**Depends on**: B-7
**Requirements**: B-PAY-02, B-PAY-03, B-PAY-04
**Success Criteria** (what must be TRUE):
  1. Clicking "Upgrade" opens a Stripe Checkout session for a $9.99/month recurring subscription
  2. After successful payment, the `checkout.session.completed` webhook updates the user's `subscription_status` to `active` in the database — the Checkout success redirect URL alone grants nothing
  3. A user who cancels via the Stripe Customer Portal has their `subscription_status` set to `canceled` on `customer.subscription.deleted` webhook, losing paid access at period end
  4. `invoice.payment_failed` locks paid features with a grace period notification
  5. All webhook events are idempotent (re-processing the same event ID produces no side effects)
**Plans**: TBD

### Phase B-9: Landing Page & SEO
**Goal**: The public landing page communicates the product's value proposition clearly, converts visitors to sign-ups, and all public pages have complete meta and Open Graph tags
**Depends on**: B-8
**Requirements**: B-SEO-01, B-SEO-02
**Success Criteria** (what must be TRUE):
  1. The landing page (`/`) includes a headline, value proposition, feature highlights, pricing section ($9.99/month), and a primary CTA ("Try Free")
  2. Every public page has a unique `<title>`, `<meta description>`, and complete `og:` tags
  3. The landing page has an About section, a Privacy Policy page, and a Contact page — sufficient for AdSense application and trust signals
  4. The CTA converts: an unauthenticated visitor who clicks "Try Free" reaches the sign-in page in one step
**Plans**: TBD
**UI hint**: yes

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| A1-1: Scaffold & Deploy | 0/? | Not started | - |
| A1-2: Finance Tools | 0/? | Not started | - |
| A1-3: Health & Conversion Tools | 0/? | Not started | - |
| A1-4: Utility Tools | 0/? | Not started | - |
| A1-5: SEO Foundation | 0/? | Not started | - |
| A1-6: AdSense Integration | 0/? | Not started | - |
| A1-7: UI Polish & Performance | 0/? | Not started | - |
| A2-1: Scaffold & Deploy | 0/? | Not started | - |
| A2-2: Writing Tools Batch 1 | 0/? | Not started | - |
| A2-3: Writing Tools Batch 2 | 0/? | Not started | - |
| A2-4: Text Diff Tool | 0/? | Not started | - |
| A2-5: SEO Tools Batch 1 | 0/? | Not started | - |
| A2-6: SEO Tools Batch 2 | 0/? | Not started | - |
| A2-7: SEO & Revenue Layer | 0/? | Not started | - |
| A2-8: UI Polish & Performance | 0/? | Not started | - |
| B-1: Scaffold & Infrastructure | 0/? | Not started | - |
| B-2: Authentication | 0/? | Not started | - |
| B-3: Resume Builder UI | 0/? | Not started | - |
| B-4: AI Resume Generation | 0/? | Not started | - |
| B-5: PDF Export | 0/? | Not started | - |
| B-6: Cover Letter Builder | 0/? | Not started | - |
| B-7: Freemium & Rate Limiting | 0/? | Not started | - |
| B-8: Stripe Payments | 0/? | Not started | - |
| B-9: Landing Page & SEO | 0/? | Not started | - |

---

## Requirement Coverage Map

### Workstream A1

| Requirement | Phase | Status |
|-------------|-------|--------|
| A1-INFRA-01 | A1-1 | Pending |
| A1-INFRA-02 | A1-1 | Pending |
| A1-INFRA-03 | A1-1 | Pending |
| A1-INFRA-04 | A1-7 | Pending |
| A1-TOOL-01 | A1-2 | Pending |
| A1-TOOL-02 | A1-3 | Pending |
| A1-TOOL-03 | A1-3 | Pending |
| A1-TOOL-04 | A1-3 | Pending |
| A1-TOOL-05 | A1-2 | Pending |
| A1-TOOL-06 | A1-2 | Pending |
| A1-TOOL-07 | A1-4 | Pending |
| A1-TOOL-08 | A1-4 | Pending |
| A1-SEO-01 | A1-5 | Pending |
| A1-SEO-02 | A1-5 | Pending |
| A1-SEO-03 | A1-5 | Pending |
| A1-SEO-04 | A1-5 | Pending |
| A1-REV-01 | A1-6 | Pending |
| A1-UI-01 | A1-7 | Pending |
| A1-UI-02 | A1-7 | Pending |
| A1-UI-03 | A1-7 | Pending |
| A1-UI-04 | A1-7 | Pending |

### Workstream A2

| Requirement | Phase | Status |
|-------------|-------|--------|
| A2-INFRA-01 | A2-1 | Pending |
| A2-INFRA-02 | A2-1 | Pending |
| A2-INFRA-03 | A2-1 | Pending |
| A2-INFRA-04 | A2-8 | Pending |
| A2-WRITE-01 | A2-2 | Pending |
| A2-WRITE-02 | A2-2 | Pending |
| A2-WRITE-03 | A2-2 | Pending |
| A2-WRITE-04 | A2-3 | Pending |
| A2-WRITE-05 | A2-4 | Pending |
| A2-WRITE-06 | A2-3 | Pending |
| A2-SEO-TOOL-01 | A2-5 | Pending |
| A2-SEO-TOOL-02 | A2-5 | Pending |
| A2-SEO-TOOL-03 | A2-5 | Pending |
| A2-SEO-TOOL-04 | A2-6 | Pending |
| A2-SEO-TOOL-05 | A2-6 | Pending |
| A2-SEO-01 | A2-7 | Pending |
| A2-SEO-02 | A2-7 | Pending |
| A2-SEO-03 | A2-7 | Pending |
| A2-REV-01 | A2-7 | Pending |
| A2-REV-02 | A2-7 | Pending |
| A2-UI-01 | A2-8 | Pending |
| A2-UI-02 | A2-8 | Pending |
| A2-UI-03 | A2-8 | Pending |
| A2-UI-04 | A2-8 | Pending |

### Workstream B

| Requirement | Phase | Status |
|-------------|-------|--------|
| B-INFRA-01 | B-1 | Pending |
| B-INFRA-02 | B-1 | Pending |
| B-INFRA-03 | B-1 | Pending |
| B-RES-01 | B-3 | Pending |
| B-RES-02 | B-4 | Pending |
| B-RES-03 | B-3 | Pending |
| B-RES-04 | B-5 | Pending |
| B-RES-05 | B-3 | Pending |
| B-CVR-01 | B-6 | Pending |
| B-CVR-02 | B-6 | Pending |
| B-CVR-03 | B-6 | Pending |
| B-CVR-04 | B-6 | Pending |
| B-PAY-01 | B-7 | Pending |
| B-PAY-02 | B-8 | Pending |
| B-PAY-03 | B-8 | Pending |
| B-PAY-04 | B-8 | Pending |
| B-AUTH-01 | B-2 | Pending |
| B-AUTH-02 | B-2 | Pending |
| B-AUTH-03 | B-2 | Pending |
| B-SEO-01 | B-9 | Pending |
| B-SEO-02 | B-9 | Pending |

**Total mapped: 47/47 — no orphaned requirements**

---

## Key Research Decisions Incorporated

| Decision | Source | Applied In |
|----------|--------|------------|
| Cloudflare Pages over Vercel/Netlify for A1/A2 (unlimited bandwidth) | A1 + A2 research | A1-1, A2-1 |
| Vanilla JS for A1 (11ty for templating, zero framework runtime) | A1 research | A1-1 through A1-4 |
| Astro 5.x for A2 (Islands Architecture, zero-JS default) | A2 research | A2-1 |
| Preact island only for diff tool (3 KB vs React 45 KB) | A2 research | A2-4 |
| jsdiff (Myers algorithm) for text diff; Web Worker for large inputs | A2 research | A2-4 |
| CSS `min-height` reservation on all ad slots before load (CLS prevention) | A1 + A2 research | A1-6, A2-7 |
| Inline critical CSS, system font stack, deferred JS | A1 research | A1-7, A2-8 |
| YMYL disclaimers on BMI, health, and finance tools | A1 research | A1-2, A1-3 |
| JSON-LD: WebApplication + FAQPage + BreadcrumbList per tool page | A1 + A2 research | A1-5, A2-7 |
| Contextual affiliate placement (result-triggered, not banner) | A2 research | A2-7 |
| Semrush ($200 CPA), Grammarly ($20 premium), Writesonic (30% recurring) | A2 research | A2-7 |
| robots.txt generator disallow-all safety warning | A2 research | A2-6 |
| Next.js App Router + Vercel AI SDK streaming (avoids 10s timeout) | B research | B-4, B-6 |
| Auth.js v5 + Resend magic link + JWT sessions | B research | B-2 |
| @react-pdf/renderer server-side (NOT html2pdf.js — image-based, ATS-incompatible) | B research | B-5 |
| Upstash Redis sliding window rate limiting in Middleware (userId-keyed, not IP) | B research | B-7 |
| Stripe webhooks only for paid access grant (never Checkout success redirect) | B research | B-8 |
| Stripe idempotency via event ID on all webhook handlers | B research | B-8 |
| $9.99/month pricing (undercuts Resume.io ~$30, Zety ~$26) | B research | B-8, B-9 |
| CAR framework (Challenge-Action-Result) for Claude resume bullet prompts | B research | B-4 |
| Anthropic Structured Outputs (Nov 2025 beta, Zod schema) for resume generation | B research | B-4 |

---

*Roadmap created: 2026-04-02*
*Last updated: 2026-04-02 — initial creation*
