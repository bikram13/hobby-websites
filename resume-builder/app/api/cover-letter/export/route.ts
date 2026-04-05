import { renderToBuffer, Document, Page, Text, StyleSheet } from "@react-pdf/renderer"
import { auth } from "@/auth"
import { createElement } from "react"

const styles = StyleSheet.create({
  page: { fontFamily: "Helvetica", fontSize: 11, padding: 56, color: "#1a1a1a", lineHeight: 1.6 },
  heading: { fontSize: 13, fontFamily: "Helvetica-Bold", marginBottom: 24 },
  body: { fontSize: 11, color: "#333333" },
})

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.id) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401 })
  }

  const { text = "", jobTitle = "", company = "" } = await req.json().catch(() => ({}))
  if (!text.trim()) return new Response(JSON.stringify({ error: "text required" }), { status: 400 })

  const heading = [jobTitle, company].filter(Boolean).join(" — ")
  const doc = createElement(
    Document,
    { title: `Cover Letter${heading ? ` — ${heading}` : ""}` },
    createElement(
      Page,
      { size: "LETTER" as const, style: styles.page },
      ...(heading ? [createElement(Text, { style: styles.heading }, heading)] : []),
      createElement(Text, { style: styles.body }, text)
    )
  )

  const buffer = await renderToBuffer(doc)
  const filename = `cover-letter${company ? `-${company.replace(/[^a-z0-9]/gi, "-").toLowerCase()}` : ""}.pdf`

  return new Response(new Uint8Array(buffer), {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
    },
  })
}
