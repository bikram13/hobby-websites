import { auth } from "@/auth"
import Razorpay from "razorpay"

// ₹799/month plan — create a subscription order
export async function POST(_req: Request) {
  const session = await auth()
  if (!session?.user?.id) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401 })
  }

  const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID!,
    key_secret: process.env.RAZORPAY_KEY_SECRET!,
  })

  const order = await razorpay.orders.create({
    amount: 79900, // ₹799 in paise
    currency: "INR",
    receipt: `sub_${session.user.id}_${Date.now()}`,
    notes: { userId: session.user.id },
  })

  return new Response(JSON.stringify({ orderId: order.id, amount: order.amount, currency: order.currency }), {
    headers: { "Content-Type": "application/json" },
  })
}
