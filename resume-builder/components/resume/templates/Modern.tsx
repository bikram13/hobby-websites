import type { ResumeContent } from "@/components/resume/types"

interface Props {
  content: ResumeContent
  title: string
}

const ACCENT = "#1d4ed8" // blue-700, high contrast

export function ModernTemplate({ content, title }: Props) {
  const { contact, summary, experience, education, skills } = content

  const skillList = skills
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)

  return (
    <div
      style={{
        fontFamily: "Arial, sans-serif",
        fontSize: "12px",
        lineHeight: "1.5",
        color: "#111",
        maxWidth: "680px",
        margin: "0 auto",
        backgroundColor: "#fff",
      }}
    >
      {/* Accent header bar */}
      <div
        style={{
          backgroundColor: ACCENT,
          color: "#fff",
          padding: "28px 40px 24px",
        }}
      >
        <h1 style={{ fontSize: "24px", fontWeight: "bold", margin: "0 0 6px" }}>
          {contact.name || title}
        </h1>
        <p style={{ margin: "0", opacity: 0.9, fontSize: "11px" }}>
          {[contact.email, contact.phone, contact.location]
            .filter(Boolean)
            .join("   |   ")}
        </p>
        {(contact.linkedin || contact.website) && (
          <p style={{ margin: "4px 0 0", opacity: 0.9, fontSize: "11px" }}>
            {[contact.linkedin, contact.website].filter(Boolean).join("   |   ")}
          </p>
        )}
      </div>

      {/* Body */}
      <div style={{ padding: "28px 40px" }}>
        {/* Summary */}
        {summary && (
          <section style={{ marginBottom: "20px" }}>
            <SectionTitle>Summary</SectionTitle>
            <p style={{ margin: "6px 0 0" }}>{summary}</p>
          </section>
        )}

        {/* Work Experience */}
        {experience.length > 0 && (
          <section style={{ marginBottom: "20px" }}>
            <SectionTitle>Work Experience</SectionTitle>
            {experience.map((exp, i) => (
              <div key={i} style={{ marginTop: "12px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong style={{ color: "#111" }}>{exp.title}</strong>
                  <span style={{ color: "#555", fontSize: "11px" }}>
                    {exp.startDate} &ndash; {exp.current ? "Present" : exp.endDate}
                  </span>
                </div>
                <div style={{ color: ACCENT, fontWeight: "bold", fontSize: "11px", marginBottom: "4px" }}>
                  {exp.company}
                </div>
                {exp.bullets && (
                  <ul style={{ margin: "4px 0 0 16px", padding: 0 }}>
                    {exp.bullets
                      .split("\n")
                      .map((b) => b.trim())
                      .filter(Boolean)
                      .map((b, j) => (
                        <li key={j} style={{ marginBottom: "2px" }}>
                          {b}
                        </li>
                      ))}
                  </ul>
                )}
              </div>
            ))}
          </section>
        )}

        {/* Education */}
        {education.length > 0 && (
          <section style={{ marginBottom: "20px" }}>
            <SectionTitle>Education</SectionTitle>
            {education.map((edu, i) => (
              <div key={i} style={{ marginTop: "12px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong>{edu.school}</strong>
                  <span style={{ color: "#555", fontSize: "11px" }}>
                    {edu.startDate} &ndash; {edu.endDate}
                  </span>
                </div>
                <div style={{ color: "#555" }}>
                  {[edu.degree, edu.field].filter(Boolean).join(", ")}
                  {edu.gpa ? ` — GPA: ${edu.gpa}` : ""}
                </div>
              </div>
            ))}
          </section>
        )}

        {/* Skills */}
        {skillList.length > 0 && (
          <section>
            <SectionTitle>Skills</SectionTitle>
            <p style={{ margin: "6px 0 0" }}>{skillList.join("  •  ")}</p>
          </section>
        )}
      </div>
    </div>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <h2
        style={{
          fontSize: "13px",
          fontWeight: "bold",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: ACCENT,
          margin: "0",
        }}
      >
        {children}
      </h2>
      <hr style={{ borderTop: `2px solid ${ACCENT}`, margin: "4px 0 0" }} />
    </div>
  )
}
