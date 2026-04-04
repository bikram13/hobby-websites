import { renderToBuffer } from "@react-pdf/renderer"
import { auth } from "@/auth"
import { db } from "@/lib/prisma"
import { ResumePDF } from "@/components/resume/ResumePDF"
import type { ResumeContent } from "@/components/resume/types"
import { createElement } from "react"

export async function GET(req: Request) {
  const session = await auth()
  if (!session?.user?.id) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401 })
  }

  const { searchParams } = new URL(req.url)
  const id = searchParams.get("id")
  if (!id) return new Response(JSON.stringify({ error: "Missing id" }), { status: 400 })

  const resume = await db.resume.findUnique({
    where: { id, userId: session.user.id },
  })
  if (!resume) return new Response(JSON.stringify({ error: "Not found" }), { status: 404 })

  const content = resume.content as ResumeContent
  const buffer = await renderToBuffer(
    createElement(ResumePDF, { content, title: resume.title })
  )

  const filename = `${resume.title.replace(/[^a-z0-9]/gi, "-").toLowerCase()}.pdf`
  return new Response(new Uint8Array(buffer), {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
    },
  })
}
