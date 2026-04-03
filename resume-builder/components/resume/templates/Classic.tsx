import type { ResumeContent } from "@/components/resume/types"

interface Props {
  content: ResumeContent
  title: string
}

export function ClassicTemplate({ content, title }: Props) {
  const { contact, summary, experience, education, skills } = content

  const skillList = skills
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)

  return (
    <div
      style={{
        fontFamily: "Georgia, serif",
        fontSize: "12px",
        lineHeight: "1.5",
        color: "#111",
        maxWidth: "680px",
        margin: "0 auto",
        padding: "40px 48px",
        backgroundColor: "#fff",
      }}
    >
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "24px" }}>
        <h1 style={{ fontSize: "22px", fontWeight: "bold", margin: "0 0 4px" }}>
          {contact.name || title}
        </h1>
        <p style={{ margin: "0", color: "#444" }}>
          {[contact.email, contact.phone, contact.location]
            .filter(Boolean)
            .join("  |  ")}
        </p>
        {(contact.linkedin || contact.website) && (
          <p style={{ margin: "4px 0 0", color: "#444" }}>
            {[contact.linkedin, contact.website].filter(Boolean).join("  |  ")}
          </p>
        )}
      </div>

      <hr style={{ borderTop: "2px solid #111", margin: "0 0 16px" }} />

      {/* Summary */}
      {summary && (
        <section style={{ marginBottom: "16px" }}>
          <h2 style={sectionHeading}>Summary</h2>
          <hr style={divider} />
          <p style={{ margin: "6px 0 0" }}>{summary}</p>
        </section>
      )}

      {/* Work Experience */}
      {experience.length > 0 && (
        <section style={{ marginBottom: "16px" }}>
          <h2 style={sectionHeading}>Work Experience</h2>
          <hr style={divider} />
          {experience.map((exp, i) => (
            <div key={i} style={{ marginTop: "10px" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{exp.title}</strong>
                <span style={{ color: "#555" }}>
                  {exp.startDate} &ndash; {exp.current ? "Present" : exp.endDate}
                </span>
              </div>
              <div style={{ color: "#555", marginBottom: "4px" }}>{exp.company}</div>
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
        <section style={{ marginBottom: "16px" }}>
          <h2 style={sectionHeading}>Education</h2>
          <hr style={divider} />
          {education.map((edu, i) => (
            <div key={i} style={{ marginTop: "10px" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{edu.school}</strong>
                <span style={{ color: "#555" }}>
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
          <h2 style={sectionHeading}>Skills</h2>
          <hr style={divider} />
          <p style={{ margin: "6px 0 0" }}>{skillList.join("  •  ")}</p>
        </section>
      )}
    </div>
  )
}

const sectionHeading: React.CSSProperties = {
  fontSize: "13px",
  fontWeight: "bold",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  margin: "0",
}

const divider: React.CSSProperties = {
  borderTop: "1px solid #111",
  margin: "4px 0 0",
}
