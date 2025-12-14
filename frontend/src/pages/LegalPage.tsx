import { Link } from 'react-router-dom'

export default function LegalPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Legal Notice</h1>
        <div className="space-y-6">
          <div>
            <p className="text-neutral-600 mb-4">
              This legal notice governs the use of the ANTEX website and services.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Company Information</h2>
            <p className="text-neutral-600">
              ANTEX is a professional antenna design and simulation platform.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Disclaimer</h2>
            <p className="text-neutral-600">
              The information on this website is provided on an "as is" basis. While we strive to ensure accuracy, 
              we make no warranties, expressed or implied, regarding the completeness, accuracy, or reliability of 
              the information provided.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Limitation of Liability</h2>
            <p className="text-neutral-600">
              ANTEX shall not be liable for any direct, indirect, incidental, special, or consequential damages 
              arising from the use of this platform or the information contained herein.
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




