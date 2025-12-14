import { Link } from 'react-router-dom'

export default function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Terms & Conditions</h1>
        <div className="space-y-6">
          <div>
            <p className="text-neutral-600 mb-4">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Acceptance of Terms</h2>
            <p className="text-neutral-600 mb-2">
              By accessing and using ANTEX, you accept and agree to be bound by the terms and provisions of this agreement.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Use License</h2>
            <p className="text-neutral-600 mb-2">
              Permission is granted to temporarily use ANTEX for personal or commercial antenna design purposes. 
              This license does not include any right to resell or redistribute the software.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>User Accounts</h2>
            <p className="text-neutral-600 mb-2">
              You are responsible for maintaining the confidentiality of your account credentials and for all 
              activities that occur under your account.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Prohibited Uses</h2>
            <p className="text-neutral-600 mb-2">
              You may not use ANTEX in any way that could damage, disable, overburden, or impair the service 
              or interfere with any other party's use of the service.
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




