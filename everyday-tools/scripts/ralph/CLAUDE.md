# Project Guidelines: Everyday Tools
- **Framework:** Eleventy (11ty) static site generator
- **Templating:** Nunjucks (`.njk`) using base layout (`_includes/base.njk`, `_includes/head.njk`, `_includes/header.njk`, `_includes/footer.njk`)
- **Styling:** Tailwind CSS (via CDN) utilizing `class="dark"` by default.
- **Development Server:** `npm run serve` (runs on `http://localhost:8080`)
- **Build Output:** `npm run build` formats to `_site/` directory

## UX & Design Principles
- Emulate the "Glassmorphism" aesthetic with semi-transparent cards using `backdrop-blur`.
- Ensure all inputs and buttons map functional interactions in vanilla JS since this is a static site without client-side frameworks. Ensure variables bind reliably locally.
- Keep the `_includes/head.njk` Tailwind configuration intact. 
- The project targets minimal cognitive load. Keep UI elements uncluttered.

## Automation Instructions
You are an autonomous agent driven by the Ralph wrapper script. Always follow this exact sequence:
1. Read `scripts/ralph/prd.json` to find the highest-priority story that has `"passes": false`.
2. Work on implementing the requested changes according to its `acceptanceCriteria`. Check your work building the node script if necessary.
3. Once completed and verified, update `scripts/ralph/prd.json` to set `"passes": true` for that specific task.
4. Update `scripts/ralph/progress.txt` with what you accomplished.
5. If ALL tasks in `prd.json` are completed (`passes: true`), you must output EXACTLY `<promise>COMPLETE</promise>` in your final message to break the automation loop.
