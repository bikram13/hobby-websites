import Link from "next/link"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "AI Resume Builder — ATS-Optimised Resumes in Minutes",
  description:
    "Build a professional, ATS-optimised resume and cover letter with AI in minutes. Two clean templates, AI suggestions, PDF export. Free to start.",
  openGraph: {
    title: "AI Resume Builder — ATS-Optimised Resumes in Minutes",
    description:
      "Build a professional, ATS-optimised resume and cover letter with AI. Free to start.",
    type: "website",
    url: "https://resume-builder.vercel.app/",
  },
}

const features = [
  {
    icon: "✨",
    title: "AI-powered suggestions",
    desc: "Claude rewrites your bullet points using the CAR framework and optimises your summary for the role.",
  },
  {
    icon: "📄",
    title: "Two ATS-friendly templates",
    desc: "Classic and Modern layouts designed to pass Applicant Tracking Systems used by 98% of Fortune 500 companies.",
  },
  {
    icon: "⬇️",
    title: "PDF export",
    desc: "Download a clean, selectable-text PDF instantly. No watermarks, no subscriptions just to export.",
  },
  {
    icon: "✉️",
    title: "Cover Letter Builder",
    desc: "Input the job description and your background — AI writes a tailored 3-paragraph cover letter in seconds.",
  },
  {
    icon: "🔒",
    title: "Private by default",
    desc: "Your resume data is tied to your account and never used for training. Sign in with just your email.",
  },
  {
    icon: "💾",
    title: "Auto-save",
    desc: "Every keystroke is saved automatically. Pick up where you left off from any device.",
  },
]

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Nav */}
      <header className="border-b border-gray-100 px-4 py-3">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <span className="font-bold text-gray-900 text-lg">ResumeAI</span>
          <div className="flex items-center gap-3">
            <Link href="/auth/signin" className="text-sm text-gray-600 hover:text-gray-900">Sign in</Link>
            <Link href="/auth/signin"
              className="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
              Get started free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-4 pt-20 pb-16 text-center">
        <div className="inline-block bg-blue-50 text-blue-700 text-xs font-semibold px-3 py-1 rounded-full mb-5">
          Powered by Claude AI
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 leading-tight mb-5">
          Land more interviews with<br className="hidden sm:block" />
          an AI-crafted resume
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-8">
          Build a professional, ATS-optimised resume and cover letter in minutes.
          AI rewrites your bullets, you stay in control.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/auth/signin"
            className="bg-blue-600 text-white px-8 py-3 rounded-xl font-semibold text-lg hover:bg-blue-700">
            Build my resume — it&apos;s free
          </Link>
          <Link href="#features"
            className="border border-gray-300 text-gray-700 px-8 py-3 rounded-xl font-semibold text-lg hover:border-blue-400">
            See how it works
          </Link>
        </div>
        <p className="text-xs text-gray-400 mt-4">No credit card required · Sign in with email</p>
      </section>

      {/* Features */}
      <section id="features" className="bg-gray-50 py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-10">Everything you need to get hired</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div key={f.title} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                <div className="text-2xl mb-3">{f.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Simple pricing</h2>
          <p className="text-gray-500 mb-10">Start free. Upgrade when you need more AI generations.</p>
          <div className="grid sm:grid-cols-2 gap-6">
            {/* Free */}
            <div className="rounded-2xl border border-gray-200 p-8 text-left">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Free</p>
              <p className="text-4xl font-bold text-gray-900 mb-1">₹0</p>
              <p className="text-sm text-gray-400 mb-6">forever</p>
              <ul className="space-y-2 text-sm text-gray-600 mb-8">
                <li>✓ Unlimited resumes &amp; cover letters</li>
                <li>✓ 2 ATS templates</li>
                <li>✓ PDF export</li>
                <li>✓ 3 AI generations per day</li>
                <li>✓ Auto-save</li>
              </ul>
              <Link href="/auth/signin"
                className="block text-center border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:border-blue-400 font-medium text-sm">
                Get started free
              </Link>
            </div>
            {/* Pro */}
            <div className="rounded-2xl border-2 border-blue-600 p-8 text-left relative">
              <div className="absolute -top-3 left-6 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">Most popular</div>
              <p className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2">Pro</p>
              <p className="text-4xl font-bold text-gray-900 mb-1">₹799</p>
              <p className="text-sm text-gray-400 mb-6">per month</p>
              <ul className="space-y-2 text-sm text-gray-600 mb-8">
                <li>✓ Everything in Free</li>
                <li>✓ Unlimited AI generations</li>
                <li>✓ Priority support</li>
                <li>✓ New templates as released</li>
              </ul>
              <Link href="/auth/signin"
                className="block text-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium text-sm">
                Start Pro
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-blue-600 py-14 px-4 text-center">
        <h2 className="text-2xl font-bold text-white mb-3">Ready to land your next role?</h2>
        <p className="text-blue-100 mb-6">Join thousands of job seekers who built their resume with AI.</p>
        <Link href="/auth/signin"
          className="inline-block bg-white text-blue-600 font-semibold px-8 py-3 rounded-xl hover:bg-blue-50 text-lg">
          Build my resume for free
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 px-4 text-center text-sm text-gray-400">
        <div className="max-w-5xl mx-auto flex flex-wrap justify-center gap-6">
          <Link href="/privacy" className="hover:text-gray-600">Privacy Policy</Link>
          <Link href="/about" className="hover:text-gray-600">About</Link>
          <Link href="/contact" className="hover:text-gray-600">Contact</Link>
        </div>
        <p className="mt-4">&copy; {new Date().getFullYear()} ResumeAI. All rights reserved.</p>
      </footer>
    </main>
  )
}
