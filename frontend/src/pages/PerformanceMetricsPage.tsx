import { Link } from 'react-router-dom'

export default function PerformanceMetricsPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="card shadow-medium">
        <h1 className="text-4xl font-bold mb-2" style={{ color: '#3a606e' }}>Performance Metrics</h1>
        <p className="text-lg text-neutral-600 mb-8">
          Comprehensive performance evaluation metrics for antenna designs. ANTEX provides detailed analysis 
          of all critical antenna parameters to ensure your designs meet specifications and industry standards.
        </p>
        
        <div className="space-y-8">
          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Overall Performance Score</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              The overall performance score is a weighted composite metric (0-100) that evaluates multiple 
              aspects of antenna performance:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>Frequency Accuracy (30%):</strong> How close the resonant frequency matches the target</li>
              <li><strong>Bandwidth Achievement (25%):</strong> How well the design meets bandwidth requirements</li>
              <li><strong>Gain Performance (20%):</strong> Antenna gain relative to theoretical maximum</li>
              <li><strong>Efficiency (15%):</strong> Radiation efficiency and power handling</li>
              <li><strong>Impedance Matching (10%):</strong> VSWR and return loss performance</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              The scoring algorithm uses industry-standard weighting factors and provides a breakdown of 
              individual contributions, helping you identify areas for improvement.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Radiation Pattern Analysis</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              ANTEX provides comprehensive 3D radiation pattern visualization and analysis:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>3D Radiation Patterns:</strong> Interactive 3D visualization using Plotly.js</li>
              <li><strong>E-Plane and H-Plane Cuts:</strong> Standard 2D pattern cuts for analysis</li>
              <li><strong>Beamwidth Calculation:</strong> 3-dB and 10-dB beamwidth in both principal planes</li>
              <li><strong>Side Lobe Level:</strong> Maximum side lobe level relative to main beam</li>
              <li><strong>Front-to-Back Ratio:</strong> Ratio of forward to backward radiation</li>
              <li><strong>Polarization Analysis:</strong> Co-polar and cross-polar radiation patterns</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Radiation patterns are calculated from FDTD simulation results, providing accurate far-field 
              predictions. Patterns can be exported as images or data files for further analysis.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Gain and Directivity</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              Comprehensive gain and directivity metrics for antenna performance evaluation:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>Peak Gain (dBi):</strong> Maximum gain in the direction of maximum radiation</li>
              <li><strong>Directivity (dBi):</strong> Theoretical maximum gain (no losses)</li>
              <li><strong>Radiation Efficiency:</strong> Ratio of gain to directivity (accounts for losses)</li>
              <li><strong>Average Gain:</strong> Gain averaged over all directions</li>
              <li><strong>Gain Pattern:</strong> Gain as a function of angle in spherical coordinates</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Gain calculations account for substrate losses, conductor losses, and radiation efficiency. 
              Directivity is calculated from the radiation pattern, providing insight into antenna directivity 
              independent of losses.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Bandwidth Metrics</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              Detailed bandwidth analysis for impedance and radiation performance:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>Impedance Bandwidth:</strong> Frequency range where VSWR &lt; 2:1 (or -10 dB return loss)</li>
              <li><strong>Gain Bandwidth:</strong> Frequency range where gain remains within 3 dB of peak</li>
              <li><strong>Fractional Bandwidth:</strong> Bandwidth as percentage of center frequency</li>
              <li><strong>Bandwidth Efficiency:</strong> Ratio of achieved to target bandwidth</li>
              <li><strong>Multi-Band Analysis:</strong> Identification of multiple resonance bands</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Bandwidth metrics help evaluate antenna performance across the operating frequency range, 
              ensuring designs meet bandwidth requirements for their intended applications.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>Efficiency Analysis</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              Comprehensive efficiency metrics to understand power handling and losses:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>Radiation Efficiency:</strong> Percentage of input power radiated (vs. lost)</li>
              <li><strong>Total Efficiency:</strong> Includes mismatch losses (gain/input power)</li>
              <li><strong>Conductor Loss:</strong> Losses due to finite conductivity</li>
              <li><strong>Dielectric Loss:</strong> Losses in substrate materials</li>
              <li><strong>Surface Wave Loss:</strong> Power lost to surface waves in substrate</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Efficiency analysis helps identify loss mechanisms and optimize designs for maximum power 
              transfer. High efficiency is critical for battery-powered and low-power applications.
            </p>
          </div>

          <div className="border-l-4 pl-6" style={{ borderColor: '#607b7d' }}>
            <h2 className="text-2xl font-semibold mb-3" style={{ color: '#607b7d' }}>VSWR and Return Loss</h2>
            <p className="text-neutral-700 mb-3 leading-relaxed">
              Impedance matching quality metrics for optimal power transfer:
            </p>
            <ul className="list-disc list-inside space-y-2 text-neutral-600 mb-3">
              <li><strong>VSWR (Voltage Standing Wave Ratio):</strong> Measure of impedance mismatch (1:1 = perfect match)</li>
              <li><strong>Return Loss (dB):</strong> Power reflected from antenna port (higher is better)</li>
              <li><strong>Reflection Coefficient:</strong> Complex reflection coefficient magnitude and phase</li>
              <li><strong>Matching Quality:</strong> Assessment of matching network effectiveness</li>
            </ul>
            <p className="text-neutral-700 leading-relaxed">
              Good impedance matching (VSWR &lt; 2:1, Return Loss &gt; 10 dB) ensures maximum power transfer 
              and minimizes reflections that can cause system-level issues.
            </p>
          </div>
        </div>

        <div className="mt-10 pt-8 border-t border-neutral-200">
          <h3 className="text-xl font-semibold mb-4" style={{ color: '#607b7d' }}>Accessing Performance Metrics</h3>
          <p className="text-neutral-600 mb-4">
            Performance metrics are automatically calculated for all optimized designs and simulation results. 
            Navigate to any project and select the "Performance" tab to view comprehensive metrics and visualizations.
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

