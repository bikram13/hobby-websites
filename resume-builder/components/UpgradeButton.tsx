"use client"

import { useState } from "react"

interface Props {
  userId: string
  className?: string
}

export function UpgradeButton({ userId, className = "" }: Props) {
  const [loading, setLoading] = useState(false)

  async function handleUpgrade() {
    setLoading(true)
    try {
      const res = await fetch("/api/subscription/create-order", { method: "POST" })
      if (!res.ok) throw new Error("Failed to create order")
      const { orderId, amount, currency } = await res.json()

      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
        amount,
        currency,
        name: "AI Resume Builder",
        description: "Pro Plan — ₹799/month",
        order_id: orderId,
        prefill: {},
        notes: { userId },
        theme: { color: "#2563eb" },
        handler: async () => {
          // Payment captured — webhook handles DB update
          window.location.reload()
        },
      }

      // @ts-expect-error Razorpay is loaded via script tag
      const rzp = new window.Razorpay(options)
      rzp.open()
    } catch {
      alert("Something went wrong. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleUpgrade}
      disabled={loading}
      className={`bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 ${className}`}
    >
      {loading ? "Loading…" : "Upgrade to Pro — ₹799/mo"}
    </button>
  )
}
