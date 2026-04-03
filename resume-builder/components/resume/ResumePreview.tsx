"use client"

import { ClassicTemplate } from "@/components/resume/templates/Classic"
import { ModernTemplate } from "@/components/resume/templates/Modern"
import type { ResumeContent } from "@/components/resume/types"

interface Props {
  content: ResumeContent
  template: string
  title: string
}

export function ResumePreview({ content, template, title }: Props) {
  return (
    <div className="bg-gray-100 rounded-xl overflow-auto h-full min-h-[600px] p-4">
      <div className="shadow-lg rounded overflow-hidden">
        {template === "modern" ? (
          <ModernTemplate content={content} title={title} />
        ) : (
          <ClassicTemplate content={content} title={title} />
        )}
      </div>
    </div>
  )
}
