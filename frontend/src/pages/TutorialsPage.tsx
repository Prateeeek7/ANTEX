import { Link } from 'react-router-dom'

export default function TutorialsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Tutorials</h1>
        <p className="text-neutral-600 mb-6">
          Step-by-step tutorials to help you get started with ANTEX antenna design tools.
        </p>
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Getting Started</h2>
            <p className="text-neutral-600 mb-2">
              Learn how to create your first antenna project and run optimization algorithms.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Optimization Algorithms</h2>
            <p className="text-neutral-600 mb-2">
              Understand how Genetic Algorithms and Particle Swarm Optimization work for antenna design.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>FDTD Simulation</h2>
            <p className="text-neutral-600 mb-2">
              Learn to run 3D electromagnetic simulations and interpret results.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>RF Analysis</h2>
            <p className="text-neutral-600 mb-2">
              Master Smith Chart analysis and impedance matching techniques.
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




