export type ToolCategory = 'Writing' | 'SEO'

export interface Tool {
  slug: string
  category: ToolCategory
  title: string
  description: string
  path: string
  phase: string
  status?: 'live' | 'coming-soon'
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
    status: 'live',
  },
  {
    slug: 'character-counter',
    category: 'Writing',
    title: 'Character Counter',
    description: 'Count characters with and without spaces — great for Twitter, meta descriptions, and more.',
    path: '/writing/character-counter',
    phase: 'A2-2',
    status: 'live',
  },
  {
    slug: 'readability-checker',
    category: 'Writing',
    title: 'Readability Checker',
    description: 'Get your Flesch-Kincaid reading ease score and grade level instantly.',
    path: '/writing/readability-checker',
    phase: 'A2-2',
    status: 'live',
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
    status: 'live',
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
    status: 'live',
  },
  {
    slug: 'meta-tag-generator',
    category: 'SEO',
    title: 'Meta Tag Generator',
    description: 'Generate optimized title and meta description tags with a live SERP preview.',
    path: '/seo/meta-tag-generator',
    phase: 'A2-5',
    status: 'live',
  },
  {
    slug: 'url-slug-generator',
    category: 'SEO',
    title: 'URL Slug Generator',
    description: 'Convert any text into a clean, SEO-friendly lowercase-hyphenated URL slug.',
    path: '/seo/url-slug-generator',
    phase: 'A2-5',
    status: 'live',
  },
  {
    slug: 'open-graph-generator',
    category: 'SEO',
    title: 'Open Graph Generator',
    description: 'Build og: meta tags for social sharing with a live Twitter/Facebook preview.',
    path: '/seo/open-graph-generator',
    phase: 'A2-6',
    status: 'live',
  },
  {
    slug: 'robots-txt-generator',
    category: 'SEO',
    title: 'Robots.txt Generator',
    description: 'Configure your robots.txt rules via UI — includes a safety warning for Disallow: /.',
    path: '/seo/robots-txt-generator',
    phase: 'A2-6',
    status: 'live',
  },
]

// Helper: get tools by category
export function toolsByCategory(category: ToolCategory): Tool[] {
  return tools.filter(t => t.category === category)
}
