import { Link } from 'react-router-dom'

export default function HelpCenterPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Help Center</h1>
        <p className="text-neutral-600 mb-6">
          Find answers to common questions and get support for ANTEX.
        </p>
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>FAQs</h2>
            <p className="text-neutral-600 mb-2">
              Browse frequently asked questions about project creation, optimization, and simulation.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Documentation</h2>
            <p className="text-neutral-600 mb-2">
              Comprehensive documentation covering all features and capabilities.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Contact Support</h2>
            <p className="text-neutral-600 mb-2">
              Need additional help? Reach out to our support team for personalized assistance.
            </p>
          </div>
        </div>
        <div className="mt-8 flex gap-4">
          <Link to="/contact" className="btn-primary inline-flex items-center">
            Contact Support
          </Link>
          <Link to="/" className="btn-secondary inline-flex items-center">
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}




