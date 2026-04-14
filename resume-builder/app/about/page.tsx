export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-24">
      <h1 className="text-3xl font-bold mb-8">About AI Resume Builder</h1>

      <div className="space-y-6 text-gray-700">
        <p className="text-lg">
          AI Resume Builder helps job seekers create ATS-optimised resumes in minutes using
          the latest Claude AI models from Anthropic.
        </p>

        <p>
          We believe every candidate deserves a resume that clearly communicates their value.
          Our tool analyses your experience and rewrites it using language that passes
          applicant tracking systems and resonates with hiring managers.
        </p>

        <h2 className="text-xl font-semibold mt-8 mb-2">What We Offer</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li>AI-powered resume bullet point improvement</li>
          <li>Cover letter generation tailored to job descriptions</li>
          <li>ATS-friendly formatting</li>
          <li>Up to 3 free AI generations per day</li>
          <li>Unlimited generations on the Pro plan</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8 mb-2">Built With</h2>
        <p>
          Next.js · Auth.js · Prisma · Neon PostgreSQL · Anthropic Claude · Razorpay
        </p>
      </div>
    </div>
  );
}
