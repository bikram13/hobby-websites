import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { db } from "@/lib/prisma"
import Link from "next/link"
import { NewResumeButton } from "@/components/resume/NewResumeButton"

export default async function DashboardPage() {
  const session = await auth()
  if (!session?.user?.id) redirect("/auth/signin")

  const resumes = await db.resume.findMany({
    where: { userId: session.user.id },
    orderBy: { updatedAt: "desc" },
    select: { id: true, title: true, template: true, updatedAt: true },
  })

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-gray-900">My Resumes</h1>
          <NewResumeButton />
        </div>

        {resumes.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
            <p className="text-gray-500 mb-4">No resumes yet. Create your first one!</p>
            <NewResumeButton />
          </div>
        ) : (
          <ul className="space-y-3">
            {resumes.map((resume) => (
              <li key={resume.id}>
                <Link
                  href={`/resume/${resume.id}`}
                  className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 hover:border-blue-400 hover:shadow-sm transition-all"
                >
                  <div>
                    <p className="font-semibold text-gray-900">{resume.title}</p>
                    <p className="text-sm text-gray-400 mt-0.5">
                      {resume.template === "modern" ? "Modern" : "Classic"} template &middot; Updated{" "}
                      {new Date(resume.updatedAt).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </p>
                  </div>
                  <span className="text-blue-500 text-sm font-medium">Edit &rarr;</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  )
}
