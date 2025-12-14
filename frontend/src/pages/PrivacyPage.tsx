import { Link } from 'react-router-dom'

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Privacy Policy</h1>
        <div className="space-y-6">
          <div>
            <p className="text-neutral-600 mb-4">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Information We Collect</h2>
            <p className="text-neutral-600 mb-2">
              We collect information you provide directly to us, including account information, project data, 
              and usage information to improve our services.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>How We Use Your Information</h2>
            <p className="text-neutral-600 mb-2">
              We use the information we collect to provide, maintain, and improve our services, process transactions, 
              and communicate with you.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Data Security</h2>
            <p className="text-neutral-600 mb-2">
              We implement appropriate technical and organizational measures to protect your personal information 
              against unauthorized access, alteration, disclosure, or destruction.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Your Rights</h2>
            <p className="text-neutral-600 mb-2">
              You have the right to access, update, or delete your personal information at any time through your 
              account settings or by contacting us.
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




