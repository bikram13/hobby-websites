"use client"

import { useState, useCallback } from "react"

interface Props {
  section: string
  currentContent: string
  jobTitle?: string
  onApply: (text: string) => void
}

export function AIImproveButton({ section, currentContent, jobTitle = "", onApply }: Props) {
  const [open, setOpen] = useState(false)
  const [output, setOutput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const generate = useCallback(async () => {
    setLoading(true)
    setOutput("")
    setError("")
    try {
      const res = await fetch("/api/resume/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ section, currentContent, jobTitle }),
      })
      if (res.status === 429) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || "Daily limit reached. Try again tomorrow.")
      }
      if (!res.ok) throw new Error("Generation failed")
      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      if (!reader) throw new Error("No stream")
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        setOutput((prev) => prev + decoder.decode(value))
      }
    } catch {
      setError("Generation failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }, [section, currentContent, jobTitle])

  function handleOpen() {
    setOpen(true)
    generate()
  }

  return (
    <>
      <button
        type="button"
        onClick={handleOpen}
        className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 mt-1"
      >
        ✨ Improve with AI
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
            <div className="p-5 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">AI Suggestion</h3>
              <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600 text-lg leading-none">×</button>
            </div>

            <div className="p-5 min-h-[120px]">
              {loading && !output && (
                <div className="flex items-center gap-2 text-gray-400 text-sm">
                  <span className="animate-spin inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                  Generating…
                </div>
              )}
              {error && <p className="text-red-500 text-sm">{error}</p>}
              {output && <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">{output}</p>}
            </div>

            <div className="p-4 border-t border-gray-100 flex gap-2 justify-end">
              <button onClick={generate} disabled={loading} className="text-sm px-3 py-1.5 border border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 disabled:opacity-50">
                Regenerate
              </button>
              <button onClick={() => { onApply(output); setOpen(false) }} disabled={!output || loading} className="text-sm px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                Use this
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
