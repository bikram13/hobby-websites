"use client"

import { useState, useCallback } from "react"
import Link from "next/link"

export function CoverLetterBuilder() {
  const [jobTitle, setJobTitle] = useState("")
  const [company, setCompany] = useState("")
  const [jobDescription, setJobDescription] = useState("")
  const [background, setBackground] = useState("")
  const [output, setOutput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [copied, setCopied] = useState(false)

  const generate = useCallback(async () => {
    if (!jobTitle.trim() && !jobDescription.trim()) return
    setLoading(true)
    setOutput("")
    setError("")
    try {
      const res = await fetch("/api/cover-letter/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobTitle, company, jobDescription, background }),
      })
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
  }, [jobTitle, company, jobDescription, background])

  async function downloadPDF() {
    const res = await fetch("/api/cover-letter/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: output, jobTitle, company }),
    })
    if (!res.ok) { alert("PDF export failed"); return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `cover-letter-${company || "draft"}.pdf`.replace(/\s+/g, "-").toLowerCase()
    a.click()
    URL.revokeObjectURL(url)
  }

  function copyText() {
    navigator.clipboard.writeText(output).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 sticky top-0 z-10">
        <Link href="/dashboard" className="text-gray-400 hover:text-gray-600 text-sm">← Dashboard</Link>
        <h1 className="text-sm font-semibold text-gray-900 flex-1">Cover Letter Builder</h1>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8 grid lg:grid-cols-2 gap-6">
        {/* Input panel */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-4">
            <h2 className="font-semibold text-gray-900">Job Details</h2>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Job Title *</label>
              <input
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Senior Software Engineer"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Company</label>
              <input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Acme Corp"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Job Description</label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={5}
                placeholder="Paste the job description here…"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 resize-y"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Your Background</label>
              <textarea
                value={background}
                onChange={(e) => setBackground(e.target.value)}
                rows={4}
                placeholder="Briefly describe your relevant experience and skills…"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 resize-y"
              />
            </div>
            <button
              onClick={generate}
              disabled={loading || (!jobTitle.trim() && !jobDescription.trim())}
              className="w-full py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Generating…" : "Generate Cover Letter"}
            </button>
          </div>
        </div>

        {/* Output panel */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Cover Letter</h2>
            {output && (
              <div className="flex gap-2">
                <button
                  onClick={generate}
                  disabled={loading}
                  className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 disabled:opacity-50"
                >
                  Regenerate
                </button>
                <button
                  onClick={copyText}
                  className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg text-gray-600 hover:border-blue-400"
                >
                  {copied ? "Copied!" : "Copy Text"}
                </button>
                <button
                  onClick={downloadPDF}
                  className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Download PDF
                </button>
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 min-h-[400px]">
            {!output && !loading && !error && (
              <p className="text-gray-400 text-sm italic">Your cover letter will appear here after you click Generate.</p>
            )}
            {loading && !output && (
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <span className="animate-spin inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                Writing your cover letter…
              </div>
            )}
            {error && <p className="text-red-500 text-sm">{error}</p>}
            {output && (
              <textarea
                value={output}
                onChange={(e) => setOutput(e.target.value)}
                className="w-full h-full min-h-[360px] text-sm text-gray-800 leading-relaxed resize-none focus:outline-none"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
