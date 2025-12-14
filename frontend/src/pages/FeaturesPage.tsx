import { Link } from 'react-router-dom'

export default function FeaturesPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-3xl font-bold mb-4" style={{ color: '#3a606e' }}>Features</h1>
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>AI-Powered Optimization</h2>
            <p className="text-neutral-600">
              Genetic Algorithms and Particle Swarm Optimization to automatically find optimal antenna geometries 
              that meet your specifications.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Multi-Shape Geometry Support</h2>
            <p className="text-neutral-600">
              Support for multiple antenna families including patch antennas, slot antennas, meandered lines, and 
              planar monopoles with parametric control.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>3D FDTD Simulation</h2>
            <p className="text-neutral-600">
              Industry-grade 3D Finite-Difference Time-Domain simulation for accurate electromagnetic field analysis 
              and S-parameter extraction.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>RF Analysis Tools</h2>
            <p className="text-neutral-600">
              Interactive Smith Charts, impedance matching recommendations, and comprehensive RF parameter analysis.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Performance Dashboard</h2>
            <p className="text-neutral-600">
              Comprehensive performance metrics including gain, efficiency, beamwidth, and overall design score.
            </p>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Export Capabilities</h2>
            <p className="text-neutral-600">
              Export geometries as SVG, DXF, or STL files for fabrication, and generate comprehensive PDF reports.
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




