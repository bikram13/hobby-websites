# Requirements: Hobby Websites Portfolio

**Defined:** 2026-04-02
**Core Value:** Each website must deliver immediate, no-signup utility so visitors return and share — traffic is the foundation of all revenue.

---

## Project A1 — Everyday Tools Site

### v1 Requirements

#### Structure & Infrastructure
- [ ] **A1-INFRA-01**: Project is a static site deployable to Vercel/Netlify with zero configuration
- [ ] **A1-INFRA-02**: Site has a homepage listing all available tools with descriptions and links
- [ ] **A1-INFRA-03**: Each tool lives on its own URL slug (e.g., `/tip-calculator`, `/bmi-calculator`)
- [ ] **A1-INFRA-04**: Site loads in under 2 seconds on mobile (Lighthouse performance ≥ 85)

#### Tools
- [ ] **A1-TOOL-01**: Tip calculator (bill amount, tip %, split count → per-person amount)
- [ ] **A1-TOOL-02**: Unit converter (length, weight, temperature, volume)
- [ ] **A1-TOOL-03**: Age calculator (DOB → exact age in years/months/days)
- [ ] **A1-TOOL-04**: BMI calculator (height + weight → BMI + category)
- [ ] **A1-TOOL-05**: Percentage calculator (X% of Y, X is what % of Y, % change)
- [ ] **A1-TOOL-06**: Loan/EMI calculator (principal, rate, tenure → monthly payment)
- [ ] **A1-TOOL-07**: Time zone converter (convert time between major time zones)
- [ ] **A1-TOOL-08**: Random number / password generator

#### SEO & Revenue
- [ ] **A1-SEO-01**: Each tool page has unique meta title, description, and Open Graph tags
- [ ] **A1-SEO-02**: Structured data (JSON-LD) on each tool page for rich snippets
- [ ] **A1-SEO-03**: XML sitemap generated at `/sitemap.xml`
- [ ] **A1-SEO-04**: robots.txt configured correctly
- [ ] **A1-REV-01**: Google AdSense ad slots integrated on tool pages (non-intrusive placement)

#### UI/UX
- [ ] **A1-UI-01**: Mobile-first responsive design
- [ ] **A1-UI-02**: Clean, minimal UI — tool is the focus, no distractions
- [ ] **A1-UI-03**: No login, no signup, no cookies popup required (no tracking beyond AdSense)
- [ ] **A1-UI-04**: Dark/light mode toggle

### v2 Requirements (Deferred)
- More tools: currency converter, calorie calculator, date difference calculator
- Tool favorites / recent history (localStorage)
- Share result via URL (query params)

---

## Project A2 — SEO / Writing Tools Site

### v1 Requirements

#### Structure & Infrastructure
- [ ] **A2-INFRA-01**: Static site deployable to Vercel/Netlify
- [ ] **A2-INFRA-02**: Homepage with tool directory and category filters
- [ ] **A2-INFRA-03**: Each tool on its own URL slug
- [ ] **A2-INFRA-04**: Lighthouse performance ≥ 85 on mobile

#### Writing Tools
- [ ] **A2-WRITE-01**: Word counter (word, character, sentence, paragraph counts; reading time)
- [ ] **A2-WRITE-02**: Character counter with/without spaces
- [ ] **A2-WRITE-03**: Readability checker (Flesch-Kincaid score + grade level)
- [ ] **A2-WRITE-04**: Case converter (UPPER, lower, Title Case, camelCase, snake_case)
- [ ] **A2-WRITE-05**: Text diff tool (compare two texts, highlight differences)
- [ ] **A2-WRITE-06**: Lorem ipsum generator (configurable paragraphs/words/sentences)

#### SEO Tools
- [ ] **A2-SEO-TOOL-01**: Keyword density checker (paste text → top keywords + frequency %)
- [ ] **A2-SEO-TOOL-02**: Meta tag generator (title, description, keywords → preview + copy)
- [ ] **A2-SEO-TOOL-03**: URL slug generator (text → SEO-friendly slug)
- [ ] **A2-SEO-TOOL-04**: Open Graph tag generator (fill form → copy og: meta tags)
- [ ] **A2-SEO-TOOL-05**: Robots.txt generator (configure via UI → download file)

#### SEO & Revenue
- [ ] **A2-SEO-01**: Unique meta tags per tool page
- [ ] **A2-SEO-02**: Structured data (JSON-LD) on each page
- [ ] **A2-SEO-03**: XML sitemap at `/sitemap.xml`
- [ ] **A2-REV-01**: Google AdSense integrated on tool pages
- [ ] **A2-REV-02**: Affiliate links to relevant SEO tools (Ahrefs, SEMrush, Grammarly)

#### UI/UX
- [ ] **A2-UI-01**: Mobile-first responsive design
- [ ] **A2-UI-02**: Text areas with real-time processing (no submit button needed for counters)
- [ ] **A2-UI-03**: Copy-to-clipboard on all outputs
- [ ] **A2-UI-04**: Dark/light mode toggle

### v2 Requirements (Deferred)
- AI-assisted rewrite/summarize (upgrade path to monetization)
- Plagiarism checker integration
- Grammar checker integration

---

## Project B — AI Resume & Cover Letter Builder

### v1 Requirements

#### Infrastructure
- [ ] **B-INFRA-01**: Next.js app deployable to Vercel
- [ ] **B-INFRA-02**: Serverless API routes for Claude API calls (API key server-side only)
- [ ] **B-INFRA-03**: Environment variable management for API keys

#### Resume Builder
- [ ] **B-RES-01**: User fills structured form: contact info, summary, experience, education, skills
- [ ] **B-RES-02**: AI generates/improves each section on demand (Claude claude-sonnet-4-6)
- [ ] **B-RES-03**: Live resume preview updates as user types
- [ ] **B-RES-04**: Export resume to PDF (server-side via @react-pdf/renderer — NOT html2pdf.js)
- [ ] **B-RES-05**: Multiple resume templates (at least 2: classic and modern)

#### Cover Letter Builder
- [ ] **B-CVR-01**: User inputs job title, company name, job description, and their background
- [ ] **B-CVR-02**: AI generates tailored cover letter (Claude claude-sonnet-4-6)
- [ ] **B-CVR-03**: User can regenerate or edit inline
- [ ] **B-CVR-04**: Export cover letter to PDF or copy as plain text

#### Freemium Model
- [ ] **B-PAY-01**: Free tier: 3 AI generations per day (Upstash Redis sliding window, userId-keyed)
- [ ] **B-PAY-02**: Paid tier: unlimited generations (₹799/month via Razorpay — ~$9.99 equivalent)
- [ ] **B-PAY-03**: Razorpay Subscription integration for recurring payments (supports UPI, cards, net banking, wallets)
- [ ] **B-PAY-04**: Razorpay webhook to activate/deactivate paid access (webhooks only — never success redirect)

#### Auth (minimal)
- [ ] **B-AUTH-01**: Email magic link login via Auth.js v5 + Resend (no password — reduces friction)
- [ ] **B-AUTH-02**: Session persists across browser refresh (JWT strategy, 24-hour expiry)
- [ ] **B-AUTH-03**: User data (saved resumes) stored per account in Neon PostgreSQL via Prisma

#### SEO & Marketing
- [ ] **B-SEO-01**: Landing page with clear value proposition and CTA
- [ ] **B-SEO-02**: Meta tags, OG tags on all public pages
- [ ] **B-SEO-03**: Blog/resource section for SEO content (v2)

### v2 Requirements (Deferred)
- LinkedIn profile import
- Job board integration (auto-apply)
- Resume ATS score checker
- Team/agency plans

### Out of Scope (All Projects)

| Feature | Reason |
|---------|--------|
| Mobile apps (iOS/Android) | Web-first; apps add maintenance overhead without proportional revenue at hobby scale |
| User accounts for A1/A2 | Pure utility tools — auth adds friction with no value |
| A1/A2 backend/database | All tools run client-side; no data to store |
| Social/community features | Out of scope for v1; focus on utility and SEO |
| Multi-language i18n | Complexity not justified at hobby scale for v1 |

## Traceability

### Workstream A1

| Requirement | Phase | Status |
|-------------|-------|--------|
| A1-INFRA-01 | A1-1: Scaffold & Deploy | Pending |
| A1-INFRA-02 | A1-1: Scaffold & Deploy | Pending |
| A1-INFRA-03 | A1-1: Scaffold & Deploy | Pending |
| A1-INFRA-04 | A1-7: UI Polish & Performance | Pending |
| A1-TOOL-01 | A1-2: Finance Tools | Pending |
| A1-TOOL-02 | A1-3: Health & Conversion Tools | Pending |
| A1-TOOL-03 | A1-3: Health & Conversion Tools | Pending |
| A1-TOOL-04 | A1-3: Health & Conversion Tools | Pending |
| A1-TOOL-05 | A1-2: Finance Tools | Pending |
| A1-TOOL-06 | A1-2: Finance Tools | Pending |
| A1-TOOL-07 | A1-4: Utility Tools | Pending |
| A1-TOOL-08 | A1-4: Utility Tools | Pending |
| A1-SEO-01 | A1-5: SEO Foundation | Pending |
| A1-SEO-02 | A1-5: SEO Foundation | Pending |
| A1-SEO-03 | A1-5: SEO Foundation | Pending |
| A1-SEO-04 | A1-5: SEO Foundation | Pending |
| A1-REV-01 | A1-6: AdSense Integration | Pending |
| A1-UI-01 | A1-7: UI Polish & Performance | Pending |
| A1-UI-02 | A1-7: UI Polish & Performance | Pending |
| A1-UI-03 | A1-7: UI Polish & Performance | Pending |
| A1-UI-04 | A1-7: UI Polish & Performance | Pending |

### Workstream A2

| Requirement | Phase | Status |
|-------------|-------|--------|
| A2-INFRA-01 | A2-1: Scaffold & Deploy | Pending |
| A2-INFRA-02 | A2-1: Scaffold & Deploy | Pending |
| A2-INFRA-03 | A2-1: Scaffold & Deploy | Pending |
| A2-INFRA-04 | A2-8: UI Polish & Performance | Pending |
| A2-WRITE-01 | A2-2: Writing Tools Batch 1 | Pending |
| A2-WRITE-02 | A2-2: Writing Tools Batch 1 | Pending |
| A2-WRITE-03 | A2-2: Writing Tools Batch 1 | Pending |
| A2-WRITE-04 | A2-3: Writing Tools Batch 2 | Pending |
| A2-WRITE-05 | A2-4: Text Diff Tool | Pending |
| A2-WRITE-06 | A2-3: Writing Tools Batch 2 | Pending |
| A2-SEO-TOOL-01 | A2-5: SEO Tools Batch 1 | Pending |
| A2-SEO-TOOL-02 | A2-5: SEO Tools Batch 1 | Pending |
| A2-SEO-TOOL-03 | A2-5: SEO Tools Batch 1 | Pending |
| A2-SEO-TOOL-04 | A2-6: SEO Tools Batch 2 | Pending |
| A2-SEO-TOOL-05 | A2-6: SEO Tools Batch 2 | Pending |
| A2-SEO-01 | A2-7: SEO & Revenue Layer | Pending |
| A2-SEO-02 | A2-7: SEO & Revenue Layer | Pending |
| A2-SEO-03 | A2-7: SEO & Revenue Layer | Pending |
| A2-REV-01 | A2-7: SEO & Revenue Layer | Pending |
| A2-REV-02 | A2-7: SEO & Revenue Layer | Pending |
| A2-UI-01 | A2-8: UI Polish & Performance | Pending |
| A2-UI-02 | A2-8: UI Polish & Performance | Pending |
| A2-UI-03 | A2-8: UI Polish & Performance | Pending |
| A2-UI-04 | A2-8: UI Polish & Performance | Pending |

### Workstream B

| Requirement | Phase | Status |
|-------------|-------|--------|
| B-INFRA-01 | B-1: Scaffold & Infrastructure | Pending |
| B-INFRA-02 | B-1: Scaffold & Infrastructure | Pending |
| B-INFRA-03 | B-1: Scaffold & Infrastructure | Pending |
| B-RES-01 | B-3: Resume Builder UI | Pending |
| B-RES-02 | B-4: AI Resume Generation | Pending |
| B-RES-03 | B-3: Resume Builder UI | Pending |
| B-RES-04 | B-5: PDF Export | Pending |
| B-RES-05 | B-3: Resume Builder UI | Pending |
| B-CVR-01 | B-6: Cover Letter Builder | Pending |
| B-CVR-02 | B-6: Cover Letter Builder | Pending |
| B-CVR-03 | B-6: Cover Letter Builder | Pending |
| B-CVR-04 | B-6: Cover Letter Builder | Pending |
| B-PAY-01 | B-7: Freemium & Rate Limiting | Pending |
| B-PAY-02 | B-8: Stripe Payments | Pending |
| B-PAY-03 | B-8: Stripe Payments | Pending |
| B-PAY-04 | B-8: Stripe Payments | Pending |
| B-AUTH-01 | B-2: Authentication | Pending |
| B-AUTH-02 | B-2: Authentication | Pending |
| B-AUTH-03 | B-2: Authentication | Pending |
| B-SEO-01 | B-9: Landing Page & SEO | Pending |
| B-SEO-02 | B-9: Landing Page & SEO | Pending |

**Coverage:**
- v1 requirements: 47 total
- Mapped to phases: 47
- Unmapped: 0

---
*Requirements defined: 2026-04-02*
*Last updated: 2026-04-02 — traceability updated with fine-grained phase assignments*
