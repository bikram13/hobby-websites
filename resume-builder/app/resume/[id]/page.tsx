import { auth } from "@/auth"
import { redirect, notFound } from "next/navigation"
import { db } from "@/lib/prisma"
import { ResumeEditor } from "@/components/resume/ResumeEditor"
import type { ResumeContent } from "@/components/resume/types"

export default async function ResumePage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const session = await auth()
  if (!session?.user?.id) redirect("/auth/signin")

  const { id } = await params
  const resume = await db.resume.findFirst({
    where: { id, userId: session.user.id },
  })
  if (!resume) notFound()

  return (
    <ResumeEditor
      id={resume.id}
      initialTitle={resume.title}
      initialTemplate={resume.template}
      initialContent={resume.content as ResumeContent}
    />
  )
}
