---
phase: A1-1
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - everyday-tools/.eleventy.js
  - everyday-tools/package.json
  - everyday-tools/_includes/base.njk
  - everyday-tools/_includes/head.njk
  - everyday-tools/_includes/header.njk
  - everyday-tools/_includes/footer.njk
  - everyday-tools/_data/tools.js
  - everyday-tools/src/index.njk
  - everyday-tools/src/finance/index.njk
  - everyday-tools/src/health/index.njk
  - everyday-tools/src/unit-converters/index.njk
  - everyday-tools/src/utility/index.njk
  - everyday-tools/src/finance/tip-calculator/index.njk
  - everyday-tools/src/health/bmi-calculator/index.njk
  - everyday-tools/src/unit-converters/length-converter/index.njk
  - everyday-tools/src/utility/password-generator/index.njk
  - everyday-tools/src/css/main.css
  - everyday-tools/src/js/tool-stub.js
  - everyday-tools/.gitignore
  - .github/workflows/deploy-everyday-tools.yml
autonomous: false
requirements:
  - A1-INFRA-01
  - A1-INFRA-02
  - A1-INFRA-03

must_haves:
  truths:
    - "Pushing a commit to main triggers a Cloudflare Pages build that completes and serves the site over HTTPS"
    - "The homepage lists all four tool categories (Finance, Health, Unit Converters, Utility) with working links"
    - "Each tool slug URL returns HTTP 200 with a full HTML page (not a 404 or redirect)"
    - "No framework JavaScript runtime is shipped — view-source shows plain HTML, no React/Vue/Svelte bundle"
    - "The category architecture matches the defined structure: /finance/, /health/, /unit-converters/, /utility/"
  artifacts:
    - path: "everyday-tools/.eleventy.js"
      provides: "11ty build config — input/output dirs, passthrough copies, permalink strategy"
    - path: "everyday-tools/package.json"
      provides: "npm scripts (build, serve), 11ty as only dependency"
    - path: "everyday-tools/_includes/base.njk"
      provides: "Shared HTML shell consumed by all pages"
    - path: "everyday-tools/_data/tools.js"
      provides: "Central tool registry — source of truth for names, slugs, categories"
    - path: "everyday-tools/src/index.njk"
      provides: "Homepage listing all categories and tool links (per A1-INFRA-02)"
    - path: "everyday-tools/src/css/main.css"
      provides: "200-400 line vanilla CSS, system font stack, mobile-first responsive"
    - path: ".github/workflows/deploy-everyday-tools.yml"
      provides: "GitHub Actions workflow that triggers Cloudflare Pages deploy on push to main"
  key_links:
    - from: "everyday-tools/src/index.njk"
      to: "everyday-tools/_data/tools.js"
      via: "Nunjucks loop over tools data collection"
      pattern: "for tool in collections|tools"
    - from: "every tool page (*.njk)"
      to: "everyday-tools/_includes/base.njk"
      via: "Nunjucks layout inheritance"
      pattern: "layout: base.njk"
    - from: ".github/workflows/deploy-everyday-tools.yml"
      to: "Cloudflare Pages project"
      via: "CF_API_TOKEN + CF_ACCOUNT_ID secrets, wrangler pages deploy"
      pattern: "cloudflare/pages-action"
---

<objective>
Bootstrap the Everyday Tools (A1) site from zero to a live Cloudflare Pages deployment with the complete URL architecture in place.

Purpose: Every subsequent phase (A1-2 through A1-7) adds tools into this scaffold. Getting the skeleton right now — correct URL structure, shared layouts, zero-JS output, automated deploys — means all future tools slot in cleanly with no rework.

Output:
- A versioned `everyday-tools/` project directory in the repo root
- 11ty build producing clean static HTML for homepage, four category hubs, and one stub tool page per category
- GitHub Actions workflow that deploys to Cloudflare Pages on every push to `main`
- Vanilla CSS foundation (system font, mobile-first, ~250 lines)
- A live HTTPS URL with verified 200 responses on all defined routes
</objective>

<context>
@.planning/workstreams/everyday-tools/ROADMAP.md
@.planning/research/everyday-tools-research.md
@.planning/workstreams/milestone/REQUIREMENTS.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Init 11ty project with directory structure and build config</name>
  <files>
    everyday-tools/package.json
    everyday-tools/.eleventy.js
    everyday-tools/.gitignore
    everyday-tools/_includes/base.njk
    everyday-tools/_includes/head.njk
    everyday-tools/_includes/header.njk
    everyday-tools/_includes/footer.njk
    everyday-tools/_data/tools.js
  </files>
  <action>
Create the `everyday-tools/` directory at the repo root. This is a standalone 11ty project — it has its own package.json and is NOT a monorepo workspace; other workstreams are separate projects.

**package.json** — minimal, 11ty as the only non-dev dependency:
```json
{
  "name": "everyday-tools",
  "version": "0.1.0",
  "scripts": {
    "build": "eleventy",
    "serve": "eleventy --serve --port 8080"
  },
  "dependencies": {
    "@11ty/eleventy": "^3.0.0"
  }
}
```
Run `npm install` inside `everyday-tools/` after creating this file.

**.eleventy.js** — configure 11ty:
```js
module.exports = function(eleventyConfig) {
  // Passthrough: CSS and JS go to _site as-is
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "../_includes",
      data: "../_data"
    },
    // Use Nunjucks for all template files
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    templateFormats: ["njk", "md", "html"]
  };
};
```

**.gitignore** (inside everyday-tools/):
```
node_modules/
_site/
```

**_data/tools.js** — central tool registry. This is the single source of truth for all tool metadata. Future phases add their tools here:
```js
module.exports = [
  // Finance
  {
    slug: "tip-calculator",
    name: "Tip Calculator",
    description: "Calculate tip amounts and split the bill between friends. Enter bill total, tip %, and number of people.",
    category: "finance",
    categoryName: "Finance Tools",
    status: "stub"
  },
  {
    slug: "percentage-calculator",
    name: "Percentage Calculator",
    description: "Calculate percentages three ways: X% of Y, X is what % of Y, and percentage change.",
    category: "finance",
    categoryName: "Finance Tools",
    status: "stub"
  },
  {
    slug: "loan-calculator",
    name: "Loan / EMI Calculator",
    description: "Calculate monthly loan payments using the standard amortization formula.",
    category: "finance",
    categoryName: "Finance Tools",
    status: "stub"
  },
  // Health
  {
    slug: "bmi-calculator",
    name: "BMI Calculator",
    description: "Calculate your Body Mass Index. Enter height and weight in metric or imperial units.",
    category: "health",
    categoryName: "Health Tools",
    status: "stub"
  },
  {
    slug: "age-calculator",
    name: "Age Calculator",
    description: "Calculate your exact age in years, months, and days from your date of birth.",
    category: "health",
    categoryName: "Health Tools",
    status: "stub"
  },
  // Unit Converters
  {
    slug: "unit-converter",
    name: "Unit Converter",
    description: "Convert length, weight, temperature, and volume between metric and imperial units.",
    category: "unit-converters",
    categoryName: "Unit Converters",
    status: "stub"
  },
  // Utility
  {
    slug: "time-zone-converter",
    name: "Time Zone Converter",
    description: "Convert times between major time zones around the world.",
    category: "utility",
    categoryName: "Utility Tools",
    status: "stub"
  },
  {
    slug: "password-generator",
    name: "Password Generator",
    description: "Generate secure random passwords with configurable length, uppercase, numbers, and symbols.",
    category: "utility",
    categoryName: "Utility Tools",
    status: "stub"
  },
  {
    slug: "random-number-generator",
    name: "Random Number Generator",
    description: "Generate a random number within any min/max range.",
    category: "utility",
    categoryName: "Utility Tools",
    status: "stub"
  }
];
```

**_includes/head.njk** — reusable `<head>` block. Accept `title`, `description`, `canonical` variables from front matter. System font stack; NO Google Fonts import:
```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | Everyday Tools</title>
<meta name="description" content="{{ description }}">
{% if canonical %}<link rel="canonical" href="{{ canonical }}">{% endif %}
<link rel="stylesheet" href="/css/main.css">
```

**_includes/header.njk** — site nav. Site name links to `/`. Nav links: Finance `/finance/`, Health `/health/`, Unit Converters `/unit-converters/`, Utility `/utility/`. Keep HTML under 20 lines.

**_includes/footer.njk** — minimal: copyright line, links to Privacy Policy and About (pages to be created in A1-5/A1-7 — use placeholder href="#" for now).

**_includes/base.njk** — master layout that all pages extend:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  {% include "head.njk" %}
</head>
<body>
  {% include "header.njk" %}
  <main>
    {{ content | safe }}
  </main>
  {% include "footer.njk" %}
</body>
</html>
```

Verify the build runs cleanly before moving to Task 2:
```bash
cd everyday-tools && npm run build
```
Output should be `_site/` with no errors. Zero JS files should appear in `_site/` except intentional tool JS.
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude/everyday-tools && npm run build 2>&1 | tail -5</automated>
  </verify>
  <done>
    `npm run build` exits 0. `_site/` directory is created. No `[11ty] Problem` errors in build output.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create homepage, category hubs, and stub tool pages</name>
  <files>
    everyday-tools/src/index.njk
    everyday-tools/src/finance/index.njk
    everyday-tools/src/health/index.njk
    everyday-tools/src/unit-converters/index.njk
    everyday-tools/src/utility/index.njk
    everyday-tools/src/finance/tip-calculator/index.njk
    everyday-tools/src/finance/percentage-calculator/index.njk
    everyday-tools/src/finance/loan-calculator/index.njk
    everyday-tools/src/health/bmi-calculator/index.njk
    everyday-tools/src/health/age-calculator/index.njk
    everyday-tools/src/unit-converters/unit-converter/index.njk
    everyday-tools/src/utility/time-zone-converter/index.njk
    everyday-tools/src/utility/password-generator/index.njk
    everyday-tools/src/utility/random-number-generator/index.njk
    everyday-tools/src/css/main.css
    everyday-tools/src/js/tool-stub.js
  </files>
  <action>
Create all pages that establish the URL architecture. Use `index.njk` inside each directory so 11ty generates clean URLs (e.g., `src/finance/tip-calculator/index.njk` → `/finance/tip-calculator/`).

**Per A1-INFRA-03:** tool slugs must resolve to 200. The stub pages satisfy this — full tool implementations come in A1-2 through A1-4.

**src/index.njk** — homepage (per A1-INFRA-02):
```
---
layout: base.njk
title: "Free Online Calculator Tools"
description: "Free everyday calculator and converter tools. No signup, no ads, instant results on any device."
canonical: "https://everyday-tools.pages.dev/"
---

<section class="hero">
  <h1>Everyday Calculator Tools</h1>
  <p>Free, instant tools for everyday calculations. No signup. No clutter.</p>
</section>

<section class="categories">
  <div class="category-card">
    <h2><a href="/finance/">Finance Tools</a></h2>
    <p>Tip calculator, percentage calculator, loan/EMI calculator.</p>
    <ul>
      {%- for tool in tools -%}
        {%- if tool.category == "finance" -%}
          <li><a href="/finance/{{ tool.slug }}/">{{ tool.name }}</a></li>
        {%- endif -%}
      {%- endfor -%}
    </ul>
  </div>
  <!-- Repeat pattern for health, unit-converters, utility -->
</section>
```
Write all four category cards using the same pattern — loop over `tools` filtered by category.

**Category hub pages** (e.g., `src/finance/index.njk`):
Each hub lists all tools in that category with name, description, and a link. Front matter:
```yaml
---
layout: base.njk
title: "Finance Calculator Tools"
description: "Free finance calculators: tip calculator, percentage calculator, loan and EMI calculator."
canonical: "https://everyday-tools.pages.dev/finance/"
---
```

**Stub tool pages** — create one `index.njk` per tool. Use this template (fill in title/description/category per tool):
```
---
layout: base.njk
title: "Tip Calculator — Split Any Bill Instantly"
description: "Calculate tip amounts and split the bill between friends. Enter your bill total, tip percentage, and number of people."
canonical: "https://everyday-tools.pages.dev/finance/tip-calculator/"
---

<article class="tool-page">
  <h1>Tip Calculator</h1>
  <p class="tool-intro">Calculate the tip on any bill and split it between multiple people instantly.</p>

  <div class="tool-container" id="tool-app">
    <!-- Tool UI implemented in Phase A1-2 -->
    <p class="coming-soon">Tool coming soon. Check back shortly.</p>
  </div>

  <section class="tool-explainer">
    <h2>How to use the Tip Calculator</h2>
    <p>Enter your bill total, choose a tip percentage, and specify how many people are splitting the bill. The result updates instantly.</p>

    <h2>How tip is calculated</h2>
    <p>Tip amount = Bill total × (Tip % ÷ 100). Per-person amount = (Bill total + Tip amount) ÷ Number of people.</p>

    <h2>Related tools</h2>
    <ul>
      <li><a href="/finance/percentage-calculator/">Percentage Calculator</a></li>
      <li><a href="/finance/loan-calculator/">Loan / EMI Calculator</a></li>
    </ul>
  </section>
</article>
```

Write a proportionally appropriate stub for each of the 9 tools. The explainer content must be original per tool — do not copy-paste the same text. Each stub must have:
- A meaningful H1 (primary keyword in the title)
- 1 paragraph intro explaining what the tool does
- An empty `<div id="tool-app">` placeholder with a "coming soon" notice
- An H2 "How to use [Tool]" section with 1–2 sentences
- An H2 "How [tool] works" section with the relevant formula/logic described in plain text
- An H2 "Related tools" section with 2–3 links to other tools in the same category

**src/css/main.css** — write 200–300 lines of hand-crafted CSS. Key requirements from research:
- System font stack only: `font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;`
- Mobile-first: base styles are for 375px; use `@media (min-width: 768px)` for tablet; `@media (min-width: 1024px)` for desktop
- Color palette: neutral whites/grays for light mode; use CSS custom properties (`--color-bg`, `--color-text`, `--color-accent`) so Phase A1-7 can add dark mode by toggling these on `[data-theme="dark"]`
- `max-width: 800px` centered content container with `padding: 0 1rem`
- Category cards on homepage: CSS Grid, `grid-template-columns: 1fr` on mobile, `repeat(2, 1fr)` at 768px, `repeat(4, 1fr)` at 1024px
- Tool page: `.tool-container` gets a light background card, `border-radius: 8px`, `padding: 1.5rem`, `box-shadow: 0 1px 3px rgba(0,0,0,.1)` — the tool itself should be visually prominent
- Navigation: horizontal flex row, sticky at top, subtle border-bottom
- No Bootstrap, no Tailwind CDN — hand-written only
- Reserve ad slot containers even though no AdSense yet (Phase A1-6 will fill these): `.ad-slot { min-height: 100px; width: 100%; background: transparent; }`

**src/js/tool-stub.js** — single file, empty for now. Exists so the passthrough copy works without error. Add a comment: `// Tool JavaScript loaded here in A1-2 through A1-4`

After writing all files, run a second build and confirm all expected output paths exist:
```bash
cd everyday-tools && npm run build
ls _site/
ls _site/finance/tip-calculator/
```
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude/everyday-tools && npm run build 2>&1 | grep -E "Wrote|Problem|Error" | head -20</automated>
  </verify>
  <done>
    Build reports 14+ files written (homepage + 4 category hubs + 9 stub tool pages). `_site/finance/tip-calculator/index.html` exists. `_site/health/bmi-calculator/index.html` exists. No `[11ty] Problem` lines in build output. Running `grep -r "framework" _site/ || echo "clean"` shows no framework JS bundles in output.
  </done>
</task>

<task type="auto">
  <name>Task 3: GitHub Actions workflow for Cloudflare Pages deploy</name>
  <files>
    .github/workflows/deploy-everyday-tools.yml
  </files>
  <action>
Create the CI/CD pipeline. This workflow triggers on every push to `main` that touches the `everyday-tools/` directory, runs the 11ty build, and deploys the `_site/` output to Cloudflare Pages using the official `cloudflare/pages-action`.

**.github/workflows/deploy-everyday-tools.yml:**
```yaml
name: Deploy Everyday Tools to Cloudflare Pages

on:
  push:
    branches:
      - main
    paths:
      - 'everyday-tools/**'
  workflow_dispatch:  # Allow manual trigger

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: everyday-tools

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: everyday-tools/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Build site
        run: npm run build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          projectName: everyday-tools
          directory: everyday-tools/_site
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

**Repository secrets required (user must configure these — see checkpoint below):**
- `CF_API_TOKEN` — Cloudflare API token with "Cloudflare Pages: Edit" permission
- `CF_ACCOUNT_ID` — Found in the Cloudflare dashboard right sidebar on any zone page

**Cloudflare Pages project must be pre-created** (direct upload, not git-connected — since we're deploying via Actions, not via Cloudflare's native git integration):
1. Go to Cloudflare Dashboard → Pages → Create a project → Direct Upload
2. Name the project `everyday-tools`
3. Do a one-time manual upload of `_site/` to initialize the project (or skip and let the first workflow run do it)

Commit the workflow file to the repository:
```bash
cd /Users/bikram/Documents/Claude
git add .github/workflows/deploy-everyday-tools.yml
git commit -m "ci(A1-1): add Cloudflare Pages deploy workflow for everyday-tools"
```

The `.github/` directory may need to be created if it does not exist:
```bash
mkdir -p /Users/bikram/Documents/Claude/.github/workflows
```
  </action>
  <verify>
    <automated>cat /Users/bikram/Documents/Claude/.github/workflows/deploy-everyday-tools.yml | grep -E "cloudflare/pages-action|projectName|directory" </automated>
  </verify>
  <done>
    Workflow file exists at `.github/workflows/deploy-everyday-tools.yml`. Contains `cloudflare/pages-action@v1`, `projectName: everyday-tools`, and `directory: everyday-tools/_site`. File is committed to git.
  </done>
</task>

<task type="auto">
  <name>Task 4: Add npm lock file and commit full scaffold to git</name>
  <files>
    everyday-tools/package-lock.json
  </files>
  <action>
Ensure all files are properly committed so the GitHub Actions workflow can use `npm ci` (which requires `package-lock.json`).

Run these commands from the repo root:
```bash
cd /Users/bikram/Documents/Claude/everyday-tools
npm install   # Generates package-lock.json if not already present
cd /Users/bikram/Documents/Claude
git add everyday-tools/
git status    # Confirm: package.json, package-lock.json, .eleventy.js, _includes/, _data/, src/ are all staged
git commit -m "feat(A1-1): scaffold everyday-tools 11ty project with category URL architecture"
```

Do NOT commit `everyday-tools/node_modules/` or `everyday-tools/_site/`. Verify `.gitignore` inside `everyday-tools/` contains both.

After commit, confirm the local build is clean one final time:
```bash
cd /Users/bikram/Documents/Claude/everyday-tools
rm -rf _site
npm run build
echo "Exit: $?"
```
  </action>
  <verify>
    <automated>cd /Users/bikram/Documents/Claude && git log --oneline -3</automated>
  </verify>
  <done>
    `package-lock.json` exists in `everyday-tools/`. `git log` shows the scaffold commit. `node_modules/` and `_site/` are NOT tracked (verify with `git ls-files everyday-tools/ | grep -v node_modules | grep -v _site`).
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
    Tasks 1-4 produced:
    - A complete 11ty project at `everyday-tools/` with 11ty 3.x, Nunjucks templates, and vanilla CSS
    - Homepage listing all 4 categories and 9 tool links
    - 4 category hub pages (/finance/, /health/, /unit-converters/, /utility/)
    - 9 stub tool pages, each returning 200 with a proper HTML document, H1, intro, formula explanation, and related tools links
    - CSS using system font stack, mobile-first layout, CSS custom properties ready for dark mode
    - GitHub Actions workflow at `.github/workflows/deploy-everyday-tools.yml`
    - Everything committed to git
  </what-built>
  <how-to-verify>
    **Step 1 — Local build check:**
    ```bash
    cd /Users/bikram/Documents/Claude/everyday-tools
    npm run serve
    ```
    Open http://localhost:8080 in a browser. Verify:
    - [ ] Homepage shows 4 category sections, each with tool links
    - [ ] Clicking "Tip Calculator" goes to http://localhost:8080/finance/tip-calculator/ and shows a full page (H1, intro, formula, related tools)
    - [ ] Clicking "BMI Calculator" goes to http://localhost:8080/health/bmi-calculator/ and returns a full page
    - [ ] The nav header is present on every page with links back to category hubs
    - [ ] View-source on any page shows NO `<script src="...react...">` or framework bundle

    **Step 2 — Zero JS verification:**
    ```bash
    find /Users/bikram/Documents/Claude/everyday-tools/_site -name "*.js" | head -10
    ```
    Should only show `tool-stub.js` (the empty placeholder). No framework bundles.

    **Step 3 — URL structure spot-check:**
    ```bash
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/finance/tip-calculator/
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health/bmi-calculator/
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/unit-converters/unit-converter/
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/utility/password-generator/
    ```
    All should return `200`.

    **Step 4 — Cloudflare Pages setup (requires your Cloudflare account):**
    1. Log in to https://dash.cloudflare.com → Pages
    2. Create a project named `everyday-tools` using Direct Upload
    3. Upload the `everyday-tools/_site/` directory manually as the first deployment
    4. Note the assigned URL (e.g., `https://everyday-tools-xxxx.pages.dev`)
    5. Verify the live URL shows the homepage correctly over HTTPS

    **Step 5 — Add secrets to GitHub repo:**
    Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret:
    - `CF_API_TOKEN`: Create at https://dash.cloudflare.com/profile/api-tokens → Create Token → use "Cloudflare Pages: Edit" template
    - `CF_ACCOUNT_ID`: Found in Cloudflare dashboard right sidebar (any page)

    **Step 6 — Trigger the workflow:**
    Make a trivial change (e.g., add a space to `src/index.njk`), commit, and push to `main`.
    Watch the Actions tab in GitHub. The `Deploy Everyday Tools to Cloudflare Pages` workflow should run and pass.
    Verify the live Cloudflare Pages URL updates with the change.
  </how-to-verify>
  <resume-signal>
    Type "approved" once:
    1. http://localhost:8080/finance/tip-calculator/ returns 200 locally
    2. The Cloudflare Pages URL is live and shows the homepage over HTTPS
    3. A push to main triggered a successful workflow run

    Or describe any issues (wrong URL structure, build errors, workflow failures) and I will fix them before proceeding to A1-2.
  </resume-signal>
</task>

</tasks>

<verification>
After all tasks complete and the checkpoint is approved, verify these phase-level checks:

```bash
# 1. Build is clean
cd /Users/bikram/Documents/Claude/everyday-tools && npm run build
echo "Build exit: $?"

# 2. All 14 expected output files exist
ls _site/index.html
ls _site/finance/index.html
ls _site/health/index.html
ls _site/unit-converters/index.html
ls _site/utility/index.html
ls _site/finance/tip-calculator/index.html
ls _site/finance/percentage-calculator/index.html
ls _site/finance/loan-calculator/index.html
ls _site/health/bmi-calculator/index.html
ls _site/health/age-calculator/index.html
ls _site/unit-converters/unit-converter/index.html
ls _site/utility/time-zone-converter/index.html
ls _site/utility/password-generator/index.html
ls _site/utility/random-number-generator/index.html

# 3. No framework JavaScript shipped
find _site/ -name "*.js" | grep -v tool-stub | wc -l
# Must output: 0

# 4. CSS uses system font (not Google Fonts)
grep -i "google\|fonts.googleapis" src/css/main.css | wc -l
# Must output: 0

# 5. Tool registry covers all 8 required tools from A1 requirements
node -e "const t = require('./_data/tools.js'); console.log(t.length, 'tools'); t.forEach(x => console.log(x.slug))"
# Must show 9 tools including all A1-TOOL-01 through A1-TOOL-08 slugs
```
</verification>

<success_criteria>
Phase A1-1 is complete when ALL of the following are true:

1. **A1-INFRA-01 (static, zero-config deploy):** `npm run build` inside `everyday-tools/` produces a `_site/` directory of plain HTML/CSS files. Cloudflare Pages serves them with HTTPS. No server-side rendering, no backend, no build-time environment variables required.

2. **A1-INFRA-02 (homepage with tool list):** `https://[your-pages-url]/` renders a page listing all 4 tool categories. Each category section links to its category hub and all tools within it. Verified by viewing in a browser.

3. **A1-INFRA-03 (clean URL slugs returning 200):** Every URL in the following list returns HTTP 200 on the live Cloudflare Pages domain:
   - `/finance/tip-calculator/`
   - `/finance/percentage-calculator/`
   - `/finance/loan-calculator/`
   - `/health/bmi-calculator/`
   - `/health/age-calculator/`
   - `/unit-converters/unit-converter/`
   - `/utility/time-zone-converter/`
   - `/utility/password-generator/`
   - `/utility/random-number-generator/`

4. **Zero framework JS shipped:** `view-source` on any page shows no `<script src>` pointing to React, Vue, Angular, Svelte, or any framework bundle. The only JavaScript files present are intentional tool JS (currently just the empty `tool-stub.js`).

5. **Automated deploys working:** A push to `main` that modifies files in `everyday-tools/` triggers the GitHub Actions workflow, which completes successfully and updates the live Cloudflare Pages URL.
</success_criteria>

<output>
After all tasks complete and the checkpoint is approved, create:
`.planning/workstreams/everyday-tools/phases/A1-1/SUMMARY.md`

Include:
- Live Cloudflare Pages URL
- Confirmed URL routes returning 200
- 11ty version used
- CSS line count (must be 200-400)
- Any deviations from this plan (none expected)
- What A1-2 should know: tool stubs are in place, `_data/tools.js` is the tool registry, CSS custom properties `--color-bg` / `--color-text` / `--color-accent` are ready for dark mode in A1-7
</output>
