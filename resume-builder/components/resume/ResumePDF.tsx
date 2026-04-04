import { Document, Page, Text, View, StyleSheet } from "@react-pdf/renderer"
import type { ResumeContent } from "@/components/resume/types"

const styles = StyleSheet.create({
  page: { fontFamily: "Helvetica", fontSize: 10, padding: 40, color: "#1a1a1a", lineHeight: 1.3 },
  name: { fontSize: 20, fontFamily: "Helvetica-Bold", marginBottom: 4 },
  contactRow: { flexDirection: "row", flexWrap: "wrap", gap: 10, fontSize: 9, color: "#555555", marginBottom: 14 },
  contactItem: { fontSize: 9, color: "#555555" },
  sectionTitle: {
    fontSize: 10, fontFamily: "Helvetica-Bold",
    borderBottomWidth: 1, borderBottomColor: "#333333",
    paddingBottom: 2, marginBottom: 6, marginTop: 12,
    textTransform: "uppercase", letterSpacing: 0.5,
  },
  jobHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 2 },
  jobTitle: { fontSize: 10, fontFamily: "Helvetica-Bold" },
  jobMeta: { fontSize: 9, color: "#555555" },
  bullet: { fontSize: 9, marginLeft: 10, marginBottom: 2 },
  bodyText: { fontSize: 9, color: "#333333" },
  eduHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 1 },
  entryBlock: { marginBottom: 8 },
})

interface Props {
  content: ResumeContent
  title: string
}

export function ResumePDF({ content, title }: Props) {
  const { contact, summary, experience, education, skills } = content

  const contactItems = [
    contact.email, contact.phone, contact.location, contact.linkedin, contact.website,
  ].filter(Boolean)

  return (
    <Document title={title}>
      <Page size="LETTER" style={styles.page}>
        {/* Header */}
        {contact.name ? <Text style={styles.name}>{contact.name}</Text> : null}
        {contactItems.length > 0 && (
          <View style={styles.contactRow}>
            {contactItems.map((item, i) => (
              <Text key={i} style={styles.contactItem}>{item}</Text>
            ))}
          </View>
        )}

        {/* Summary */}
        {summary ? (
          <View>
            <Text style={styles.sectionTitle}>Summary</Text>
            <Text style={styles.bodyText}>{summary}</Text>
          </View>
        ) : null}

        {/* Experience */}
        {experience.length > 0 && (
          <View>
            <Text style={styles.sectionTitle}>Experience</Text>
            {experience.map((exp, i) => {
              const dates = exp.current
                ? `${exp.startDate} — Present`
                : `${exp.startDate}${exp.endDate ? ` — ${exp.endDate}` : ""}`
              const bullets = exp.bullets
                ? exp.bullets.split("\n").map((b) => b.replace(/^[-•*]\s*/, "").trim()).filter(Boolean)
                : []
              return (
                <View key={i} style={styles.entryBlock}>
                  <View style={styles.jobHeader}>
                    <Text style={styles.jobTitle}>{exp.title}{exp.company ? ` · ${exp.company}` : ""}</Text>
                    <Text style={styles.jobMeta}>{dates}</Text>
                  </View>
                  {bullets.map((b, j) => (
                    <Text key={j} style={styles.bullet}>• {b}</Text>
                  ))}
                </View>
              )
            })}
          </View>
        )}

        {/* Education */}
        {education.length > 0 && (
          <View>
            <Text style={styles.sectionTitle}>Education</Text>
            {education.map((edu, i) => {
              const degree = [edu.degree, edu.field].filter(Boolean).join(", ")
              const dates = `${edu.startDate}${edu.endDate ? ` — ${edu.endDate}` : ""}`
              return (
                <View key={i} style={styles.entryBlock}>
                  <View style={styles.eduHeader}>
                    <Text style={styles.jobTitle}>{edu.school}</Text>
                    <Text style={styles.jobMeta}>{dates}</Text>
                  </View>
                  {degree ? <Text style={styles.bodyText}>{degree}{edu.gpa ? ` · GPA ${edu.gpa}` : ""}</Text> : null}
                </View>
              )
            })}
          </View>
        )}

        {/* Skills */}
        {skills ? (
          <View>
            <Text style={styles.sectionTitle}>Skills</Text>
            <Text style={styles.bodyText}>{skills}</Text>
          </View>
        ) : null}
      </Page>
    </Document>
  )
}
