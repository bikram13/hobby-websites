const BASE = 'https://seo-writing-tools.pages.dev'

export function toolJsonLd(slug: string, title: string, description: string, path: string): string {
  return JSON.stringify([
    {
      '@context': 'https://schema.org',
      '@type': 'WebApplication',
      name: title,
      url: `${BASE}${path}/`,
      description,
      applicationCategory: 'UtilityApplication',
      operatingSystem: 'Any',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    },
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: `${BASE}/` },
        { '@type': 'ListItem', position: 2, name: title, item: `${BASE}${path}/` },
      ],
    },
  ])
}

// Contextual affiliate recommendations per tool category
export type AffiliateLink = { name: string; url: string; desc: string }

export const affiliates: Record<string, AffiliateLink[]> = {
  Writing: [
    { name: 'Grammarly', url: 'https://grammarly.com', desc: 'AI-powered grammar and style checker' },
    { name: 'Writesonic', url: 'https://writesonic.com', desc: 'AI writing assistant for long-form content' },
  ],
  SEO: [
    { name: 'Semrush', url: 'https://semrush.com', desc: 'All-in-one SEO toolkit — keyword research, audits, rank tracking' },
    { name: 'Ahrefs', url: 'https://ahrefs.com', desc: 'Backlink analysis and keyword explorer' },
  ],
}
