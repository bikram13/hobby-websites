export type ExperienceEntry = {
  company: string
  title: string
  startDate: string
  endDate: string
  current: boolean
  bullets: string
}

export type EducationEntry = {
  school: string
  degree: string
  field: string
  startDate: string
  endDate: string
  gpa: string
}

export type ResumeContent = {
  contact: {
    name: string
    email: string
    phone: string
    location: string
    linkedin: string
    website: string
  }
  summary: string
  experience: ExperienceEntry[]
  education: EducationEntry[]
  skills: string
}

export const emptyContent: ResumeContent = {
  contact: { name: "", email: "", phone: "", location: "", linkedin: "", website: "" },
  summary: "",
  experience: [],
  education: [],
  skills: "",
}
