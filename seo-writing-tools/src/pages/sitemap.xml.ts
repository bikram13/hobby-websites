import type { APIRoute } from 'astro'
import { tools } from '../data/tools'

const BASE = 'https://seo-writing-tools.pages.dev'

export const GET: APIRoute = () => {
  const urls = [
    `<url><loc>${BASE}/</loc><priority>1.0</priority><changefreq>weekly</changefreq></url>`,
    ...tools
      .filter(t => t.status === 'live')
      .map(t => `<url><loc>${BASE}${t.path}/</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>`),
  ]

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>`,
    { headers: { 'Content-Type': 'application/xml' } }
  )
}
