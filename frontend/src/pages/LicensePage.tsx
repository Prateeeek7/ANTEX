import { Link } from 'react-router-dom'

export default function LicensePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>License</h1>
        <div className="space-y-6">
          <div>
            <p className="text-neutral-600 mb-4">
              ANTEX is provided under a proprietary license. All rights reserved.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Copyright</h2>
            <p className="text-neutral-600">
              © {new Date().getFullYear()} ANTEX. All rights reserved.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Usage Terms</h2>
            <p className="text-neutral-600">
              This software and associated documentation files are proprietary and confidential. Unauthorized copying, 
              modification, distribution, or use of this software, via any medium, is strictly prohibited.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Open Source Components</h2>
            <p className="text-neutral-600">
              ANTEX uses various open-source libraries and frameworks, each with their own licenses. Please refer to 
              individual component licenses for specific terms.
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




