import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import { performanceApi, PerformanceMetrics, RadiationPatternData } from '../api/performance'
import RadiationPattern3D from '../components/RadiationPattern3D'
import toast from 'react-hot-toast'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'
import BackButton from '../components/BackButton'

export default function PerformanceDashboardPage() {
  const { id } = useParams<{ id: string }>()
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [radiationPattern, setRadiationPattern] = useState<RadiationPatternData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [project, setProject] = useState<any>(null)

  useEffect(() => {
    if (id) {
      loadProject()
      loadMetrics()
      loadRadiationPattern()
    }
  }, [id])

  const loadProject = async () => {
    try {
      const data = await projectsApi.get(parseInt(id!))
      setProject(data)
    } catch (error: any) {
      console.error('Failed to load project:', error)
    }
  }

  const loadMetrics = async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const data = await performanceApi.getMetrics(parseInt(id))
      setMetrics(data)
    } catch (error: any) {
      console.error('Failed to load metrics:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load performance metrics'
      setError(errorMsg)
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const loadRadiationPattern = async () => {
    if (!id) return
    try {
      const data = await performanceApi.getRadiationPattern(parseInt(id))
      setRadiationPattern(data)
    } catch (error: any) {
      console.error('Failed to load radiation pattern:', error)
      // Don't show error for radiation pattern - it's optional
    }
  }

  const exportPDF = async () => {
    if (!id || !metrics) return
    try {
      const blob = await performanceApi.exportPDF(parseInt(id))
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `antenna_design_report_${id}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('PDF report downloaded!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to export PDF')
    }
  }

  // Show loading state
  if (loading) {
    return (
      <div className="px-4 py-6">
        <div className="mb-4">
          <BackButton to={id ? `/projects/${id}` : '/'} label="Back to Project" />
        </div>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4" style={{ borderColor: '#607b7d' }}></div>
            <div style={{ color: '#6b7a6b' }}>Loading performance metrics...</div>
          </div>
        </div>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="px-4 py-6">
        <div className="mb-4">
          <BackButton to={id ? `/projects/${id}` : '/'} label="Back to Project" />
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-2xl mx-auto">
          <div className="flex items-center mb-4">
            <svg className="w-8 h-8 text-yellow-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900">Performance Metrics Unavailable</h2>
          </div>
          <p className="text-gray-700 mb-4">{error}</p>
          {error.includes('No design candidate') && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800 mb-3">
                To view performance metrics, you need to:
              </p>
              <ol className="list-decimal list-inside text-sm text-blue-800 space-y-2 mb-4">
                <li>Start an optimization run from the project's Overview tab</li>
                <li>Wait for the optimization to complete and generate design candidates</li>
                <li>Return to this page to view performance metrics</li>
              </ol>
              {id && (
                <Link
                  to={`/projects/${id}`}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Go to Project Overview →
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    )
  }

  // Show no data state
  if (!metrics) {
    return (
      <div className="px-4 py-6">
        <div className="mb-4">
          <BackButton to={id ? `/projects/${id}` : '/'} label="Back to Project" />
        </div>
        <div className="card max-w-2xl mx-auto">
          <h2 className="text-xl font-semibold mb-4" style={{ color: '#3a606e' }}>No Performance Data</h2>
          <p className="mb-4" style={{ color: '#6b7a6b' }}>
            Performance metrics require a design candidate. Please start an optimization run first.
          </p>
          {id && (
            <Link
              to={`/projects/${id}`}
              className="btn-primary inline-flex items-center"
            >
              Go to Project Overview →
            </Link>
          )}
        </div>
      </div>
    )
  }

  // Prepare data for charts
  const scoreData = metrics.score_breakdown
    ? Object.entries(metrics.score_breakdown).map(([key, value]) => ({
        metric: key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        score: value
      }))
    : []

  const radarData = scoreData.map(item => ({
    subject: item.metric,
    A: item.score,
    fullMark: 100
  }))

  return (
    <div className="px-4 py-6 space-y-6">
      <div className="mb-4">
        <BackButton to={id ? `/projects/${id}` : '/'} label="Back to Project" />
      </div>
      {/* Header */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold" style={{ color: '#3a606e' }}>Performance Dashboard</h1>
            {project && <p className="mt-1" style={{ color: '#6b7a6b' }}>{project.name}</p>}
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold" style={{ color: '#607b7d' }}>{metrics.overall_score.toFixed(1)}</div>
            <div className="text-sm" style={{ color: '#828e82' }}>Overall Score / 100</div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-1">Frequency Error</div>
          <div className={`text-2xl font-bold ${metrics.frequency_error_percent < 5 ? 'text-green-600' : metrics.frequency_error_percent < 10 ? 'text-yellow-600' : 'text-red-600'}`}>
            {metrics.frequency_error_percent.toFixed(2)}%
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {metrics.resonant_frequency_ghz.toFixed(3)} GHz
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-1">Bandwidth</div>
          <div className={`text-2xl font-bold ${metrics.bandwidth_mhz >= metrics.target_bandwidth_mhz ? 'text-green-600' : 'text-yellow-600'}`}>
            {metrics.bandwidth_mhz.toFixed(1)} MHz
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Target: {metrics.target_bandwidth_mhz.toFixed(1)} MHz
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-1">Gain</div>
          <div className="text-2xl font-bold text-blue-600">
            {metrics.gain_dbi.toFixed(2)} dBi
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Efficiency: {metrics.efficiency_percent.toFixed(1)}%
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-sm text-gray-500 mb-1">VSWR</div>
          <div className={`text-2xl font-bold ${metrics.matched ? 'text-green-600' : 'text-red-600'}`}>
            {metrics.vswr.toFixed(2)}
          </div>
          <div className="text-xs mt-1 inline-flex items-center" style={{ color: '#828e82' }}>
            {metrics.matched ? (
              <>
                <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Matched
              </>
            ) : (
              <>
                <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Needs Matching
              </>
            )}
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      {metrics && scoreData.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Performance Score Breakdown</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scoreData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" angle={-45} textAnchor="end" height={100} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>

            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Score" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Detailed Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Frequency & Bandwidth */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Frequency & Bandwidth</h2>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Resonant Frequency</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.resonant_frequency_ghz.toFixed(3)} GHz</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Target Frequency</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.target_frequency_ghz.toFixed(3)} GHz</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Frequency Error</dt>
                <dd className={`text-sm font-medium ${metrics.frequency_error_percent < 5 ? 'text-green-600' : 'text-red-600'}`}>
                  {metrics.frequency_error_percent.toFixed(2)}%
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Bandwidth</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.bandwidth_mhz.toFixed(1)} MHz</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Target Bandwidth</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.target_bandwidth_mhz.toFixed(1)} MHz</dd>
              </div>
            </dl>
          </div>

          {/* Gain & Efficiency */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Gain & Efficiency</h2>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Gain</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.gain_dbi.toFixed(2)} dBi</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Directivity</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.directivity_dbi.toFixed(2)} dBi</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Efficiency</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.efficiency_percent.toFixed(1)}%</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">E-plane Beamwidth</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.beamwidth_e_plane_deg.toFixed(1)}°</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">H-plane Beamwidth</dt>
                <dd className="text-sm font-medium text-gray-900">{metrics.beamwidth_h_plane_deg.toFixed(1)}°</dd>
              </div>
            </dl>
          </div>
        </div>
      )}

      {/* Radiation Pattern */}
      {radiationPattern && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">3D Radiation Pattern</h2>
          <RadiationPattern3D patternData={radiationPattern} viewMode="3d" />
        </div>
      )}

      {/* Export Options */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Export Report</h2>
        <p className="text-sm text-gray-600 mb-4">
          Generate a comprehensive PDF report with all performance metrics, charts, and analysis.
        </p>
        <button
          onClick={exportPDF}
          disabled={!metrics}
          className="btn-primary inline-flex items-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          Export PDF Report
        </button>
      </div>
    </div>
  )
}

