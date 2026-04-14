import { streamText } from "ai"
import { anthropic } from "@ai-sdk/anthropic"
import { auth } from "@/auth"
import { aiRatelimit } from "@/lib/ratelimit"
import { db } from "@/lib/prisma"

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.id) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401 })
  }

  const subscription = await db.subscription.findUnique({
    where: { userId: session.user.id },
    select: { status: true, currentPeriodEnd: true },
  })
  const isSubscribed =
    subscription?.status === "active" &&
    subscription.currentPeriodEnd != null &&
    subscription.currentPeriodEnd > new Date()

  if (!isSubscribed) {
    const { success } = await aiRatelimit.limit(`coverletter:${session.user.id}`)
    if (!success) {
      return new Response(JSON.stringify({ error: "Daily limit reached (3/day). Resets at midnight." }), { status: 429 })
    }
  }

  const { jobTitle = "", company = "", jobDescription = "", background = "" } = await req.json().catch(() => ({}))

  if (!jobTitle && !jobDescription) {
    return new Response(JSON.stringify({ error: "jobTitle or jobDescription required" }), { status: 400 })
  }

  const result = streamText({
    model: anthropic("claude-haiku-4-5-20251001"),
    system:
      "You are an expert cover letter writer. Write in plain text only — no markdown, no asterisks, no headers. Write in first person. Be concise, professional, and persuasive. Output only the cover letter body (no address blocks, no date, no sign-off — just the paragraphs).",
    prompt: `Write a 3-paragraph cover letter body for a ${jobTitle || "professional"} role${company ? ` at ${company}` : ""}.

${jobDescription ? `Job description:\n${jobDescription}\n` : ""}${background ? `\nCandidate background:\n${background}` : ""}

Guidelines:
- Paragraph 1: Hook — express genuine interest in the role and company
- Paragraph 2: Value — highlight 2-3 specific skills/achievements that match the job
- Paragraph 3: Close — express enthusiasm, invite next steps

Write conversationally but professionally. No filler phrases like "I am writing to apply".`,
    maxOutputTokens: 500,
  })

  return result.toTextStreamResponse()
}
