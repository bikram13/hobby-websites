"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"

export function NewResumeButton() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  async function handleClick() {
    setLoading(true)
    try {
      const res = await fetch("/api/resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "Untitled Resume", template: "classic" }),
      })
      const resume = await res.json()
      router.push(`/resume/${resume.id}`)
    } catch {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
    >
      {loading ? "Creating…" : "+ New Resume"}
    </button>
  )
}
