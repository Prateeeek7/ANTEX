import { Link } from 'react-router-dom'

export default function CaseStudiesPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Case Studies</h1>
        <p className="text-neutral-600 mb-6">
          Real-world examples of successful antenna designs using ANTEX.
        </p>
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>5G Base Station Antenna</h2>
            <p className="text-neutral-600 mb-2">
              Design and optimization of a compact patch antenna array for 5G base station applications at 28 GHz.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>IoT Sensor Antenna</h2>
            <p className="text-neutral-600 mb-2">
              Miniaturized meandered line antenna design for IoT sensor networks operating at 2.4 GHz.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>UWB Communication Antenna</h2>
            <p className="text-neutral-600 mb-2">
              Ultra-wideband planar monopole antenna optimized for 3.1-10.6 GHz range with excellent impedance matching.
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




