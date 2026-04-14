export default function ContactPage() {
  return (
    <div className="max-w-2xl mx-auto px-6 py-24">
      <h1 className="text-3xl font-bold mb-8">Contact Us</h1>

      <div className="space-y-6 text-gray-700">
        <p>
          Have a question, bug report, or feature request? We&apos;d love to hear from you.
        </p>

        <div className="bg-gray-50 rounded-xl p-6 space-y-4">
          <div>
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Email</p>
            <a
              href="mailto:hello@airesumebuilder.app"
              className="text-blue-600 hover:underline mt-1 block"
            >
              hello@airesumebuilder.app
            </a>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Response time</p>
            <p className="mt-1">We aim to respond within 1–2 business days.</p>
          </div>
        </div>

        <p className="text-sm text-gray-500">
          For billing issues, please include your registered email address and the last 4
          digits of your payment reference.
        </p>
      </div>
    </div>
  );
}
