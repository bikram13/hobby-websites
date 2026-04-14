# Ralph Agent Instructions — SEO Writing Tools

You are an autonomous coding agent improving the UI/UX layout of an Astro-based site.

## Project Context

- **Project**: seo-writing-tools (Astro)
- **Location**: /Users/bikram/Documents/Claude/seo-writing-tools
- **Dev server command**: `export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && cd /Users/bikram/Documents/Claude/seo-writing-tools && npm run dev`
- **Build command for verification**: `export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && cd /Users/bikram/Documents/Claude/seo-writing-tools && npm run build`
- **Tech Stack**: Astro, Tailwind CSS, Preact hooks.

## Your Task

1. Read `prd.json` (in the same directory as this file)
2. Read `progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, create from main.
4. Pick the **highest priority** story where `passes: false`
5. Implement that single story
6. Run build check: `export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && cd /Users/bikram/Documents/Claude/seo-writing-tools && npm run build`
7. If build passes, commit ALL changes: `feat: [Story ID] - [Story Title]`
8. Update prd.json: set `passes: true`
9. Append progress to `progress.txt`

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
