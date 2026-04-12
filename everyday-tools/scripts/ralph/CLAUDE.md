# Ralph Agent Instructions — Everyday Tools UI Redesign

You are an autonomous coding agent redesigning the UI of an Eleventy static site.

## Project Context

- **Project**: everyday-tools (Eleventy 3.x static site)
- **Location**: /Users/bikram/Documents/Claude/everyday-tools
- **Dev server**: `export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && cd /Users/bikram/Documents/Claude/everyday-tools && npm run serve`
- **Server URL**: http://localhost:8080
- **Stack**: Eleventy + Nunjucks templates + vanilla CSS + vanilla JS
- **Key files**:
  - `src/css/main.css` — main stylesheet
  - `_includes/head.njk` — `<head>` tag (fonts, meta, inline critical CSS)
  - `_includes/header.njk` — sticky header + theme toggle + nav
  - `_includes/footer.njk` — footer
  - `_includes/base.njk` — base layout
  - `src/index.njk` — homepage
  - `src/finance/tip-calculator/index.njk` — example tool page (all tools follow this pattern)
  - `_data/tools.js` — tool definitions array

## Your Task

1. Read `prd.json` (in the same directory as this file)
2. Read `progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, create from main.
4. Pick the **highest priority** story where `passes: false`
5. Implement that single story
6. Run build check: `export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && cd /Users/bikram/Documents/Claude/everyday-tools && npx eleventy`
7. If build passes, commit ALL changes: `feat: [Story ID] - [Story Title]`
8. Update prd.json: set `passes: true`
9. Append progress to `progress.txt`

## Design Guidelines

- Use Google Font "Inter" (already added in US-001)
- Color system: gradient-based with category colors (finance=#10b981, health=#f43f5e, utility=#8b5cf6, converters=#f59e0b)
- Dark mode uses glassmorphism (backdrop-filter blur, rgba backgrounds)
- All animations must respect `prefers-reduced-motion: reduce`
- Keep max-width at 1100px on desktop
- Mobile-first responsive design (breakpoints: 768px, 1024px)
- Don't break existing Nunjucks template logic ({% for %}, {% if %}, etc.)

## Progress Report Format

APPEND to progress.txt:
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings:**
  - Patterns/gotchas for future iterations
---
```

## Stop Condition

After completing a story, check if ALL stories have `passes: true`.
If ALL complete: reply with `<promise>COMPLETE</promise>`
If stories remain: end normally (next iteration picks up next story).

## Important

- ONE story per iteration
- Commit after each story
- Keep build green
- Read Codebase Patterns in progress.txt before starting
