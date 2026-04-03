"use client"

import { useState } from "react"
import type { ResumeContent, ExperienceEntry, EducationEntry } from "./types"
import { emptyContent } from "./types"

interface Props {
  initialContent: ResumeContent
  onChange: (content: ResumeContent) => void
}

export function ResumeForm({ initialContent, onChange }: Props) {
  const [content, setContent] = useState<ResumeContent>(initialContent)

  function update(patch: Partial<ResumeContent>) {
    const next = { ...content, ...patch }
    setContent(next)
    onChange(next)
  }

  function updateContact(patch: Partial<ResumeContent["contact"]>) {
    update({ contact: { ...content.contact, ...patch } })
  }

  // ---- Experience helpers ----
  function addExperience() {
    update({
      experience: [
        ...content.experience,
        { company: "", title: "", startDate: "", endDate: "", current: false, bullets: "" },
      ],
    })
  }

  function updateExperience(index: number, patch: Partial<ExperienceEntry>) {
    const next = content.experience.map((e, i) => (i === index ? { ...e, ...patch } : e))
    update({ experience: next })
  }

  function removeExperience(index: number) {
    update({ experience: content.experience.filter((_, i) => i !== index) })
  }

  // ---- Education helpers ----
  function addEducation() {
    update({
      education: [
        ...content.education,
        { school: "", degree: "", field: "", startDate: "", endDate: "", gpa: "" },
      ],
    })
  }

  function updateEducation(index: number, patch: Partial<EducationEntry>) {
    const next = content.education.map((e, i) => (i === index ? { ...e, ...patch } : e))
    update({ education: next })
  }

  function removeEducation(index: number) {
    update({ education: content.education.filter((_, i) => i !== index) })
  }

  return (
    <div className="space-y-8">
      {/* Contact Info */}
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Contact Info
        </h2>
        <div className="grid grid-cols-2 gap-3">
          <Field
            label="Full Name"
            value={content.contact.name}
            onChange={(v) => updateContact({ name: v })}
            colSpan={2}
          />
          <Field
            label="Email"
            type="email"
            value={content.contact.email}
            onChange={(v) => updateContact({ email: v })}
          />
          <Field
            label="Phone"
            value={content.contact.phone}
            onChange={(v) => updateContact({ phone: v })}
          />
          <Field
            label="Location"
            value={content.contact.location}
            onChange={(v) => updateContact({ location: v })}
          />
          <Field
            label="LinkedIn URL"
            value={content.contact.linkedin}
            onChange={(v) => updateContact({ linkedin: v })}
          />
          <Field
            label="Website"
            value={content.contact.website}
            onChange={(v) => updateContact({ website: v })}
            colSpan={2}
          />
        </div>
      </section>

      {/* Professional Summary */}
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Professional Summary
        </h2>
        <textarea
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows={4}
          placeholder="Write 2-3 sentences summarising your experience and goals..."
          value={content.summary}
          onChange={(e) => update({ summary: e.target.value })}
        />
      </section>

      {/* Work Experience */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
            Work Experience
          </h2>
          <button
            type="button"
            onClick={addExperience}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            + Add Position
          </button>
        </div>
        <div className="space-y-6">
          {content.experience.map((exp, i) => (
            <div key={i} className="border border-gray-200 rounded-lg p-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400 font-medium">Position {i + 1}</span>
                <button
                  type="button"
                  onClick={() => removeExperience(i)}
                  className="text-xs text-red-400 hover:text-red-600"
                >
                  Remove
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Field
                  label="Job Title"
                  value={exp.title}
                  onChange={(v) => updateExperience(i, { title: v })}
                />
                <Field
                  label="Company"
                  value={exp.company}
                  onChange={(v) => updateExperience(i, { company: v })}
                />
                <Field
                  label="Start Date"
                  value={exp.startDate}
                  placeholder="e.g. Jan 2022"
                  onChange={(v) => updateExperience(i, { startDate: v })}
                />
                <div>
                  <Field
                    label="End Date"
                    value={exp.endDate}
                    placeholder="e.g. Dec 2023"
                    onChange={(v) => updateExperience(i, { endDate: v })}
                    disabled={exp.current}
                  />
                  <label className="flex items-center gap-1.5 mt-1.5 text-xs text-gray-500 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={exp.current}
                      onChange={(e) => updateExperience(i, { current: e.target.checked })}
                      className="rounded"
                    />
                    Currently working here
                  </label>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Bullet Points (one per line)
                </label>
                <textarea
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={4}
                  placeholder="Led a team of 5 engineers to deliver..."
                  value={exp.bullets}
                  onChange={(e) => updateExperience(i, { bullets: e.target.value })}
                />
              </div>
            </div>
          ))}
          {content.experience.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-4">No positions added yet.</p>
          )}
        </div>
      </section>

      {/* Education */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
            Education
          </h2>
          <button
            type="button"
            onClick={addEducation}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            + Add Education
          </button>
        </div>
        <div className="space-y-6">
          {content.education.map((edu, i) => (
            <div key={i} className="border border-gray-200 rounded-lg p-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400 font-medium">Education {i + 1}</span>
                <button
                  type="button"
                  onClick={() => removeEducation(i)}
                  className="text-xs text-red-400 hover:text-red-600"
                >
                  Remove
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Field
                  label="School / University"
                  value={edu.school}
                  onChange={(v) => updateEducation(i, { school: v })}
                  colSpan={2}
                />
                <Field
                  label="Degree"
                  value={edu.degree}
                  placeholder="e.g. Bachelor of Science"
                  onChange={(v) => updateEducation(i, { degree: v })}
                />
                <Field
                  label="Field of Study"
                  value={edu.field}
                  placeholder="e.g. Computer Science"
                  onChange={(v) => updateEducation(i, { field: v })}
                />
                <Field
                  label="Start Year"
                  value={edu.startDate}
                  placeholder="e.g. 2018"
                  onChange={(v) => updateEducation(i, { startDate: v })}
                />
                <Field
                  label="End Year"
                  value={edu.endDate}
                  placeholder="e.g. 2022"
                  onChange={(v) => updateEducation(i, { endDate: v })}
                />
                <Field
                  label="GPA (optional)"
                  value={edu.gpa}
                  placeholder="e.g. 3.8"
                  onChange={(v) => updateEducation(i, { gpa: v })}
                />
              </div>
            </div>
          ))}
          {content.education.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-4">No education added yet.</p>
          )}
        </div>
      </section>

      {/* Skills */}
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Skills
        </h2>
        <input
          type="text"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Python, React, SQL, Project Management..."
          value={content.skills}
          onChange={(e) => update({ skills: e.target.value })}
        />
        <p className="text-xs text-gray-400 mt-1">Separate skills with commas</p>
      </section>
    </div>
  )
}

// ---- Reusable field component ----
interface FieldProps {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
  colSpan?: number
  disabled?: boolean
}

function Field({ label, value, onChange, placeholder, type = "text", colSpan, disabled }: FieldProps) {
  return (
    <div className={colSpan === 2 ? "col-span-2" : ""}>
      <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
      <input
        type={type}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
      />
    </div>
  )
}
