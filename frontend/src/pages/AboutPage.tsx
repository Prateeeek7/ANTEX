import { Link } from 'react-router-dom'

export default function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-4xl font-bold mb-2" style={{ color: '#3a606e' }}>About ANTEX</h1>
        <p className="text-lg text-neutral-600 mb-8">
          Industry-grade antenna design and simulation platform powered by AI optimization and advanced EM simulation.
        </p>
        
        <div className="space-y-8">
          <div>
            <h2 className="text-2xl font-semibold mb-4" style={{ color: '#607b7d' }}>Our Mission</h2>
            <p className="text-neutral-700 mb-4 leading-relaxed">
              ANTEX was created to revolutionize antenna design workflows by combining the power of artificial 
              intelligence with industry-grade electromagnetic simulation. Our mission is to provide engineers 
              with accessible, powerful tools that bridge the gap between conceptual design and manufacturing-ready 
              antenna solutions.
            </p>
            <p className="text-neutral-700 leading-relaxed">
              We believe that antenna design should be fast, intuitive, and accurate. By automating optimization 
              processes and providing comprehensive analysis tools, we enable engineers to focus on innovation 
              rather than repetitive design iterations.
            </p>
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4" style={{ color: '#607b7d' }}>What Makes ANTEX Different</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="border-l-4 pl-4" style={{ borderColor: '#607b7d' }}>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>AI-Powered Optimization</h3>
                <p className="text-neutral-600">
                  Advanced Genetic Algorithms and Particle Swarm Optimization automatically explore design spaces 
                  to find optimal solutions that meet your specifications.
                </p>
              </div>
              <div className="border-l-4 pl-4" style={{ borderColor: '#607b7d' }}>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Industry-Grade Simulation</h3>
                <p className="text-neutral-600">
                  3D FDTD electromagnetic simulation provides accurate S-parameters, radiation patterns, and 
                  field visualizations comparable to commercial EM tools.
                </p>
              </div>
              <div className="border-l-4 pl-4" style={{ borderColor: '#607b7d' }}>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Comprehensive Analysis</h3>
                <p className="text-neutral-600">
                  Integrated RF analysis tools including Smith Charts, impedance matching, and performance 
                  metrics provide complete design evaluation.
                </p>
              </div>
              <div className="border-l-4 pl-4" style={{ borderColor: '#607b7d' }}>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Multi-Shape Support</h3>
                <p className="text-neutral-600">
                  Support for multiple antenna families (patch, slot, meandered, monopole) with parametric 
                  control and auto-design capabilities.
                </p>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4" style={{ color: '#607b7d' }}>Key Capabilities</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Design & Optimization</h3>
                <ul className="list-disc list-inside space-y-2 text-neutral-600">
                  <li>Multi-shape antenna geometry support with 8+ shape families</li>
                  <li>Genetic Algorithm (GA) optimization with customizable parameters</li>
                  <li>Particle Swarm Optimization (PSO) for fast convergence</li>
                  <li>Auto-design feature for intelligent initial parameter selection</li>
                  <li>Parametric geometry control with constraint handling</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Simulation & Analysis</h3>
                <ul className="list-disc list-inside space-y-2 text-neutral-600">
                  <li>3D FDTD electromagnetic simulation with field visualization</li>
                  <li>S-parameter extraction and Touchstone file export</li>
                  <li>Interactive Smith Chart analysis</li>
                  <li>AI-powered impedance matching recommendations</li>
                  <li>3D radiation pattern visualization</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Performance Evaluation</h3>
                <ul className="list-disc list-inside space-y-2 text-neutral-600">
                  <li>Comprehensive performance metrics dashboard</li>
                  <li>Overall score calculation with detailed breakdown</li>
                  <li>Gain, efficiency, and beamwidth analysis</li>
                  <li>Bandwidth and frequency accuracy evaluation</li>
                  <li>Comparative analysis of multiple design candidates</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#607b7d' }}>Export & Integration</h3>
                <ul className="list-disc list-inside space-y-2 text-neutral-600">
                  <li>Geometry export as SVG, DXF, and STL formats</li>
                  <li>Comprehensive PDF report generation</li>
                  <li>Touchstone file export for external tools</li>
                  <li>RESTful API for programmatic access</li>
                  <li>Docker containerization for easy deployment</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4" style={{ color: '#607b7d' }}>Technology Stack</h2>
            <p className="text-neutral-700 mb-4 leading-relaxed">
              ANTEX is built on modern, open-source technologies to ensure reliability, performance, and extensibility:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600">
              <li><strong>Frontend:</strong> React, TypeScript, Tailwind CSS for responsive, modern UI</li>
              <li><strong>Backend:</strong> FastAPI (Python) for high-performance REST API</li>
              <li><strong>Database:</strong> PostgreSQL for robust data management</li>
              <li><strong>Optimization:</strong> Custom GA/PSO implementations using NumPy and SciPy</li>
              <li><strong>Simulation:</strong> Pure Python 3D FDTD solver for EM simulation</li>
              <li><strong>Deployment:</strong> Docker and Docker Compose for containerized deployment</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4" style={{ color: '#607b7d' }}>Use Cases</h2>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-neutral-50 rounded-lg">
                <h3 className="font-semibold mb-2" style={{ color: '#607b7d' }}>5G & Wireless</h3>
                <p className="text-sm text-neutral-600">
                  Design antennas for 5G base stations, IoT devices, and wireless communication systems.
                </p>
              </div>
              <div className="p-4 bg-neutral-50 rounded-lg">
                <h3 className="font-semibold mb-2" style={{ color: '#607b7d' }}>Research & Education</h3>
                <p className="text-sm text-neutral-600">
                  Educational tool for teaching antenna design principles and optimization techniques.
                </p>
              </div>
              <div className="p-4 bg-neutral-50 rounded-lg">
                <h3 className="font-semibold mb-2" style={{ color: '#607b7d' }}>Rapid Prototyping</h3>
                <p className="text-sm text-neutral-600">
                  Quickly iterate on designs and validate concepts before detailed CAD modeling.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10 pt-8 border-t border-neutral-200">
          <div className="flex gap-4">
            <Link to="/features" className="btn-primary inline-flex items-center">
              View Features
            </Link>
            <Link to="/projects/new" className="btn-secondary inline-flex items-center">
              Get Started
            </Link>
            <Link to="/" className="btn-secondary inline-flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

