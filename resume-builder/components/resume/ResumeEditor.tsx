"use client"

import { useState, useCallback, useRef } from "react"
import { ResumeForm } from "@/components/resume/ResumeForm"
import { ResumePreview } from "@/components/resume/ResumePreview"
import type { ResumeContent } from "@/components/resume/types"
import Link from "next/link"

interface Props {
  id: string
  initialTitle: string
  initialTemplate: string
  initialContent: ResumeContent
}

export function ResumeEditor({ id, initialTitle, initialTemplate, initialContent }: Props) {
  const [title, setTitle] = useState(initialTitle)
  const [template, setTemplate] = useState(initialTemplate)
  const [content, setContent] = useState<ResumeContent>(initialContent)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(true)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const save = useCallback(
    async (patch: { title?: string; template?: string; content?: ResumeContent }) => {
      setSaving(true)
      try {
        await fetch(`/api/resume/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
        })
        setSaved(true)
      } finally {
        setSaving(false)
      }
    },
    [id]
  )

  function scheduleSave(patch: { title?: string; template?: string; content?: ResumeContent }) {
    setSaved(false)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => save(patch), 1500)
  }

  function handleContentChange(next: ResumeContent) {
    setContent(next)
    scheduleSave({ content: next })
  }

  function handleTemplateChange(t: string) {
    setTemplate(t)
    scheduleSave({ template: t })
  }

  function handleTitleChange(t: string) {
    setTitle(t)
    scheduleSave({ title: t })
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 sticky top-0 z-10">
        <Link href="/dashboard" className="text-gray-400 hover:text-gray-600 text-sm">
          ← Dashboard
        </Link>
        <input
          value={title}
          onChange={(e) => handleTitleChange(e.target.value)}
          className="flex-1 text-sm font-semibold text-gray-900 bg-transparent border-none outline-none min-w-0"
          placeholder="Resume title"
        />
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleTemplateChange("classic")}
            className={`text-xs px-3 py-1.5 rounded-md border transition-colors ${
              template === "classic"
                ? "bg-blue-600 text-white border-blue-600"
                : "text-gray-600 border-gray-300 hover:border-blue-400"
            }`}
          >
            Classic
          </button>
          <button
            onClick={() => handleTemplateChange("modern")}
            className={`text-xs px-3 py-1.5 rounded-md border transition-colors ${
              template === "modern"
                ? "bg-blue-600 text-white border-blue-600"
                : "text-gray-600 border-gray-300 hover:border-blue-400"
            }`}
          >
            Modern
          </button>
          <span className="text-xs text-gray-400 ml-2">
            {saving ? "Saving…" : saved ? "Saved" : "Unsaved"}
          </span>
        </div>
      </header>

      {/* Split editor */}
      <div className="flex-1 flex overflow-hidden">
        <div className="w-1/2 overflow-y-auto border-r border-gray-200 bg-white p-6">
          <ResumeForm initialContent={content} onChange={handleContentChange} />
        </div>
        <div className="w-1/2 overflow-y-auto p-6">
          <ResumePreview content={content} template={template} title={title} />
        </div>
      </div>
    </div>
  )
}
