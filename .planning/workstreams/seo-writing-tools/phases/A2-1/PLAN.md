---
phase: A2-1
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - astro.config.mjs
  - package.json
  - tailwind.config.mjs
  - src/layouts/BaseLayout.astro
  - src/components/CategoryFilter.astro
  - src/components/ToolCard.astro
  - src/data/tools.ts
  - src/pages/index.astro
  - src/pages/writing/word-counter.astro
  - src/pages/seo/url-slug-generator.astro
  - src/styles/global.css
  - public/robots.txt
  - .gitignore
autonomous: true
requirements:
  - A2-INFRA-01
  - A2-INFRA-02
  - A2-INFRA-03

must_haves:
  truths:
    - "Pushing to main triggers a Cloudflare Pages build and deploys to a live HTTPS URL automatically"
    - "The homepage shows all 11 tools organized into Writing and SEO categories with working filter buttons"
    - "Clicking a category filter hides tools from other categories without a page reload"
    - "Each tool URL (e.g., /writing/word-counter, /seo/url-slug-generator) returns pre-rendered static HTML — view-source shows no framework bootstrap JS"
    - "Running astro build completes without errors and the dist/ folder contains only .html files and CSS for non-interactive pages"
    - "Tailwind CSS is compiled at build time via JIT — no CDN link appears in the HTML output"
  artifacts:
    - path: "astro.config.mjs"
      provides: "Astro project config with static output mode and Tailwind integration"
    - path: "src/data/tools.ts"
      provides: "Single source of truth for all 11 tool definitions — slug, title, description, category"
    - path: "src/layouts/BaseLayout.astro"
      provides: "Shared HTML shell: <head>, nav, footer, slot"
    - path: "src/components/ToolCard.astro"
      provides: "Reusable card component for tool directory listing"
    - path: "src/components/CategoryFilter.astro"
      provides: "Filter UI with vanilla JS — no Astro component JS bundle"
    - path: "src/pages/index.astro"
      provides: "Homepage — imports tools.ts, renders all ToolCards, mounts CategoryFilter"
    - path: "src/pages/writing/word-counter.astro"
      provides: "Placeholder tool page at /writing/word-counter"
    - path: "src/pages/seo/url-slug-generator.astro"
      provides: "Placeholder tool page at /seo/url-slug-generator"
  key_links:
    - from: "src/data/tools.ts"
      to: "src/pages/index.astro"
      via: "import tools from '../data/tools'"
      pattern: "import.*tools"
    - from: "src/components/CategoryFilter.astro"
      to: "src/components/ToolCard.astro"
      via: "data-category attribute on each card, JS filters by matching value"
      pattern: "data-category"
    - from: "astro.config.mjs"
      to: "dist/"
      via: "output: 'static' + adapter: cloudflare"
      pattern: "output.*static"
---

<objective>
Bootstrap the A2 SEO/Writing Tools site from zero: initialize the Astro 5.x project, integrate Tailwind CSS v4, build a filterable tool directory homepage, create placeholder pages for all 11 tools at their permanent URL slugs, and wire up Cloudflare Pages for automatic git deploys.

Purpose: Every subsequent phase (A2-2 through A2-8) depends on this scaffold. The URL structure, layout system, tool data model, and deploy pipeline must all be correct and locked before any tool logic is built.

Output: A live Cloudflare Pages site with a functioning homepage and 11 placeholder tool pages, all pre-rendered as static HTML with zero framework runtime JS.
</objective>

<execution_context>
Working directory for all commands: the project root (e.g., ~/sites/seo-writing-tools or wherever you init the project).
All `npm` commands assume Node 20+.
All file paths below are relative to the project root.
</execution_context>

<context>
@/Users/bikram/Documents/Claude/.planning/workstreams/seo-writing-tools/ROADMAP.md
@/Users/bikram/Documents/Claude/.planning/research/seo-writing-tools-research.md
@/Users/bikram/Documents/Claude/.planning/workstreams/milestone/REQUIREMENTS.md

Key decisions locked from research:
- Astro 5.x (NOT Next.js) — Islands Architecture, zero-JS default output
- Tailwind CSS v4 — JIT, installed via npm, NOT the CDN script tag
- Cloudflare Pages — unlimited bandwidth free tier; use @astrojs/cloudflare adapter
- Vanilla JS for interactive islands (NOT React, NOT Vue)
- Preact reserved ONLY for the diff tool in Phase A2-4
- URL structure: /writing/{slug} and /seo/{slug} (two category subdirectories)
- 11 tools total: 6 Writing, 5 SEO (defined in Task 2 below)
- No user accounts, no server-side functions, no database — fully static
</context>

<tasks>

<task type="auto">
  <name>Task 1: Initialize Astro 5.x project with Tailwind CSS v4 and Cloudflare adapter</name>
  <files>
    package.json,
    astro.config.mjs,
    tailwind.config.mjs,
    src/styles/global.css,
    .gitignore,
    tsconfig.json
  </files>
  <action>
    Run the Astro scaffold, then configure all integrations. Execute in sequence:

    ```bash
    # 1. Create project (select "Empty" template, TypeScript: strict, no git init yet)
    npm create astro@latest . -- --template empty --typescript strict --no-install --no-git

    # 2. Install dependencies
    npm install

    # 3. Add Tailwind CSS v4 (the official Astro integration installs @tailwindcss/vite)
    npx astro add tailwind

    # 4. Add Cloudflare Pages adapter
    npx astro add cloudflare
    ```

    After scaffolding, edit astro.config.mjs to set static output mode explicitly:

    ```js
    // astro.config.mjs
    import { defineConfig } from 'astro/config'
    import tailwind from '@astrojs/tailwind'
    import cloudflare from '@astrojs/cloudflare'

    export default defineConfig({
      output: 'static',          // Pre-render everything — no server runtime
      adapter: cloudflare(),
      integrations: [tailwind()],
      site: 'https://your-project.pages.dev',  // update after CF Pages URL is known
    })
    ```

    Create src/styles/global.css with Tailwind v4 directives (v4 uses @import not @tailwind):

    ```css
    /* src/styles/global.css */
    @import "tailwindcss";

    /* Base resets */
    *, *::before, *::after { box-sizing: border-box; }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      margin: 0;
      background: #f9fafb;
      color: #111827;
    }
    ```

    Note: Do NOT use @tailwind base / @tailwind components / @tailwind utilities — those are Tailwind v3 syntax. Tailwind v4 uses @import "tailwindcss".

    Add to .gitignore: node_modules/, dist/, .wrangler/, .env, .env.local

    Verify the dev server starts and the default page renders without console errors:
    ```bash
    npm run dev
    ```
  </action>
  <verify>
    ```bash
    # Build must succeed with zero errors
    npm run build

    # Confirm output mode is static — no _worker.js in dist/
    ls dist/ | grep -v _worker

    # Confirm Tailwind output is compiled (not a CDN link)
    grep -r "cdn.tailwindcss\|unpkg.com/tailwindcss" dist/ && echo "FAIL: CDN found" || echo "PASS: no CDN"

    # Confirm no framework runtime bundle
    ls dist/_astro/*.js 2>/dev/null | wc -l  # should be 0 for purely static pages
    ```
  </verify>
  <done>
    - `npm run build` exits 0 with no errors or warnings
    - dist/ contains index.html (or placeholder) and a compiled CSS file
    - No CDN tailwind script tag in any HTML file in dist/
    - No _astro/*.js runtime bundle in dist/ (zero framework JS)
    - dev server starts at localhost:4321 and renders without errors
  </done>
</task>

<task type="auto">
  <name>Task 2: Define tool data model and create all 11 tool placeholder pages</name>
  <files>
    src/data/tools.ts,
    src/pages/writing/word-counter.astro,
    src/pages/writing/character-counter.astro,
    src/pages/writing/readability-checker.astro,
    src/pages/writing/case-converter.astro,
    src/pages/writing/text-diff.astro,
    src/pages/writing/lorem-ipsum-generator.astro,
    src/pages/seo/keyword-density-checker.astro,
    src/pages/seo/meta-tag-generator.astro,
    src/pages/seo/url-slug-generator.astro,
    src/pages/seo/open-graph-generator.astro,
    src/pages/seo/robots-txt-generator.astro
  </files>
  <action>
    Create the tool data model first — it is the single source of truth used by the homepage, nav, and sitemap.

    ```ts
    // src/data/tools.ts
    export type ToolCategory = 'Writing' | 'SEO'

    export interface Tool {
      slug: string          // URL path segment, e.g. 'word-counter'
      category: ToolCategory
      title: string         // Display name
      description: string   // One sentence, shown on homepage card
      path: string          // Full URL path, e.g. '/writing/word-counter'
      phase: string         // Which phase implements this tool
    }

    export const tools: Tool[] = [
      // Writing tools (Phase A2-2 and A2-3)
      {
        slug: 'word-counter',
        category: 'Writing',
        title: 'Word Counter',
        description: 'Count words, characters, sentences, paragraphs, and reading time in real time.',
        path: '/writing/word-counter',
        phase: 'A2-2',
      },
      {
        slug: 'character-counter',
        category: 'Writing',
        title: 'Character Counter',
        description: 'Count characters with and without spaces — great for Twitter, meta descriptions, and more.',
        path: '/writing/character-counter',
        phase: 'A2-2',
      },
      {
        slug: 'readability-checker',
        category: 'Writing',
        title: 'Readability Checker',
        description: 'Get your Flesch-Kincaid reading ease score and grade level instantly.',
        path: '/writing/readability-checker',
        phase: 'A2-2',
      },
      {
        slug: 'case-converter',
        category: 'Writing',
        title: 'Case Converter',
        description: 'Convert text to UPPER CASE, lower case, Title Case, camelCase, or snake_case.',
        path: '/writing/case-converter',
        phase: 'A2-3',
      },
      {
        slug: 'text-diff',
        category: 'Writing',
        title: 'Text Diff Tool',
        description: 'Compare two texts side-by-side and highlight every addition and deletion.',
        path: '/writing/text-diff',
        phase: 'A2-4',
      },
      {
        slug: 'lorem-ipsum-generator',
        category: 'Writing',
        title: 'Lorem Ipsum Generator',
        description: 'Generate placeholder text by paragraphs, sentences, or word count.',
        path: '/writing/lorem-ipsum-generator',
        phase: 'A2-3',
      },
      // SEO tools (Phase A2-5 and A2-6)
      {
        slug: 'keyword-density-checker',
        category: 'SEO',
        title: 'Keyword Density Checker',
        description: 'Analyze keyword frequency in your content — stopwords filtered, top terms ranked.',
        path: '/seo/keyword-density-checker',
        phase: 'A2-5',
      },
      {
        slug: 'meta-tag-generator',
        category: 'SEO',
        title: 'Meta Tag Generator',
        description: 'Generate optimized title and meta description tags with a live SERP preview.',
        path: '/seo/meta-tag-generator',
        phase: 'A2-5',
      },
      {
        slug: 'url-slug-generator',
        category: 'SEO',
        title: 'URL Slug Generator',
        description: 'Convert any text into a clean, SEO-friendly lowercase-hyphenated URL slug.',
        path: '/seo/url-slug-generator',
        phase: 'A2-5',
      },
      {
        slug: 'open-graph-generator',
        category: 'SEO',
        title: 'Open Graph Generator',
        description: 'Build og: meta tags for social sharing with a live Twitter/Facebook preview.',
        path: '/seo/open-graph-generator',
        phase: 'A2-6',
      },
      {
        slug: 'robots-txt-generator',
        category: 'SEO',
        title: 'Robots.txt Generator',
        description: 'Configure your robots.txt rules via UI — includes a safety warning for Disallow: /.',
        path: '/seo/robots-txt-generator',
        phase: 'A2-6',
      },
    ]

    // Helper: get tools by category
    export function toolsByCategory(category: ToolCategory): Tool[] {
      return tools.filter(t => t.category === category)
    }
    ```

    Create ONE placeholder page, then replicate the pattern for all 11. Each placeholder must:
    - Import and use BaseLayout (created in Task 3 — write a minimal inline shell for now)
    - Show the tool title and a "Coming soon" note with the phase that will build it
    - Have the correct URL when built (Astro file path = URL path)
    - Contain NO framework JS — purely static HTML

    Example placeholder (replicate for all 11, adjusting title/description/phase):

    ```astro
    ---
    // src/pages/writing/word-counter.astro
    import { tools } from '../../data/tools'

    const tool = tools.find(t => t.slug === 'word-counter')!
    const title = `${tool.title} — Free Online Tool`
    const description = tool.description
    ---
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{title}</title>
        <meta name="description" content={description} />
      </head>
      <body>
        <main style="max-width:720px;margin:4rem auto;padding:0 1rem;font-family:system-ui,sans-serif">
          <nav><a href="/">← All Tools</a></nav>
          <h1>{tool.title}</h1>
          <p>{tool.description}</p>
          <p><em>Tool implementation coming in phase {tool.phase}.</em></p>
        </main>
      </body>
    </html>
    ```

    Use BaseLayout once it exists (Task 3). For now the inline shell is fine — Task 3 will refactor these to use BaseLayout, or you can write Task 3 first if you prefer strict interface-first ordering.

    Create all 11 pages following this exact file → URL mapping:
    - src/pages/writing/word-counter.astro → /writing/word-counter
    - src/pages/writing/character-counter.astro → /writing/character-counter
    - src/pages/writing/readability-checker.astro → /writing/readability-checker
    - src/pages/writing/case-converter.astro → /writing/case-converter
    - src/pages/writing/text-diff.astro → /writing/text-diff
    - src/pages/writing/lorem-ipsum-generator.astro → /writing/lorem-ipsum-generator
    - src/pages/seo/keyword-density-checker.astro → /seo/keyword-density-checker
    - src/pages/seo/meta-tag-generator.astro → /seo/meta-tag-generator
    - src/pages/seo/url-slug-generator.astro → /seo/url-slug-generator
    - src/pages/seo/open-graph-generator.astro → /seo/open-graph-generator
    - src/pages/seo/robots-txt-generator.astro → /seo/robots-txt-generator
  </action>
  <verify>
    ```bash
    npm run build

    # Verify all 11 tool pages exist in dist/
    echo "=== Writing tools ===" && ls dist/writing/
    echo "=== SEO tools ===" && ls dist/seo/

    # Verify each page is static HTML (no script tags with src pointing to _astro/)
    for f in dist/writing/*.html dist/seo/*.html; do
      echo -n "$f: "
      grep -c '<script src="/_astro/' "$f" && echo "FAIL: has runtime JS" || echo "PASS"
    done

    # Spot-check one URL resolves correctly in dev
    # npm run dev, then: curl -s http://localhost:4321/writing/word-counter | grep -o '<h1>.*</h1>'
    ```
  </verify>
  <done>
    - dist/writing/ contains 6 .html files matching the 6 writing tool slugs
    - dist/seo/ contains 5 .html files matching the 5 SEO tool slugs
    - Each file contains the tool title in an `<h1>` tag
    - No `<script src="/_astro/...">` tag in any tool page HTML
    - src/data/tools.ts exports the `tools` array with all 11 entries, typed correctly
  </done>
</task>

<task type="auto">
  <name>Task 3: Build BaseLayout, ToolCard component, and wire homepage with category filter</name>
  <files>
    src/layouts/BaseLayout.astro,
    src/components/ToolCard.astro,
    src/components/CategoryFilter.astro,
    src/pages/index.astro,
    src/styles/global.css
  </files>
  <action>
    Build the layout and homepage. The filter island uses vanilla JS inline in a `<script>` tag
    inside CategoryFilter.astro — NOT `client:load` (that would ship an Astro JS bundle).
    Inline `<script>` tags in Astro compile to a plain `<script>` in the HTML output, which is
    framework-free.

    ```astro
    ---
    // src/layouts/BaseLayout.astro
    import '../styles/global.css'

    interface Props {
      title: string
      description: string
    }

    const { title, description } = Astro.props
    const canonicalURL = new URL(Astro.url.pathname, Astro.site)
    ---
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{title}</title>
        <meta name="description" content={description} />
        <link rel="canonical" href={canonicalURL} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:url" content={canonicalURL} />
        <meta property="og:type" content="website" />
      </head>
      <body>
        <header class="bg-white border-b border-gray-200 px-4 py-3">
          <nav class="max-w-5xl mx-auto flex items-center gap-6">
            <a href="/" class="font-semibold text-gray-900 text-lg">SEO &amp; Writing Tools</a>
            <a href="/#writing" class="text-sm text-gray-600 hover:text-gray-900">Writing</a>
            <a href="/#seo" class="text-sm text-gray-600 hover:text-gray-900">SEO</a>
          </nav>
        </header>
        <main class="max-w-5xl mx-auto px-4 py-10">
          <slot />
        </main>
        <footer class="border-t border-gray-200 mt-16 px-4 py-6 text-center text-sm text-gray-500">
          Free tools. No signup. No tracking. &copy; {new Date().getFullYear()}
        </footer>
      </body>
    </html>
    ```

    ```astro
    ---
    // src/components/ToolCard.astro
    import type { Tool } from '../data/tools'

    interface Props {
      tool: Tool
    }

    const { tool } = Astro.props
    ---
    <a
      href={tool.path}
      data-category={tool.category}
      class="tool-card block rounded-lg border border-gray-200 bg-white p-5 hover:border-blue-400 hover:shadow-sm transition-all"
    >
      <span class="inline-block mb-2 text-xs font-medium uppercase tracking-wide text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
        {tool.category}
      </span>
      <h2 class="text-base font-semibold text-gray-900 mb-1">{tool.title}</h2>
      <p class="text-sm text-gray-600 leading-relaxed">{tool.description}</p>
    </a>
    ```

    ```astro
    ---
    // src/components/CategoryFilter.astro
    // Props: active category for initial state (default = 'All')
    interface Props {
      categories: string[]
    }
    const { categories } = Astro.props
    ---
    <div class="flex gap-2 mb-8 flex-wrap" id="category-filter">
      <button
        class="filter-btn active px-4 py-2 rounded-full text-sm font-medium bg-gray-900 text-white"
        data-filter="All"
      >All</button>
      {categories.map(cat => (
        <button
          class="filter-btn px-4 py-2 rounded-full text-sm font-medium bg-white border border-gray-300 text-gray-700 hover:border-gray-500"
          data-filter={cat}
        >{cat}</button>
      ))}
    </div>

    <script>
      // Vanilla JS — no framework. Runs after DOMContentLoaded.
      const buttons = document.querySelectorAll<HTMLButtonElement>('.filter-btn')
      const cards = document.querySelectorAll<HTMLElement>('.tool-card')

      buttons.forEach(btn => {
        btn.addEventListener('click', () => {
          const filter = btn.dataset.filter ?? 'All'

          // Update active button styles
          buttons.forEach(b => {
            b.classList.remove('active', 'bg-gray-900', 'text-white')
            b.classList.add('bg-white', 'border', 'border-gray-300', 'text-gray-700')
          })
          btn.classList.add('active', 'bg-gray-900', 'text-white')
          btn.classList.remove('bg-white', 'border-gray-300', 'text-gray-700')

          // Show/hide cards
          cards.forEach(card => {
            const match = filter === 'All' || card.dataset.category === filter
            card.style.display = match ? 'block' : 'none'
          })
        })
      })
    </script>
    ```

    ```astro
    ---
    // src/pages/index.astro
    import BaseLayout from '../layouts/BaseLayout.astro'
    import ToolCard from '../components/ToolCard.astro'
    import CategoryFilter from '../components/CategoryFilter.astro'
    import { tools } from '../data/tools'

    const title = 'Free SEO & Writing Tools — No Signup Required'
    const description = 'Fast, free browser-based tools for writers and SEOs. Word counter, readability checker, keyword density analyzer, meta tag generator, and more — real-time results, no data sent to any server.'
    ---
    <BaseLayout title={title} description={description}>
      <section class="mb-10">
        <h1 class="text-3xl font-bold text-gray-900 mb-3">Free SEO &amp; Writing Tools</h1>
        <p class="text-gray-600 text-lg max-w-2xl">
          Fast, free tools that run entirely in your browser.
          No signup. No data sent to any server. Real-time results.
        </p>
      </section>

      <CategoryFilter categories={['Writing', 'SEO']} />

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {tools.map(tool => <ToolCard tool={tool} />)}
      </div>
    </BaseLayout>
    ```

    After writing these files, update all 11 tool placeholder pages (from Task 2) to use BaseLayout:
    - Replace the inline `<!doctype html>` shell with `import BaseLayout from '../../layouts/BaseLayout.astro'`
    - Wrap content in `<BaseLayout title={title} description={description}>`

    This ensures all pages share the same nav and footer from the start.
  </action>
  <verify>
    ```bash
    npm run build

    # Homepage must exist
    test -f dist/index.html && echo "PASS: index.html exists" || echo "FAIL"

    # Homepage must contain all 11 tool links
    LINK_COUNT=$(grep -c 'href="/writing/\|href="/seo/' dist/index.html)
    echo "Tool links in homepage: $LINK_COUNT (expect 11)"
    [ "$LINK_COUNT" -eq 11 ] && echo "PASS" || echo "FAIL"

    # Filter buttons must be present
    grep -q 'data-filter="Writing"' dist/index.html && echo "PASS: Writing filter button" || echo "FAIL"
    grep -q 'data-filter="SEO"' dist/index.html && echo "PASS: SEO filter button" || echo "FAIL"

    # Category data attributes must be present on tool cards
    grep -c 'data-category="Writing"' dist/index.html  # expect 6
    grep -c 'data-category="SEO"' dist/index.html      # expect 5

    # Tailwind class must appear in built CSS (confirms JIT ran)
    find dist/ -name '*.css' -exec grep -l 'grid-cols' {} \;

    # No Astro island runtime — filter uses inline script only
    grep -c '_astro/CategoryFilter' dist/index.html || echo "PASS: no island bundle"
    ```
  </verify>
  <done>
    - dist/index.html exists and contains 11 `<a href>` links to tool pages
    - Each ToolCard has `data-category="Writing"` or `data-category="SEO"` in its HTML
    - Filter buttons have `data-filter="All"`, `data-filter="Writing"`, `data-filter="SEO"`
    - Inline `<script>` for filter logic is present in the HTML (not a separate bundle file)
    - No `<script src="/_astro/CategoryFilter...">` tag (vanilla JS, not an Astro island)
    - Compiled CSS file contains Tailwind utility classes (grid-cols, rounded-lg, etc.)
    - All 11 tool pages use BaseLayout and share the same nav header
  </done>
</task>

<task type="auto">
  <name>Task 4: Configure Cloudflare Pages and verify automatic git deploy pipeline</name>
  <files>
    .github/workflows/ (none needed — Cloudflare Pages has native git integration)
    wrangler.toml (optional, only if local preview needed)
    public/_headers (Cloudflare security headers)
    public/robots.txt
  </files>
  <action>
    Set up Cloudflare Pages to deploy automatically on every push to main. This task involves
    one manual dashboard step (connecting the repo) — all other steps are CLI or config.

    STEP 1 — Connect repo in Cloudflare Pages dashboard (one-time manual action):
    1. Go to dash.cloudflare.com → Workers & Pages → Create → Pages → Connect to Git
    2. Select your GitHub repo
    3. Set build configuration:
       - Framework preset: Astro
       - Build command: `npm run build`
       - Build output directory: `dist`
       - Node.js version: 20.x (set in Environment Variables: NODE_VERSION = 20)
    4. Click "Save and Deploy" — first deploy will run

    STEP 2 — Add Cloudflare security headers file:

    ```
    # public/_headers
    /*
      X-Frame-Options: DENY
      X-Content-Type-Options: nosniff
      Referrer-Policy: strict-origin-when-cross-origin
      Permissions-Policy: camera=(), microphone=(), geolocation=()
    ```

    These headers are served by Cloudflare's edge on every response. No server config needed.

    STEP 3 — Add robots.txt:

    ```
    # public/robots.txt
    User-agent: *
    Allow: /

    Sitemap: https://your-project.pages.dev/sitemap.xml
    ```

    Update the Sitemap URL once the actual Cloudflare Pages domain is known. The sitemap
    will be generated in Phase A2-7; the reference here is forward-looking.

    STEP 4 — Update astro.config.mjs with the actual Cloudflare Pages domain once it's assigned:

    ```js
    site: 'https://your-actual-project.pages.dev',
    ```

    STEP 5 — Verify the pipeline by pushing a trivial change:

    ```bash
    git add .
    git commit -m "feat(A2-1): scaffold Astro 5.x site with Tailwind v4 and tool directory"
    git push origin main
    ```

    Watch the Cloudflare Pages dashboard — build should start within 30 seconds, complete
    within 2–3 minutes, and the deployed URL should serve the homepage with HTTPS.

    STEP 6 — Smoke-test the live URL:

    ```bash
    # Replace with your actual Pages URL
    SITE_URL="https://your-project.pages.dev"

    curl -s -o /dev/null -w "%{http_code}" "$SITE_URL/"              # expect 200
    curl -s -o /dev/null -w "%{http_code}" "$SITE_URL/writing/word-counter"  # expect 200
    curl -s -o /dev/null -w "%{http_code}" "$SITE_URL/seo/url-slug-generator" # expect 200

    # Confirm HTTPS redirect (HTTP should redirect to HTTPS)
    curl -s -o /dev/null -w "%{http_code}" "http://your-project.pages.dev/" # expect 301 or 308
    ```
  </action>
  <verify>
    ```bash
    # After pushing to main and waiting for build to complete:
    SITE_URL="https://your-project.pages.dev"

    # All tool pages return 200
    for path in / /writing/word-counter /writing/character-counter /writing/readability-checker \
                /writing/case-converter /writing/text-diff /writing/lorem-ipsum-generator \
                /seo/keyword-density-checker /seo/meta-tag-generator /seo/url-slug-generator \
                /seo/open-graph-generator /seo/robots-txt-generator; do
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${SITE_URL}${path}")
      echo "$path → $STATUS"
    done

    # Confirm HTTPS (Cloudflare provides this automatically)
    curl -I "$SITE_URL/" 2>&1 | grep -i "strict-transport\|X-Frame"

    # Confirm no server-side runtime (purely static)
    curl -s "$SITE_URL/writing/word-counter" | grep -c '<script src="/_astro/' || echo "0 runtime scripts — PASS"
    ```
  </verify>
  <done>
    - Cloudflare Pages project is connected to the GitHub repo
    - Pushing to main triggers an automatic build (visible in CF Pages dashboard)
    - All 13 URLs (homepage + 12 tool pages, including the base writing/ and seo/ directories if needed) return HTTP 200
    - The site URL uses HTTPS
    - HTTP requests redirect to HTTPS (Cloudflare default behavior)
    - Security headers (X-Frame-Options, X-Content-Type-Options) are present in curl -I output
    - robots.txt is accessible at /robots.txt and returns 200
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 5: Visual and functional verification of live site</name>
  <what-built>
    A complete Astro 5.x static site live on Cloudflare Pages with:
    - A homepage showing all 11 tools as cards in a responsive grid
    - Category filter buttons (All / Writing / SEO) that show/hide cards without page reload
    - 11 placeholder tool pages at their permanent URL slugs under /writing/ and /seo/
    - Zero framework JS on any page (pure static HTML + Tailwind CSS)
    - Automatic deploy on git push to main
    - HTTPS enforced via Cloudflare
  </what-built>
  <how-to-verify>
    1. Open the live Cloudflare Pages URL in a browser (Chrome or Firefox)

    2. Homepage check:
       - You see a page titled "Free SEO & Writing Tools"
       - 11 tool cards are visible in a grid layout
       - Each card shows a category badge (Writing or SEO), a title, and a description

    3. Category filter check:
       - Click "Writing" button — only 6 writing tool cards remain visible, SEO cards disappear
       - Click "SEO" button — only 5 SEO tool cards remain visible, Writing cards disappear
       - Click "All" button — all 11 cards reappear
       - Filter must work WITHOUT a page reload (no URL change, no flash)

    4. Tool page check:
       - Click "Word Counter" card — you arrive at /writing/word-counter
       - Page shows the tool title and a "Coming soon" note
       - "← All Tools" link returns you to the homepage
       - Repeat for one SEO tool: click "URL Slug Generator" → /seo/url-slug-generator

    5. View source check (critical for zero-JS verification):
       - On any tool page, right-click → View Page Source
       - Confirm there is NO `<script src="/_astro/...">` tag in the source
       - Confirm there is NO `<script src="https://cdn.tailwindcss.com">` tag

    6. Mobile check (DevTools or real device):
       - Open DevTools → Toggle device toolbar → set to 375px width
       - Homepage grid should collapse to single column
       - All cards should be readable and tappable without horizontal scroll

    7. Deploy pipeline check:
       - Make any small change (e.g., change the homepage subtitle text)
       - Push to main: `git push origin main`
       - Go to Cloudflare Pages dashboard → verify a new build starts automatically
       - After ~2 minutes, verify the change is visible on the live URL
  </how-to-verify>
  <resume-signal>
    Type "approved" if all 7 checks pass.
    If any check fails, describe which step failed and what you observed — the executor will fix and re-verify.
  </resume-signal>
</task>

</tasks>

<verification>
Run the full build verification suite before marking the phase complete:

```bash
# 1. Clean build succeeds
npm run build && echo "BUILD PASS" || echo "BUILD FAIL"

# 2. All 11 tool pages present
TOOL_COUNT=$(ls dist/writing/*.html dist/seo/*.html 2>/dev/null | wc -l)
echo "Tool pages in dist: $TOOL_COUNT (expect 11)"

# 3. Zero framework runtime JS (astro islands) on tool pages
ISLAND_JS=$(grep -rl '_astro/' dist/writing/ dist/seo/ 2>/dev/null | wc -l)
echo "Pages with island JS: $ISLAND_JS (expect 0)"

# 4. No CDN Tailwind
CDN=$(grep -rl 'cdn.tailwindcss\|unpkg.com/tailwindcss' dist/ 2>/dev/null | wc -l)
echo "Pages with CDN Tailwind: $CDN (expect 0)"

# 5. Homepage has filter buttons
grep -q 'data-filter="Writing"' dist/index.html && echo "Filter: PASS" || echo "Filter: FAIL"

# 6. All tools linked from homepage
LINKS=$(grep -c 'href="/writing/\|href="/seo/' dist/index.html)
echo "Tool links on homepage: $LINKS (expect 11)"
```
</verification>

<success_criteria>
Phase A2-1 is complete when ALL of the following are true:

1. **Live deploy (A2-INFRA-01):** Pushing to main automatically deploys to a Cloudflare Pages URL with HTTPS. The deploy pipeline can be verified in the CF Pages dashboard.

2. **Filterable homepage (A2-INFRA-02):** The homepage at the live URL renders all 11 tool cards. The Writing and SEO filter buttons hide/show cards client-side without a page reload. The "All" filter restores all cards.

3. **Clean URL slugs (A2-INFRA-03):** All 11 tool paths return HTTP 200:
   - /writing/word-counter, /writing/character-counter, /writing/readability-checker
   - /writing/case-converter, /writing/text-diff, /writing/lorem-ipsum-generator
   - /seo/keyword-density-checker, /seo/meta-tag-generator, /seo/url-slug-generator
   - /seo/open-graph-generator, /seo/robots-txt-generator

4. **Zero framework JS:** `view-source` on any tool page shows no `<script src="/_astro/...">` tag. The category filter uses a plain inline `<script>` tag with vanilla JS — not an Astro island bundle.

5. **Tailwind JIT (not CDN):** No `cdn.tailwindcss.com` script tag anywhere. Tailwind classes are present in a compiled CSS file in dist/.

6. **Human verification approved:** The checkpoint task (Task 5) has been marked "approved" by the user after visual and functional testing on the live URL.
</success_criteria>

<output>
After all tasks complete and the checkpoint is approved, create the phase summary:

File: /Users/bikram/Documents/Claude/.planning/workstreams/seo-writing-tools/phases/A2-1/SUMMARY.md

Contents must include:
- Live Cloudflare Pages URL
- Git repo URL
- List of all 11 tool slugs and their live URLs
- Astro version and Tailwind version confirmed (from package.json)
- Notes on any deviations from this plan
- Confirmation that `astro build` produces zero framework JS
- Date completed
</output>
