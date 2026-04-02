# Hobby Websites Portfolio

## What This Is

A portfolio of revenue-generating hobby websites built and maintained by a solo developer. The portfolio consists of three parallel projects: an everyday utility tools site, an SEO/writing tools site, and an AI-powered resume and cover letter builder — each designed to attract organic traffic and generate passive income.

## Core Value

Each website must deliver immediate, no-signup utility to visitors so they return and share — traffic is the foundation of all revenue.

## Requirements

### Validated

(None yet — ship to validate)

### Active

**Project A1 — Everyday Tools Site**
- [ ] Collection of utility tools: unit converters, calculators, tip calculator, age calculator, BMI calculator, etc.
- [ ] Fast, clean UI with no login required
- [ ] Google AdSense integration for ad revenue
- [ ] SEO-optimized pages per tool (meta tags, structured data)
- [ ] Mobile responsive design

**Project A2 — SEO / Writing Tools Site**
- [ ] Writing tools: word counter, readability checker, character counter, sentence counter
- [ ] SEO tools: keyword density checker, meta tag generator, slug generator
- [ ] Fast, no-signup access
- [ ] AdSense + affiliate revenue integration
- [ ] SEO-optimized landing pages per tool

**Project B — AI Resume & Cover Letter Builder**
- [ ] AI-powered resume builder (structured sections, export to PDF)
- [ ] AI-powered cover letter generator (job description input → tailored letter)
- [ ] Freemium model: free tier (limited uses) + paid tier ($5-15/month)
- [ ] Integration with Claude API (claude-sonnet-4-6)
- [ ] Clean, professional UI

### Out of Scope

- User accounts / auth for A1 and A2 — unnecessary friction for utility tools, adds complexity without revenue benefit
- Mobile apps — web-first; apps require separate store submissions and maintenance overhead
- Social features — not relevant to utility/tool sites at this stage
- Database for A1/A2 — all tools run client-side; no backend needed for pure utility tools

## Context

- Hobby project by a solo developer; no team, no deadlines
- Revenue targets: passive AdSense income for A1/A2, subscription MRR for Project B
- All three projects run as parallel GSD workstreams
- Hosting: static sites (Vercel/Netlify) for A1/A2; serverless or lightweight Node backend for B
- Stack preference: modern web (HTML/CSS/JS or lightweight framework), minimal dependencies
- SEO is critical for A1/A2 — organic Google traffic is the primary acquisition channel

## Constraints

- **Budget**: Hobby project — minimize recurring costs; prefer free tiers of services
- **Maintenance**: Solo developer — keep each project simple and self-contained
- **AI Costs**: Project B uses Claude API — freemium model must cover API costs
- **Hosting**: Prefer Vercel/Netlify free tiers for A1/A2; serverless for B to keep costs near zero at low traffic

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Three separate sites vs. one | Better SEO targeting per niche; simpler codebases; independent revenue streams | — Pending |
| GSD workstreams for parallelism | User wants to develop all three simultaneously without context switching overhead | — Pending |
| Client-side only for A1/A2 | No hosting costs, fast load times, better SEO scores, no backend to maintain | — Pending |
| Claude API for Project B | Best AI quality for resume/cover letter generation; user already uses Claude ecosystem | — Pending |

---
*Last updated: 2026-04-02 — initial project setup*
