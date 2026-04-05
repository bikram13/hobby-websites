import { db } from "@/lib/prisma"
import crypto from "crypto"

function verifySignature(body: string, signature: string): boolean {
  const secret = process.env.RAZORPAY_WEBHOOK_SECRET
  if (!secret) return false
  const expected = crypto.createHmac("sha256", secret).update(body).digest("hex")
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature))
}

export async function POST(req: Request) {
  const body = await req.text()
  const signature = req.headers.get("x-razorpay-signature") ?? ""

  if (!verifySignature(body, signature)) {
    return new Response("Invalid signature", { status: 400 })
  }

  const event = JSON.parse(body)
  const { event: eventType, payload } = event

  // Extract userId from subscription notes or linked entity
  const notes = payload?.subscription?.entity?.notes ?? payload?.payment?.entity?.notes ?? {}
  const userId = notes?.userId as string | undefined

  if (!userId) return new Response("OK", { status: 200 })

  if (eventType === "subscription.activated" || eventType === "payment.captured") {
    await db.subscription.upsert({
      where: { userId },
      create: {
        userId,
        razorpaySubId: payload?.subscription?.entity?.id,
        status: "active",
        currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      },
      update: {
        status: "active",
        currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      },
    })
  }

  if (eventType === "subscription.cancelled" || eventType === "subscription.completed") {
    await db.subscription.updateMany({
      where: { userId },
      data: { status: "cancelled" },
    })
  }

  if (eventType === "subscription.halted" || eventType === "payment.failed") {
    await db.subscription.updateMany({
      where: { userId },
      data: { status: "halted" },
    })
  }

  return new Response("OK", { status: 200 })
}
