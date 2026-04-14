export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-24">
      <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>
      <p className="text-gray-500 mb-6 text-sm">Last updated: April 2026</p>

      <section className="prose prose-gray max-w-none space-y-6 text-gray-700">
        <p>
          Your privacy is important to us. This Privacy Policy explains how AI Resume Builder
          collects, uses, and protects your personal information.
        </p>

        <h2 className="text-xl font-semibold mt-8 mb-2">Information We Collect</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li>Email address (used solely for magic-link sign-in)</li>
          <li>Resume and cover letter content you create</li>
          <li>Subscription and payment status (processed by Razorpay)</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8 mb-2">How We Use Your Data</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li>To authenticate you and maintain your session</li>
          <li>To store and retrieve your resumes and cover letters</li>
          <li>To enforce subscription limits and process payments</li>
          <li>We do not sell or share your data with third parties</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8 mb-2">Data Retention</h2>
        <p>
          Your data is retained for as long as your account is active. You may request
          deletion at any time by contacting us.
        </p>

        <h2 className="text-xl font-semibold mt-8 mb-2">Contact</h2>
        <p>
          For privacy-related questions, please contact us at{' '}
          <a href="mailto:hello@airesumebuilder.app" className="text-blue-600 hover:underline">
            hello@airesumebuilder.app
          </a>
          .
        </p>
      </section>
    </div>
  );
}
