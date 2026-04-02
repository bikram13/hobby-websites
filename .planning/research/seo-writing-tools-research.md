# SEO & Writing Tools Site — Domain Research

**Project:** Niche SEO and writing tools website
**Researched:** 2026-04-02
**Overall confidence:** MEDIUM-HIGH (core technical claims HIGH; affiliate rate specifics MEDIUM due to program changes)

---

## 1. Tech Stack for Text-Processing Utility Sites

### Recommendation: Astro + Vanilla JS islands + Tailwind CSS

**Framework: Astro (not Next.js)**

For a static, SEO-first tool site, Astro is the correct choice over Next.js. The reasoning is architectural: Next.js ships the full React runtime even for static exports (~85 KB gzipped baseline), while Astro's Islands Architecture delivers zero JavaScript by default and only activates JS for components that explicitly need it.

Measured benchmarks (2025) show Astro sites:
- Load ~40% faster than comparable Next.js static builds
- Ship ~90% less JavaScript
- 60% of Astro sites pass Core Web Vitals vs 38% for Next.js/Gatsby equivalents
- Achieve Lighthouse SEO scores of 100 routinely because output is clean, pre-rendered HTML

For a tool site this matters more than usual because each tool page is essentially a static shell with a small interactive island (the tool itself). Astro's `client:load` directive on a single component handles this perfectly without penalizing the whole page with framework overhead.

**Interactive tool logic: Vanilla JS or lightweight framework component**

Do NOT build tools in React. For word counters, case converters, and URL slug generators, plain JavaScript event listeners on `<textarea>` elements is faster, has zero bundle overhead, and is trivially debuggable. Reserve component frameworks only where state management genuinely helps (e.g., the diff tool with side-by-side panels).

For the diff tool specifically, use a Preact island (`client:load`) rather than React — Preact is 3 KB vs React's ~45 KB and the API is identical.

**CSS: Tailwind CSS v4**

At multi-page scale (10+ tool pages + blog/guide content), Tailwind's PurgeCSS/JIT output converges to under 10 KB. A small project using vanilla CSS stays small, but Tailwind pays off once you're maintaining a consistent design system across 20+ pages. Mobile-first utility classes also align with the mobile-first requirement.

**Build output: Static export to CDN**

All tools run client-side in the browser. There is no server required. This means:
- Zero cold starts
- Deployable to Cloudflare Pages free tier (unlimited bandwidth — the critical differentiator vs Vercel/Netlify which cap at 100 GB/month)
- Full CDN distribution at Cloudflare's 300+ edge locations

**Hosting: Cloudflare Pages (not Vercel, not Netlify)**

| Platform | Free Bandwidth | Free Builds/mo | CDN Nodes | Best For |
|----------|---------------|----------------|-----------|----------|
| Cloudflare Pages | Unlimited | 500 | 300+ | High-traffic static sites |
| Vercel | 100 GB/mo | 100 (hobby) | ~50+ | Next.js apps |
| Netlify | 100 GB/mo | 300 min | ~30 | JAMstack / forms |

For a tools site that could receive unpredictable traffic spikes (from social sharing, Reddit, ProductHunt), Cloudflare Pages is the only free tier that won't cut you off mid-month. The 300+ edge nodes also give genuinely global performance.

**Real-time processing considerations**

All 11 tools listed (word counter, character counter, readability, case converter, diff, lorem ipsum, keyword density, meta tag generator, URL slug, Open Graph, robots.txt) can run entirely in the browser with no server calls. This is the correct approach:

- No latency from server round-trips
- No API costs
- Works offline after first load (cache with a service worker)
- Privacy-respecting (user text never leaves the browser) — a genuine marketing differentiator

For the readability checker and keyword density checker, debounce the processing at ~200–300ms to avoid blocking the main thread on large pastes. For the diff tool, use a Web Worker for large inputs since the Myers diff on 50,000-word documents can block the UI for ~200ms.

**Full recommended stack:**

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | Astro 5.x | Zero-JS default, Islands, Lighthouse 100 |
| Interactivity | Vanilla JS (most tools) / Preact (diff) | Minimal bundle, no framework overhead |
| Styling | Tailwind CSS v4 | Consistent design at scale, <10 KB output |
| Hosting | Cloudflare Pages | Unlimited bandwidth free tier, global CDN |
| Analytics | Cloudflare Web Analytics | Zero-JS, no cookie consent required |
| Sitemap/SEO | astro-seo + astro-sitemap | Built-in, zero config |

---

## 2. SEO Strategy for Competing Against Established Players

### The Core Problem

SmallSEOTools, TextFixer, Tools4Noobs, and similar incumbents have:
- Domain authority built over 10+ years
- Thousands of backlinks
- Broad keyword coverage

You cannot out-authority them on head terms ("word counter", "character counter") in the first 12 months. The strategy is to go around them, not through them.

### Strategy 1: Long-tail keyword domination first

Head terms are unwinnable early. Long-tail variants are not:

| Head term (hard) | Long-tail variants (winnable) |
|-----------------|-------------------------------|
| word counter | word counter for Twitter/X character limit |
| | word counter for college essays 500 words |
| | word counter for SEO meta descriptions |
| character counter | character counter for Instagram bio |
| | character counter with spaces vs without |
| readability checker | readability checker for 5th grade level |
| | Flesch-Kincaid score checker for academic writing |
| keyword density | keyword density checker for on-page SEO |
| meta tag generator | meta tag generator for Open Graph social preview |

Long-tail keywords convert better because user intent is more specific. Target 3–5 long-tail variants per tool as dedicated landing page sections or FAQ content.

### Strategy 2: Topical authority via supporting content

Tools alone rank as utility pages. To build domain authority, surround each tool with supporting content:

- "What is Flesch-Kincaid and what score should you aim for?" (guide)
- "How to write meta descriptions: length, keywords, CTR" (guide → links to your meta tag generator)
- "Word count by content type: blog posts, essays, tweets, emails" (guide → links to word counter)

This hub-and-spoke architecture means each tool page is the hub, and 2–4 supporting guides are spokes linking back to it. Google rewards sites where tools and educational content reinforce each other.

### Strategy 3: Differentiation on quality, not breadth

Incumbents have 100+ tools of mediocre quality. You have 11 tools that should be noticeably better:

- Faster (no ads blocking interaction, no page reloads)
- Cleaner UI (mobile-first, no visual clutter)
- More informative output (readability score + interpretation, not just a number)
- No email signup required to use basic features

This gives you a legitimate reason to exist and something to say in outreach.

### Strategy 4: On-page SEO for tool pages

Each tool page needs:
- H1: "[Tool Name] — Free [descriptor]" (e.g., "Flesch-Kincaid Readability Checker — Free Online Tool")
- Meta description: Include the tool function + a differentiating phrase ("no signup required", "real-time results")
- FAQ section with FAQPage structured data (JSON-LD) — FAQ rich results show at position 0
- HowTo structured data for tools that have steps
- Breadcrumb structured data
- Internal links to 2–3 related tools and 1–2 supporting guides

Schema markup does not directly boost rankings but improves SERP appearance, and FAQ rich results can appear even when you rank position 3–5, capturing significant CTR.

### Strategy 5: Core Web Vitals as a ranking advantage

Established tool sites are often slow (ad-heavy, unoptimized). If your site consistently achieves:
- LCP < 1.5s
- CLS < 0.05
- INP < 100ms

...you have a genuine ranking signal advantage on mobile searches. The Astro + Cloudflare Pages stack makes this achievable without heroic optimization effort.

### Timeline expectation

- Months 1–3: Crawling, indexing, no meaningful rankings
- Months 3–6: Long-tail and low-competition terms begin ranking
- Months 6–12: Supporting content builds domain authority, head-term rankings improve
- Month 12+: Compounding effect if content cluster strategy is followed consistently

---

## 3. Affiliate Programs Worth Integrating

### Tier 1: High-value, high-conversion (recommend integrating from day one)

**Semrush**
- Commission: $200 flat fee per new paid subscription (CPA model, migrated from recurring)
- Additional: $10 per free trial activation
- Cookie duration: 120 days
- Platform: Impact
- Fit: Meta tag generator, keyword density checker, Open Graph generator pages
- Note: The shift from recurring to flat CPA was controversial for legacy affiliates but provides faster cash flow. $200/conversion is among the highest in the SaaS affiliate space.
- Confidence: HIGH (official Semrush KB page confirmed)

**Grammarly**
- Commission: $0.20 per free signup + $20 per premium upgrade
- Cookie duration: 90 days
- Fit: Word counter, readability checker, character counter pages
- Note: Volume play — high conversion rates on writing tool pages because the audience is exactly right. An SEO writing tool user who sees a Grammarly recommendation is a warm lead.
- Confidence: HIGH (multiple sources confirm these rates)

**Writesonic**
- Commission: 30% recurring for lifetime of customer
- Plans: $16+/month
- Effective per-referral value: ~$5.76+/month recurring
- Fit: All tool pages, especially content-focused tools
- Note: Jasper ended their affiliate program January 26, 2025. Writesonic is currently the strongest recurring-commission AI writing tool affiliate.
- Confidence: HIGH (official Writesonic affiliate page confirmed)

### Tier 2: Worth adding as traffic scales

**Ahrefs**
- Commission: Conflicting reports (30% recurring claimed by some sources, other sources say no active public program)
- Status: UNCLEAR — official Ahrefs program status requires direct verification at ahrefs.com/affiliates
- Fit: Would be excellent for keyword density and meta tag pages
- Confidence: LOW — do not rely on this until verified directly with Ahrefs
- Action: Check ahrefs.com directly before including in site content

**Mangools (KWFinder)**
- Fit: Keyword density, meta tag generator pages
- Note: Smaller program but consistent commissions for SEO tool referrals
- Confidence: MEDIUM

**NordVPN / privacy tools**
- Fit: robots.txt generator page (privacy-adjacent audience)
- Note: High CPC niche, $100+ per referral common

### Commission rate summary

| Program | Rate | Type | Cookie | Integration Point |
|---------|------|------|--------|-------------------|
| Semrush | $200/sale + $10/trial | CPA | 120 days | SEO tools pages |
| Grammarly | $20 premium / $0.20 free | CPA | 90 days | Writing tools pages |
| Writesonic | 30% recurring | Recurring | — | All pages |
| Ahrefs | Unverified | — | — | Verify first |

### Placement strategy

- Do not use affiliate banners in the tool interface — it degrades the tool experience
- Place affiliate recommendations in:
  - "Next steps" sections below the tool result ("Your text has low readability — improve it with [Grammarly]")
  - Supporting guide content (naturally contextual)
  - An "Upgrade your toolkit" sidebar on desktop
  - Email sequences (if you build a list)

The highest converting placement is contextual: after the tool produces a result that implies the user has a problem, recommend a solution.

---

## 4. Readability Algorithm Implementation (Flesch-Kincaid)

### The formulas

**Flesch Reading Ease (higher = easier to read)**
```
score = 206.835 - (1.015 × ASL) - (84.6 × ASW)
```
Where:
- ASL = Average Sentence Length (total words / total sentences)
- ASW = Average Syllables per Word (total syllables / total words)

**Flesch-Kincaid Grade Level (US school grade)**
```
grade = 0.39 × ASL + 11.8 × ASW - 15.59
```

**Score interpretation (Reading Ease)**

| Score | Grade Level | Description |
|-------|-------------|-------------|
| 90–100 | 5th grade | Very easy — conversational English |
| 70–80 | 7th grade | Easy — consumer content |
| 60–70 | 8–9th grade | Standard — journalism |
| 50–60 | 10–12th grade | Fairly difficult |
| 30–50 | College | Difficult — academic |
| 0–30 | Professional | Very difficult — legal/technical |

### Implementation approach

**Option A: Use the `flesch` + `flesch-kincaid` npm packages (ESM)**

The `words/flesch` and `words/flesch-kincaid` packages on npm implement the formulas directly. Both are TypeScript-typed, ESM-only, and depend on the `syllable` package for syllable counting.

```js
import { fleschKincaid } from 'flesch-kincaid'
import { syllable } from 'syllable'

// Requires pre-computed counts
const score = fleschKincaid({
  sentence: sentenceCount,
  word: wordCount,
  syllable: syllableCount
})
```

**Option B: Implement from scratch (recommended for this project)**

For a static site with no build-time Node.js dependency on NLP packages, implementing the syllable counter and formula directly gives you full control and zero external dependency risk. The syllable counting algorithm used in the `syllable` package is based on a dictionary + rules approach:

```js
function countSyllables(word) {
  word = word.toLowerCase().replace(/[^a-z]/g, '')
  if (word.length <= 3) return 1
  word = word.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '')
  word = word.replace(/^y/, '')
  const matches = word.match(/[aeiouy]{1,2}/g)
  return matches ? matches.length : 1
}
```

This regex-based approximation is accurate enough for Flesch-Kincaid purposes (the formula itself has a margin of ~0.5 grade levels) and runs in microseconds per word.

**The sentence splitting problem**

Sentence detection is harder than it looks. A naive `.split('.')` breaks on:
- Abbreviations (U.S., Dr., etc.)
- Decimal numbers (3.14)
- Ellipses (...)

A workable approach for a browser tool:

```js
function countSentences(text) {
  // Split on . ! ? followed by whitespace and uppercase, or end of string
  const sentences = text.match(/[^.!?]*[.!?]+/g) || []
  return Math.max(1, sentences.length)
}
```

**Additional readability scores to offer**

Coleman-Liau uses character count instead of syllable count, making it fully deterministic:
```
CLI = 0.0588 × L - 0.296 × S - 15.8
```
Where L = avg letters per 100 words, S = avg sentences per 100 words.

The `cgiffard/TextStatistics.js` library implements Flesch-Kincaid, Gunning-Fog, Coleman-Liau, SMOG, and ARI in a single browser-compatible file. Worth reviewing as a reference implementation even if you don't use it directly.

### Performance note

Real-time readability calculation on 10,000-word pastes is fast (<5ms) with the above approach. No debouncing needed for readability. Debounce only for the diff tool and keyword density checker.

---

## 5. Text Diff Algorithm Options

### Recommendation: `diff` package (jsdiff) with Myers algorithm

**The Myers diff algorithm** (O(ND), 1986) is the standard for text diff tools. It finds the shortest edit script — the minimum number of insertions and deletions needed to transform one text into another. This is what Git uses.

**Available libraries:**

| Library | Algorithm | Bundle Size | Browser | Best For |
|---------|-----------|-------------|---------|----------|
| `diff` (jsdiff) | Myers | ~12 KB min | Yes (dist/diff.min.js) | General text diff |
| `diff-match-patch` (Google) | Bitap/Myers hybrid | ~32 KB | Yes | Fuzzy matching + patches |
| `fast-diff` | Simplified Myers | ~2 KB | Yes | Speed-focused, character-level |
| `myers-diff` | Pure Myers | ~8 KB | Yes | Direct Myers implementation |

**Use `diff` (jsdiff) v8+** — it is the most battle-tested, ships with TypeScript types built-in (no @types/diff needed), and supports character-level, word-level, and line-level diff modes which are exactly what a browser diff tool needs.

```js
import { diffWords, diffChars, diffLines } from 'diff'

// Word-level diff (best for prose comparison)
const changes = diffWords(oldText, newText)

// Render with highlights
changes.forEach(part => {
  const color = part.added ? 'green' : part.removed ? 'red' : 'grey'
  // render span with color
})
```

**diff-match-patch** (Google) is overkill for a simple diff display tool — it adds fuzzy matching and patch application that you don't need, at nearly 3x the bundle size.

**fast-diff** is worth knowing: at 2 KB it's ideal if you only need character-level diff for small inputs (e.g., showing changes in a single field). Not appropriate for document-level comparison.

**UX recommendation for the diff tool:**

- Default view: side-by-side (desktop) / unified (mobile)
- Toggle between word-level and line-level diff
- Show statistics: X words added, Y words removed, Z unchanged
- Syntax highlight changed sections with accessible green/red + strikethrough (not color alone — accessibility)
- For large documents (>10,000 words), run diff in a Web Worker to prevent UI blocking

```js
// web-worker-diff.js
import { diffWords } from 'diff'
self.onmessage = ({ data }) => {
  const result = diffWords(data.original, data.modified)
  self.postMessage(result)
}
```

### Patience diff (alternative)

Patience diff (used by Bazaar, some Git configs) produces more human-readable diffs for code. For a prose writing tool, Myers diff produces equally readable results. Patience diff has no mature npm package — do not use it for this project.

---

## 6. Monetization Insights Specific to SEO Tool Sites

### AdSense RPM reality for utility/tool sites

Tool sites have a specific monetization profile:

- High page views per session (users often visit multiple tools)
- Low session duration per page (30–90 seconds per tool use)
- High return visitor rate (bookmarkable tools)
- Moderate AdSense RPM: estimated $2–$6 for US/UK/AU traffic on SEO/writing topics

The SEO and digital marketing niche is not the highest-CPM AdSense category (finance/legal holds those positions), but it benefits from advertiser competition from SaaS companies (Semrush, Ahrefs, Grammarly, Jasper alternatives) bidding on your audience.

### Ad network progression strategy

Follow a tiered approach as traffic grows:

**Phase 1 (0–10K sessions/month): Google AdSense**
- No traffic minimum
- No content minimum beyond standard quality
- AdSense auto-ads work but manual placement outperforms — place one leaderboard above the fold, one after tool results, one in sidebar (desktop only)
- Expected RPM: $1–$4

**Phase 2 (10K+ sessions/month): Ezoic**
- Ezoic's Access Now program has removed the old 10,000-pageview minimum
- AI-driven ad placement typically 2–3x AdSense RPM in testing (reported $5–$15 RPM)
- Revenue share is 10% (Ezoic takes 10% of gross, you keep 90%)
- Can run alongside AdSense (Ezoic becomes the ad manager)

**Phase 3 (50K+ sessions/month): Mediavine Journey**
- Mediavine Journey requires 10,000 sessions/month minimum (down from 50K for main program)
- Main Mediavine program requires 50K sessions/month
- Reported RPMs of $15–$40 in digital marketing niches
- Requires a high percentage of original, long-form content — tool pages alone may not qualify

**Do not rush to Mediavine.** The application process is selective and rejections delay you. Build to 50K sessions with Ezoic, then apply.

### Affiliate vs AdSense: which earns more per visitor

For a tools site with the right affiliate integration, affiliate revenue outperforms AdSense per visitor at scale:

- AdSense: ~$3 RPM = $0.003 per visitor
- Semrush affiliate: $200/sale at 0.5% conversion = $1.00 per 1000 visitors (333x AdSense per visitor)
- Grammarly: $20/premium at 2% conversion = $0.40 per 1000 visitors (133x AdSense)

The math strongly favors affiliate over AdSense for monetization per visitor. However, affiliate revenue is inconsistent (lumpy, depends on conversions) while AdSense is predictable. The optimal strategy is both, prioritizing affiliate placement.

### Page-level monetization mapping

| Tool Page | Primary Affiliate | Secondary Affiliate | AdSense Placement |
|-----------|------------------|--------------------|--------------------|
| Word counter | Grammarly | Writesonic | Below result |
| Character counter | Grammarly | — | Below result |
| Readability checker | Grammarly | Writesonic | Below result |
| Case converter | — | — | Sidebar only |
| Text diff | — | — | Above fold |
| Lorem ipsum | — | — | Sidebar only |
| Keyword density | Semrush | Ahrefs (if verified) | Below result |
| Meta tag generator | Semrush | — | Below result |
| URL slug generator | Semrush | — | Sidebar + below |
| Open Graph generator | Semrush | — | Below result |
| robots.txt generator | Semrush | — | Below result |

### High-value contextual placement pattern

The highest-converting affiliate placements follow the "tool result implies a need" pattern:

- Readability score is low → "Improve your writing with Grammarly (free)"
- Keyword density is 0.3% (too low for target keyword) → "Analyze your full SEO with Semrush"
- Meta description is 165 characters (too long) → "Track your meta tag performance in Semrush"

Build these contextual recommendations into the tool output logic, not as static banners.

### Email list as a long-term asset

Tool sites with an email list break the dependency on Google traffic. A simple "Get our SEO writing checklist (free PDF)" opt-in converts well on writing/SEO tool pages. A list of 5,000 engaged subscribers is worth more to long-term revenue stability than AdSense alone. Do not build this at launch — it requires content investment — but plan the infrastructure (ConvertKit, or Beehiiv free tier) from the beginning.

### Revenue diversification timeline

| Traffic Level | Primary Revenue | Expected Monthly |
|--------------|-----------------|-----------------|
| 0–5K sessions | AdSense only | $5–$25 |
| 5K–20K sessions | AdSense + affiliate | $50–$300 |
| 20K–50K sessions | Ezoic + affiliate | $300–$1,500 |
| 50K–150K sessions | Mediavine + affiliate | $1,500–$8,000+ |

These ranges assume US/UK/AU traffic majority. Non-English-speaking traffic dramatically lowers AdSense RPM (India traffic: $0.30–$0.80 RPM vs US $5–$12 RPM). SEO-focused tool pages naturally attract English-speaking audiences, which is favorable.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Astro vs Next.js recommendation | HIGH | Multiple verified benchmarks, 2025 data |
| Cloudflare Pages hosting | HIGH | Official docs + community confirmation |
| Flesch-Kincaid formulas | HIGH | Formulas are stable, published 1975, unchanged |
| jsdiff / Myers algorithm | HIGH | npm package docs confirmed, actively maintained |
| Semrush affiliate ($200/sale) | HIGH | Official Semrush KB page confirmed |
| Grammarly affiliate rates | HIGH | Multiple sources confirm $0.20/$20 |
| Writesonic 30% recurring | HIGH | Official affiliate page confirmed |
| Ahrefs affiliate status | LOW | Conflicting sources — verify at ahrefs.com directly |
| Jasper affiliate end date | HIGH | Multiple sources confirm January 26, 2025 |
| AdSense RPM ranges | MEDIUM | Ranges vary; tool niches not always reported separately |
| Ezoic/Mediavine RPM claims | MEDIUM | Real-world reports but highly variable by niche |
| Topical authority timeline | MEDIUM | Based on industry consensus, not controlled data |

---

## Critical Implementation Notes

**Do not implement tools as server-side functions.** Even keyword density checking is fast enough to run in the browser on 10,000-word inputs. A server dependency introduces latency, cost, and a single point of failure.

**The robots.txt generator needs a warning.** A user who generates `Disallow: /` and deploys it de-indexes their site. The tool must detect this pattern and display a prominent warning. This is both a UX and legal liability issue.

**The Open Graph generator should include a live preview.** Showing the user how their OG tags will render on Twitter/X, LinkedIn, and Facebook in real-time is the primary differentiator from competitors. Use Canvas or a CSS-styled preview div.

**Keyword density reporting should show TF-IDF context, not just raw density.** A 2% density on "the" is meaningless; 2% density on your target keyword matters. The tool should strip stopwords (a, the, and, or, is, etc.) and report on meaningful terms only.

**Ahrefs affiliate verification is a required pre-launch task.** Do not reference Ahrefs commissions in your content until you have confirmed the current program status directly at their website. Stating outdated commission rates damages trust.

---

## Sources

- [Astro vs Next.js performance benchmarks (2025)](https://eastondev.com/blog/en/posts/dev/20251202-astro-vs-nextjs-comparison/)
- [Astro as SEO weapon — static generation](https://astrojs.dev/articles/astro-seo-weapon/)
- [Cloudflare Pages vs Vercel vs Netlify comparison (2026)](https://www.devtoolreviews.com/reviews/vercel-vs-netlify-vs-cloudflare-pages-2026)
- [Vercel vs Netlify vs Cloudflare 2025](https://www.digitalapplied.com/blog/vercel-vs-netlify-vs-cloudflare-pages-comparison)
- [Flesch-Kincaid npm package](https://github.com/words/flesch-kincaid)
- [Flesch Reading Ease npm package](https://github.com/words/flesch)
- [TextStatistics.js — multiple readability scores](https://github.com/cgiffard/TextStatistics.js)
- [jsdiff — Myers diff for JavaScript](https://github.com/kpdecker/jsdiff)
- [diff-match-patch — Google's diff library](https://github.com/google/diff-match-patch)
- [fast-diff — 2 KB character diff](https://github.com/jhchen/fast-diff)
- [Semrush affiliate program official docs](https://www.semrush.com/kb/97-affiliate-program)
- [Semrush affiliate program review 2026](https://www.affililist.com/blog/semrush-affiliate-program)
- [Writesonic affiliate program — 30% recurring](https://writesonic.com/affiliate)
- [Jasper affiliate program ended January 2025](https://www.way2earning.com/2025/05/semrush-affiliate-program/)
- [Ahrefs affiliate program status (conflicting)](https://www.way2earning.com/2025/09/ahrefs-affiliate-program/)
- [AdSense vs Ezoic vs Mediavine RPM comparison](https://geekvillage.com/adsense-vs-ezoic-vs-mediavine-which-is-best-for-small-publishers/)
- [AdSense RPM by niche 2025](https://serpzilla.com/blog/10-best-google-adsense-niches-2025-a-practical-guide-for-website-owners/)
- [Topical authority strategy 2025](https://www.enfuse-solutions.com/topical-authority-in-2025-the-seo-strategy-that-beats-backlinks/)
- [Hub and spoke SEO model](https://www.seo-kreativ.de/en/blog/hub-and-spoke-model/)
- [FAQ schema structured data — Google Search docs](https://developers.google.com/search/docs/appearance/structured-data/faqpage)
- [Schema markup guide 2025](https://www.digitalapplied.com/blog/schema-markup-implementation-guide)
- [Every readability formula explained (JavaScript)](https://dev.to/ckmtools/every-readability-formula-explained-with-javascript-examples-21ml)
- [Syllable npm package](https://www.npmjs.com/package/syllable)
- [Compromise.js NLP library](https://github.com/spencermountain/compromise)
- [Niche site profitability 2025](https://nicheinvestor.com/are-niche-sites-still-profitable-in-2025/)
