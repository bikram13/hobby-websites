import { streamText } from "ai"
import { anthropic } from "@ai-sdk/anthropic"
import { auth } from "@/auth"
import { aiRatelimit } from "@/lib/ratelimit"

function buildPrompt(section: string, currentContent: string, jobTitle: string): string {
  switch (section) {
    case "summary":
      return `Write a concise professional summary (2-3 sentences) for a ${jobTitle || "professional"} role. It should be ATS-optimized, highlight key strengths, and be written in first person without "I".${currentContent ? `\n\nExisting content to improve:\n${currentContent}` : ""}`
    case "experience":
      return `Rewrite these work experience bullet points using the CAR framework (Challenge-Action-Result). Start each bullet with a strong action verb. Keep each under 2 lines. Be specific and quantify achievements where possible.\n\nBullets to improve:\n${currentContent || "(empty — write 3 example strong bullets for a " + (jobTitle || "professional") + ")"}`
    case "skills":
      return `List 15 relevant technical and soft skills for a ${jobTitle || "professional"} role, comma-separated. Include a mix of hard skills and tools. No explanations, just the comma-separated list.`
    default:
      return `Improve this resume section for a ${jobTitle || "professional"} role:\n\n${currentContent}`
  }
}

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.id) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401 })
  }

  const { success } = await aiRatelimit.limit(`resume:${session.user.id}`)
  if (!success) {
    return new Response(JSON.stringify({ error: "Daily limit reached. You can generate 3 times per day on the free plan." }), { status: 429 })
  }

  const { section, currentContent = "", jobTitle = "" } = await req.json().catch(() => ({}))

  if (!section) {
    return new Response(JSON.stringify({ error: "section required" }), { status: 400 })
  }

  const result = streamText({
    model: anthropic("claude-haiku-4-5-20251001"), // haiku for speed + cost on generations
    system:
      "You are an expert resume writer. Write concisely, in plain text only — no markdown, no asterisks, no headers. Output only the requested content.",
    prompt: buildPrompt(section, currentContent, jobTitle),
    maxOutputTokens: 400,
  })

  return result.toTextStreamResponse()
}
