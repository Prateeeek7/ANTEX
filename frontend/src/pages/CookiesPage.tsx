import { Link } from 'react-router-dom'

export default function CookiesPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Cookie Policy</h1>
        <div className="space-y-6">
          <div>
            <p className="text-neutral-600 mb-4">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>What Are Cookies</h2>
            <p className="text-neutral-600 mb-2">
              Cookies are small text files that are placed on your device when you visit our website. They help 
              us provide you with a better experience by remembering your preferences and settings.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>How We Use Cookies</h2>
            <p className="text-neutral-600 mb-2">
              We use cookies to authenticate users, remember your preferences, analyze site usage, and improve 
              our services.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Types of Cookies</h2>
            <ul className="list-disc list-inside space-y-2 text-neutral-600">
              <li>Essential cookies: Required for the website to function properly</li>
              <li>Authentication cookies: Used to maintain your login session</li>
              <li>Analytics cookies: Help us understand how visitors use our site</li>
            </ul>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Managing Cookies</h2>
            <p className="text-neutral-600 mb-2">
              You can control and manage cookies through your browser settings. Note that disabling certain cookies 
              may affect the functionality of the website.
            </p>
          </div>
        </div>
        <div className="mt-8">
          <Link to="/" className="btn-primary inline-flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}




