import { Link } from 'react-router-dom'

export default function RFAnalysisToolsPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-4xl font-bold mb-2" style={{ color: '#3a606e' }}>RF Analysis Tools</h1>
        <p className="text-lg text-neutral-600 mb-8">
          Comprehensive RF analysis tools for antenna design evaluation and optimization. ANTEX provides industry-grade 
          tools for analyzing impedance, S-parameters, and matching networks to ensure optimal antenna performance.
        </p>
        
        <div className="space-y-8">
          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Smith Chart Analysis</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              The Smith Chart is a powerful graphical tool for visualizing complex impedance and admittance values. 
              ANTEX provides an interactive Smith Chart that allows you to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li>Visualize impedance transformations across frequency ranges</li>
              <li>Identify resonance points and matching conditions</li>
              <li>Analyze VSWR (Voltage Standing Wave Ratio) circles</li>
              <li>Track impedance changes during optimization</li>
              <li>Compare multiple design candidates on a single chart</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Our Smith Chart supports frequency sweeps from DC to millimeter-wave frequencies, with automatic 
              scaling and zoom capabilities for detailed analysis. The chart includes constant resistance and 
              reactance circles, making it easy to understand impedance matching requirements.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>S-Parameter Analysis</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              Scattering parameters (S-parameters) are fundamental to RF circuit analysis. ANTEX provides comprehensive 
              S-parameter analysis including:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>S11 (Return Loss):</strong> Measures how much power is reflected from the antenna port</li>
              <li><strong>S21 (Transmission):</strong> Measures power transfer through the antenna system</li>
              <li><strong>Bandwidth Analysis:</strong> Automatic calculation of -10 dB and -3 dB bandwidth</li>
              <li><strong>Resonant Frequency Detection:</strong> Automatic identification of resonance points</li>
              <li><strong>Touchstone Export:</strong> Export S-parameters in industry-standard .s1p/.s2p formats</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              S-parameter data is extracted from FDTD simulations or analytical models, providing accurate 
              frequency-domain characterization. The analysis includes magnitude and phase information, enabling 
              complete RF performance evaluation.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>AI-Powered Impedance Matching</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              ANTEX includes intelligent impedance matching recommendations powered by machine learning algorithms. 
              The system analyzes your antenna's impedance characteristics and suggests optimal matching networks:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>L-Matching Networks:</strong> Simple two-element matching for narrowband applications</li>
              <li><strong>Pi and T Networks:</strong> Three-element matching for broader bandwidth</li>
              <li><strong>Stub Matching:</strong> Transmission line stub solutions for microstrip designs</li>
              <li><strong>Multi-Section Matching:</strong> Multi-stage matching for ultra-wideband designs</li>
              <li><strong>Component Value Calculation:</strong> Automatic calculation of inductor and capacitor values</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              The AI matching engine considers frequency range, bandwidth requirements, component tolerances, 
              and manufacturing constraints to provide practical, realizable matching solutions. Recommendations 
              include component values, Q-factor analysis, and sensitivity analysis.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Material Library</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              ANTEX includes an extensive material library with dielectric properties for common substrate materials:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li>FR-4 (εr = 4.4, tan δ = 0.02)</li>
              <li>Rogers RO4003C (εr = 3.38, tan δ = 0.0027)</li>
              <li>Rogers RT/duroid 5880 (εr = 2.2, tan δ = 0.0009)</li>
              <li>Alumina (εr = 9.8, tan δ = 0.0001)</li>
              <li>Custom material definitions with frequency-dependent properties</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Material properties are used in all RF calculations, ensuring accurate impedance predictions 
              and matching network designs. You can also define custom materials with frequency-dependent 
              permittivity and loss tangent values.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Parameter Sweep Analysis</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              Perform systematic parameter sweeps to understand design sensitivity and optimize performance:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li>Frequency sweeps with customizable resolution</li>
              <li>Geometry parameter sweeps (length, width, feed position)</li>
              <li>Substrate property sweeps (thickness, permittivity)</li>
              <li>Multi-dimensional sweeps for design space exploration</li>
              <li>Automated sensitivity analysis and optimization recommendations</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Parameter sweeps help identify critical design parameters and their impact on antenna performance, 
              enabling data-driven design decisions and robust optimization strategies.
            </p>
          </div>
        </div>

        <div className="mt-10 pt-8 border-t border-neutral-200">
          <h3 className="text-xl font-semibold mb-4" style={{ color: '#607b7d' }}>Getting Started</h3>
          <p className="text-neutral-600 mb-4">
            To use RF Analysis tools, navigate to any project and select the "Analysis" tab. The tools are 
            automatically available for all optimized designs and can be used with simulation results.
          </p>
          <div className="flex gap-4">
            <Link to="/projects/new" className="btn-primary inline-flex items-center">
              Create New Project
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

