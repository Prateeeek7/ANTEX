import { useEffect, useRef } from 'react'
import Plotly from 'plotly.js-dist-min'

interface RadiationPattern3DProps {
  patternData?: {
    theta: number[]
    phi: number[]
    gain_pattern: number[][]
    gain_dbi: number
    beamwidth_e_plane_deg: number
    beamwidth_h_plane_deg: number
  }
  viewMode?: '3d' | 'polar' | 'cartesian'
  width?: number
  height?: number
}

/**
 * 3D Radiation Pattern Visualization.
 * 
 * Displays:
 * - 3D gain pattern surface
 * - Polar plots (E-plane, H-plane)
 * - Cartesian plots
 * - Beamwidth visualization
 */
export default function RadiationPattern3D({
  patternData,
  viewMode = '3d',
  width = 800,
  height = 600
}: RadiationPattern3DProps) {
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!chartRef.current || !patternData) return

    const { theta, phi, gain_pattern, gain_dbi, beamwidth_e_plane_deg, beamwidth_h_plane_deg } = patternData

    if (viewMode === '3d') {
      // 3D Surface Plot
      const THETA = theta.map((t, i) => Array(phi.length).fill(t))
      const PHI = phi.map((p) => Array(theta.length).fill(p))
      
      // Convert to Cartesian coordinates for 3D plot
      const x: number[] = []
      const y: number[] = []
      const z: number[] = []
      const colors: number[] = []
      
      for (let i = 0; i < theta.length; i++) {
        for (let j = 0; j < phi.length; j++) {
          const t = theta[i]
          const p = phi[j]
          const r = gain_pattern[j][i] // Note: pattern is [phi][theta]
          
          // Convert spherical to Cartesian
          const x_val = r * Math.sin(t) * Math.cos(p)
          const y_val = r * Math.sin(t) * Math.sin(p)
          const z_val = r * Math.cos(t)
          
          x.push(x_val)
          y.push(y_val)
          z.push(z_val)
          colors.push(r)
        }
      }

      const trace: any = {
        x,
        y,
        z,
        mode: 'markers',
        type: 'scatter3d',
        marker: {
          size: 3,
          color: colors,
          colorscale: 'Viridis',
          showscale: true,
          colorbar: {
            title: 'Gain (normalized)'
          }
        },
        name: 'Radiation Pattern'
      }

      const layout: any = {
        title: {
          text: `3D Radiation Pattern (Max Gain: ${gain_dbi.toFixed(2)} dBi)`,
          font: { size: 16 }
        },
        scene: {
          xaxis: { title: 'X' },
          yaxis: { title: 'Y' },
          zaxis: { title: 'Z' },
          aspectmode: 'cube',
          camera: {
            eye: { x: 1.5, y: 1.5, z: 1.5 }
          }
        },
        width,
        height,
        margin: { l: 50, r: 50, t: 50, b: 50 }
      }

      Plotly.newPlot(chartRef.current, [trace], layout, { responsive: true })
    } else if (viewMode === 'polar') {
      // Polar Plot (E-plane and H-plane cuts)
      const e_plane_idx = 0  // φ = 0
      const h_plane_idx = Math.floor(phi.length / 4)  // φ = 90°
      
      const e_plane_pattern = gain_pattern[e_plane_idx]
      const h_plane_pattern = gain_pattern[h_plane_idx]
      
      // Convert to dB
      const e_plane_db = e_plane_pattern.map(g => 20 * Math.log10(Math.max(g, 0.001)) + gain_dbi)
      const h_plane_db = h_plane_pattern.map(g => 20 * Math.log10(Math.max(g, 0.001)) + gain_dbi)
      
      const theta_deg = theta.map(t => t * 180 / Math.PI)
      
      const trace1: any = {
        r: e_plane_db,
        theta: theta_deg,
        mode: 'lines',
        type: 'scatterpolar',
        name: `E-plane (HPBW: ${beamwidth_e_plane_deg.toFixed(1)}°)`,
        line: { color: '#3b82f6', width: 2 }
      }
      
      const trace2: any = {
        r: h_plane_db,
        theta: theta_deg,
        mode: 'lines',
        type: 'scatterpolar',
        name: `H-plane (HPBW: ${beamwidth_h_plane_deg.toFixed(1)}°)`,
        line: { color: '#ef4444', width: 2 }
      }
      
      const layout: any = {
        title: {
          text: 'Radiation Pattern - Polar Plot',
          font: { size: 16 }
        },
        polar: {
          radialaxis: {
            title: 'Gain (dBi)',
            range: [gain_dbi - 30, gain_dbi + 5]
          },
          angularaxis: {
            rotation: 90,
            direction: 'counterclockwise'
          }
        },
        width,
        height,
        showlegend: true
      }
      
      Plotly.newPlot(chartRef.current, [trace1, trace2], layout, { responsive: true })
    } else {
      // Cartesian Plot
      const e_plane_idx = 0
      const e_plane_pattern = gain_pattern[e_plane_idx]
      const theta_deg = theta.map(t => t * 180 / Math.PI)
      const e_plane_db = e_plane_pattern.map(g => 20 * Math.log10(Math.max(g, 0.001)) + gain_dbi)
      
      const trace: any = {
        x: theta_deg,
        y: e_plane_db,
        mode: 'lines',
        type: 'scatter',
        name: 'E-plane',
        line: { color: '#3b82f6', width: 2 }
      }
      
      const layout: any = {
        title: {
          text: 'Radiation Pattern - E-plane Cut',
          font: { size: 16 }
        },
        xaxis: {
          title: 'Theta (degrees)',
          range: [0, 180]
        },
        yaxis: {
          title: 'Gain (dBi)'
        },
        width,
        height,
        showlegend: true
      }
      
      Plotly.newPlot(chartRef.current, [trace], layout, { responsive: true })
    }

    return () => {
      if (chartRef.current) {
        Plotly.purge(chartRef.current)
      }
    }
  }, [patternData, viewMode, width, height])

  if (!patternData) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-gray-500">No radiation pattern data available</div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-4 items-center">
        <label className="text-sm font-medium text-gray-700">
          View Mode:
          <select
            value={viewMode}
            onChange={(e) => {
              // This would need to be controlled by parent
            }}
            className="ml-2 px-3 py-1 border border-gray-300 rounded-md"
            disabled
          >
            <option value="3d">3D Surface</option>
            <option value="polar">Polar Plot</option>
            <option value="cartesian">Cartesian</option>
          </select>
        </label>
        <div className="text-sm text-gray-600">
          Max Gain: <strong>{patternData.gain_dbi.toFixed(2)} dBi</strong>
        </div>
        <div className="text-sm text-gray-600">
          E-plane HPBW: <strong>{patternData.beamwidth_e_plane_deg.toFixed(1)}°</strong>
        </div>
        <div className="text-sm text-gray-600">
          H-plane HPBW: <strong>{patternData.beamwidth_h_plane_deg.toFixed(1)}°</strong>
        </div>
      </div>
      <div ref={chartRef} style={{ width: '100%', height: '100%', minHeight: '500px' }} />
    </div>
  )
}
