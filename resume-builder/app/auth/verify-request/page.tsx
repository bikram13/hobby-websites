export default function VerifyRequestPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg
            className="w-8 h-8 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Check your email
        </h1>
        <p className="text-gray-500 text-sm">
          A sign-in link has been sent to your email address. Click it to sign
          in — the link expires in 24 hours.
        </p>
        <p className="text-gray-400 text-xs mt-4">
          Didn&apos;t receive it? Check your spam folder or{" "}
          <a href="/auth/signin" className="text-blue-600 hover:underline">
            try again
          </a>
          .
        </p>
      </div>
    </main>
  )
}
