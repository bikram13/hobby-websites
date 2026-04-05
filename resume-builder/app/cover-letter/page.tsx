import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { CoverLetterBuilder } from "@/components/cover-letter/CoverLetterBuilder"

export default async function CoverLetterPage() {
  const session = await auth()
  if (!session?.user?.id) redirect("/auth/signin")

  return <CoverLetterBuilder />
}
