import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { analysisApi, ImpedanceAnalysisResponse } from '../api/analysis'
import { projectsApi } from '../api/projects'
import SmithChart from '../components/SmithChart'
import toast from 'react-hot-toast'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import BackButton from '../components/BackButton'

export default function RFAnalysisPage() {
  const { id } = useParams<{ id: string }>()
  const [impedanceAnalysis, setImpedanceAnalysis] = useState<ImpedanceAnalysisResponse | null>(null)
  const [materials, setMaterials] = useState<Record<string, any>>({})
  const [selectedMaterial, setSelectedMaterial] = useState<string>('RO4003C')
  const [loading, setLoading] = useState(false)
  const [frequency, setFrequency] = useState<number>(2.4)
  const [sweepData, setSweepData] = useState<any>(null)
  const [sweepParam, setSweepParam] = useState<string>('length_mm')
  const [sweepStart, setSweepStart] = useState<number>(20)
  const [sweepEnd, setSweepEnd] = useState<number>(40)
  const [sweepPoints, setSweepPoints] = useState<number>(20)

  useEffect(() => {
    if (id) {
      loadMaterials()
    }
  }, [id])

  useEffect(() => {
    if (id && frequency) {
      analyzeImpedance()
    }
  }, [id, frequency])

  const loadMaterials = async () => {
    try {
      const mats = await analysisApi.getMaterials()
      setMaterials(mats)
    } catch (error: any) {
      toast.error('Failed to load material library')
    }
  }

  const analyzeImpedance = async () => {
    if (!id) return
    setLoading(true)
    try {
      const result = await analysisApi.analyzeImpedance({
        project_id: parseInt(id),
        frequency_ghz: frequency,
        use_geometry: true
      })
      setImpedanceAnalysis(result)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to analyze impedance')
    } finally {
      setLoading(false)
    }
  }

  const runParameterSweep = async () => {
    if (!id) return
    setLoading(true)
    try {
      const result = await analysisApi.parameterSweep({
        project_id: parseInt(id),
        parameter_name: sweepParam,
        start_value: sweepStart,
        end_value: sweepEnd,
        num_points: sweepPoints,
        frequency_ghz: frequency
      })
      setSweepData(result)
      toast.success('Parameter sweep completed')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Parameter sweep failed')
    } finally {
      setLoading(false)
    }
  }

  const exportTouchstone = async () => {
    if (!id) return
    try {
      const result = await analysisApi.exportTouchstone(
        parseInt(id),
        frequency * 0.8, // 80% of center frequency
        frequency * 1.2, // 120% of center frequency
        100
      )
      
      // Create download
      const blob = new Blob([result.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = result.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast.success('Touchstone file exported!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Export failed')
    }
  }

  return (
    <div className="px-4 py-6 space-y-6">
      <div className="mb-4">
        <BackButton to={id ? `/projects/${id}` : '/'} label="Back to Project" />
      </div>
      <div className="card">
        <h1 className="text-2xl font-bold mb-6" style={{ color: '#3a606e' }}>RF Analysis & Design Tools</h1>
        <p className="mb-6" style={{ color: '#6b7a6b' }}>
          Professional-grade RF analysis tools for antenna impedance matching, S-parameter analysis, 
          and material selection. Industry-standard features for professional RF design workflows.
        </p>
      </div>

      {/* Impedance Analysis Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Impedance Analysis & Smith Chart</h2>
          <div className="flex gap-4 items-center">
            <label className="text-sm font-medium text-gray-700">
              Frequency (GHz):
              <input
                type="number"
                value={frequency}
                onChange={(e) => setFrequency(parseFloat(e.target.value))}
                step="0.1"
                min="0.1"
                max="100"
                className="ml-2 px-3 py-1 border border-gray-300 rounded-md w-24"
              />
            </label>
            <button
              onClick={analyzeImpedance}
              disabled={loading || !id}
              className="btn-primary inline-flex items-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Analyze Impedance
                </>
              )}
            </button>
          </div>
        </div>

        {impedanceAnalysis && (
          <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-8">
            {/* Smith Chart */}
            <div className="rounded-lg p-8 border bg-white overflow-visible" style={{ borderColor: 'rgba(130, 142, 130, 0.2)', minWidth: '700px', width: '100%' }}>
              <h3 className="text-lg font-medium mb-6" style={{ color: '#3a606e' }}>Smith Chart</h3>
              <div className="w-full flex justify-center items-center overflow-visible" style={{ width: '100%', minHeight: '650px', minWidth: '650px' }}>
                <div className="overflow-visible" style={{ width: '600px', height: '600px' }}>
                  <SmithChart
                    s11={{
                      real: impedanceAnalysis.s11_real,
                      imag: impedanceAnalysis.s11_imag
                    }}
                    width={600}
                    height={600}
                  />
                </div>
              </div>
            </div>

            {/* Impedance Metrics */}
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Impedance Metrics</h3>
                <dl className="space-y-3">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Impedance:</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {impedanceAnalysis.impedance_real.toFixed(2)} + j{impedanceAnalysis.impedance_imag.toFixed(2)} Ω
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">VSWR:</dt>
                    <dd className={`text-sm font-medium ${impedanceAnalysis.vswr < 2.0 ? 'text-green-600' : 'text-red-600'}`}>
                      {impedanceAnalysis.vswr.toFixed(2)}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Return Loss:</dt>
                    <dd className={`text-sm font-medium ${impedanceAnalysis.return_loss_db > 10 ? 'text-green-600' : 'text-red-600'}`}>
                      {impedanceAnalysis.return_loss_db.toFixed(2)} dB
                    </dd>
                  </div>
                  <div className="flex justify-between items-center">
                    <dt className="text-sm text-gray-600">Match Status:</dt>
                    <dd className={`text-sm font-semibold inline-flex items-center ${impedanceAnalysis.matched ? 'text-green-600' : 'text-yellow-600'}`}>
                      {impedanceAnalysis.matched ? (
                        <>
                          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Matched
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          Needs Matching
                        </>
                      )}
                    </dd>
                  </div>
                </dl>
              </div>

              {/* AI Recommendations */}
              {impedanceAnalysis.ai_recommendations && (
                <div className={`rounded-lg p-4 ${
                  impedanceAnalysis.matched 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-yellow-50 border border-yellow-200'
                }`}>
                  <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    AI Matching Recommendations
                  </h3>
                  <div className="space-y-3">
                    {impedanceAnalysis.ai_recommendations.overall && (
                      <div className="bg-white rounded p-3 border border-gray-200">
                        <div className="font-medium text-sm text-gray-900 mb-1">Overall Assessment</div>
                        <div className="text-sm text-gray-700">{impedanceAnalysis.ai_recommendations.overall}</div>
                      </div>
                    )}
                    {impedanceAnalysis.ai_recommendations.resistance && (
                      <div className="bg-white rounded p-3 border border-gray-200">
                        <div className="font-medium text-sm text-gray-900 mb-1">Resistance Analysis</div>
                        <div className="text-sm text-gray-700">{impedanceAnalysis.ai_recommendations.resistance}</div>
                      </div>
                    )}
                    {impedanceAnalysis.ai_recommendations.reactance && (
                      <div className="bg-white rounded p-3 border border-gray-200">
                        <div className="font-medium text-sm text-gray-900 mb-1">Reactance Analysis</div>
                        <div className="text-sm text-gray-700">{impedanceAnalysis.ai_recommendations.reactance}</div>
                      </div>
                    )}
                    {impedanceAnalysis.ai_recommendations.best_practice && (
                      <div className="bg-blue-50 rounded p-3 border border-blue-300">
                        <div className="font-semibold text-sm text-blue-900 mb-1 inline-flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Best Practice
                        </div>
                        <div className="text-sm text-blue-800">{impedanceAnalysis.ai_recommendations.best_practice}</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Matching Networks */}
              {impedanceAnalysis.matching_networks.length > 0 && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Matching Network Solutions</h3>
                  <div className="space-y-3">
                    {impedanceAnalysis.matching_networks.slice(0, 3).map((network, idx) => (
                      <div key={idx} className={`bg-white rounded-lg p-4 border-2 ${
                        idx === 0 ? 'border-blue-500 shadow-md' : 'border-blue-200'
                      }`}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-semibold text-sm text-gray-900 inline-flex items-center">
                            {idx === 0 && (
                              <svg className="w-4 h-4 mr-1 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                              </svg>
                            )}
                            {network.type} Network
                          </div>
                          {network.priority && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                              Priority {network.priority}
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-700 mb-2">{network.description}</div>
                        {network.ai_recommendation && (
                          <div className="text-xs text-gray-600 bg-gray-50 rounded p-2 mt-2 inline-flex items-start">
                            <svg className="w-4 h-4 mr-1 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                            </svg>
                            <span>{network.ai_recommendation}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Material Library */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Material Library</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(materials).slice(0, 12).map(([name, props]) => (
            <div
              key={name}
              className={`border rounded-lg p-4 cursor-pointer transition-all ${
                selectedMaterial === name ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedMaterial(name)}
            >
              <div className="font-medium text-gray-900 mb-2">{props.name}</div>
              <div className="text-sm text-gray-600 space-y-1">
                <div>εᵣ = {props.eps_r}</div>
                <div>tan δ = {props.loss_tan}</div>
                {props.thickness_mm && <div>Thickness: {props.thickness_mm} mm</div>}
                <div className="text-xs mt-2 text-gray-500">{props.application}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Parameter Sweep */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Parameter Sweep Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Parameter</label>
            <select
              value={sweepParam}
              onChange={(e) => setSweepParam(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="length_mm">Length (mm)</option>
              <option value="width_mm">Width (mm)</option>
              <option value="substrate_height_mm">Substrate Height (mm)</option>
              <option value="feed_offset_mm">Feed Offset (mm)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Value</label>
            <input
              type="number"
              value={sweepStart}
              onChange={(e) => setSweepStart(parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Value</label>
            <input
              type="number"
              value={sweepEnd}
              onChange={(e) => setSweepEnd(parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Points</label>
            <input
              type="number"
              value={sweepPoints}
              onChange={(e) => setSweepPoints(parseInt(e.target.value))}
              min="5"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
        <button
          onClick={runParameterSweep}
          disabled={loading}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          Run Sweep
        </button>

        {sweepData && (
          <div className="mt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sweep Results</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={sweepData.results}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="parameter_value" label={{ value: sweepParam, position: 'insideBottom', offset: -5 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="vswr" stroke="#ef4444" name="VSWR" />
                <Line type="monotone" dataKey="return_loss_db" stroke="#3b82f6" name="Return Loss (dB)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Export Options */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Options</h2>
        <div className="flex gap-4">
          <button
            onClick={exportTouchstone}
            className="btn-secondary inline-flex items-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export Touchstone (.s1p)
          </button>
          <div className="text-sm text-gray-600 flex items-center">
            Industry-standard S-parameter format compatible with ADS, HFSS, CST
          </div>
        </div>
      </div>
    </div>
  )
}

