import { Link } from 'react-router-dom'

export default function TechnologyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Technology</h1>
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Frontend</h2>
            <p className="text-neutral-600 mb-2">
              Built with React, TypeScript, and Tailwind CSS for a modern, responsive user interface.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Backend</h2>
            <p className="text-neutral-600 mb-2">
              FastAPI-based REST API with PostgreSQL database for robust data management.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Optimization</h2>
            <p className="text-neutral-600 mb-2">
              Custom implementations of Genetic Algorithms and Particle Swarm Optimization using NumPy and SciPy.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Simulation</h2>
            <p className="text-neutral-600 mb-2">
              Pure Python 3D FDTD solver for electromagnetic simulation with full field visualization capabilities.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Deployment</h2>
            <p className="text-neutral-600 mb-2">
              Docker containerization for easy deployment and scalability across different environments.
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




