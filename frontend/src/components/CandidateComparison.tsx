import { useState } from 'react'
import GeometryCanvas from './GeometryCanvas'
import GeometryExporter from './GeometryExporter'
import { DesignCandidate } from '../api/optimization'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface CandidateComparisonProps {
  candidates: DesignCandidate[]
  selectedIds?: number[]
  onSelectionChange?: (ids: number[]) => void
}

/**
 * Multi-Candidate Comparison Mode.
 * 
 * Features:
 * - Side-by-side geometry comparison
 * - Performance metrics comparison
 * - Frequency response overlay
 * - Visual ranking
 */
export default function CandidateComparison({
  candidates,
  selectedIds = [],
  onSelectionChange
}: CandidateComparisonProps) {
  const [comparisonMode, setComparisonMode] = useState<'grid' | 'metrics' | 'frequency'>('grid')
  const [selected, setSelected] = useState<number[]>(selectedIds)

  const handleToggle = (id: number) => {
    const newSelected = selected.includes(id)
      ? selected.filter(i => i !== id)
      : [...selected, id]
    setSelected(newSelected)
    onSelectionChange?.(newSelected)
  }

  const comparisonCandidates = candidates.filter(c => selected.includes(c.id))
  const sortedCandidates = [...candidates].sort((a, b) => b.fitness - a.fitness)

  // Prepare metrics comparison data
  const metricsData = comparisonCandidates.map(c => ({
    id: c.id,
    fitness: c.fitness,
    return_loss: c.metrics?.return_loss_dB ?? null,
    gain: c.metrics?.gain_estimate_dBi ?? null,
    bandwidth: c.metrics?.estimated_bandwidth_mhz ?? c.metrics?.bandwidth_mhz ?? null,
  }))

  return (
    <div className="space-y-6">
      {/* Mode Selector */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setComparisonMode('grid')}
            className={`px-4 py-2 rounded-md ${
              comparisonMode === 'grid'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Grid View
          </button>
          <button
            onClick={() => setComparisonMode('metrics')}
            className={`px-4 py-2 rounded-md ${
              comparisonMode === 'metrics'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Metrics Comparison
          </button>
          <button
            onClick={() => setComparisonMode('frequency')}
            className={`px-4 py-2 rounded-md ${
              comparisonMode === 'frequency'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Frequency Response
          </button>
        </div>
        <div className="text-sm text-gray-600">
          {selected.length} of {candidates.length} selected
        </div>
      </div>

      {/* Grid View */}
      {comparisonMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedCandidates.map(candidate => (
            <div
              key={candidate.id}
              className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                selected.includes(candidate.id)
                  ? 'border-blue-500 bg-blue-50 shadow-lg'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => handleToggle(candidate.id)}
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">Candidate #{candidate.id}</h3>
                  {candidate.is_best && (
                    <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                      ⭐ Best
                    </span>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">
                    {candidate.fitness.toFixed(2)}
                  </div>
                  <div className="text-xs text-gray-500">Fitness</div>
                </div>
              </div>

              {/* Geometry */}
              <div className="mb-3 space-y-2">
                <GeometryCanvas
                  shapeFamily={candidate.geometry_params?.shape_family || 'rectangular_patch'}
                  params={candidate.geometry_params || {}}
                  width={300}
                  height={200}
                  showAnnotations={false}
                />
                <GeometryExporter
                  shapeFamily={candidate.geometry_params?.shape_family || 'rectangular_patch'}
                  parameters={candidate.geometry_params || {}}
                  candidateId={candidate.id}
                />
              </div>

              {/* Quick Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                {candidate.metrics?.return_loss_dB != null && (
                  <div>
                    <span className="text-gray-500">Return Loss:</span>
                    <span className="ml-1 font-medium text-blue-600">
                      {typeof candidate.metrics.return_loss_dB === 'number' 
                        ? candidate.metrics.return_loss_dB.toFixed(1) 
                        : candidate.metrics.return_loss_dB} dB
                    </span>
                  </div>
                )}
                {candidate.metrics?.gain_estimate_dBi != null && (
                  <div>
                    <span className="text-gray-500">Gain:</span>
                    <span className="ml-1 font-medium text-blue-600">
                      {typeof candidate.metrics.gain_estimate_dBi === 'number' 
                        ? candidate.metrics.gain_estimate_dBi.toFixed(1) 
                        : candidate.metrics.gain_estimate_dBi} dBi
                    </span>
                  </div>
                )}
                {candidate.metrics?.bandwidth_mhz != null && (
                  <div>
                    <span className="text-gray-500">Bandwidth:</span>
                    <span className="ml-1 font-medium text-blue-600">
                      {typeof candidate.metrics.bandwidth_mhz === 'number' 
                        ? candidate.metrics.bandwidth_mhz.toFixed(0) 
                        : candidate.metrics.bandwidth_mhz} MHz
                    </span>
                  </div>
                )}
                {candidate.metrics?.estimated_freq_ghz != null && (
                  <div>
                    <span className="text-gray-500">Freq:</span>
                    <span className="ml-1 font-medium text-blue-600">
                      {typeof candidate.metrics.estimated_freq_ghz === 'number' 
                        ? candidate.metrics.estimated_freq_ghz.toFixed(2) 
                        : candidate.metrics.estimated_freq_ghz} GHz
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Metrics Comparison */}
      {comparisonMode === 'metrics' && comparisonCandidates.length > 0 && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics Comparison</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={metricsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="id" label={{ value: 'Candidate ID', position: 'insideBottom', offset: -5 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="fitness" stroke="#3b82f6" name="Fitness" strokeWidth={2} />
                <Line type="monotone" dataKey="return_loss" stroke="#ef4444" name="Return Loss (dB)" />
                <Line type="monotone" dataKey="gain" stroke="#10b981" name="Gain (dBi)" />
                <Line type="monotone" dataKey="bandwidth" stroke="#f59e0b" name="Bandwidth (MHz)" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Side-by-side geometries */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {comparisonCandidates.map(candidate => (
              <div key={candidate.id} className="bg-white shadow rounded-lg p-4 space-y-2">
                <h4 className="font-medium text-gray-900 mb-2">Candidate #{candidate.id}</h4>
                <GeometryCanvas
                  shapeFamily={candidate.geometry_params?.shape_family || 'rectangular_patch'}
                  params={candidate.geometry_params || {}}
                  width={250}
                  height={180}
                  showAnnotations={true}
                />
                <GeometryExporter
                  shapeFamily={candidate.geometry_params?.shape_family || 'rectangular_patch'}
                  parameters={candidate.geometry_params || {}}
                  candidateId={candidate.id}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Frequency Response */}
      {comparisonMode === 'frequency' && comparisonCandidates.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Frequency Response Comparison</h3>
          <p className="text-sm text-gray-600 mb-4">
            Compare S11 curves and resonant frequencies across selected candidates.
          </p>
          <div className="text-center text-gray-500 py-12">
            Frequency response data will be displayed here when available from simulations.
          </div>
        </div>
      )}

      {comparisonMode !== 'grid' && comparisonCandidates.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            Select candidates from the grid view to compare metrics and frequency response.
          </p>
        </div>
      )}
    </div>
  )
}

