import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { projectsApi, Project } from '../api/projects'
import { optimizationApi, OptimizationConfig, DesignType, Algorithm, OptimizationRun, DesignCandidate } from '../api/optimization'
import { simulationApi } from '../api/optimization'
import { meepApi, MeepStatus } from '../api/meep'
import toast from 'react-hot-toast'
import GeometryCanvas from '../components/GeometryCanvas'
import CandidateComparison from '../components/CandidateComparison'
import ShapeFamilySelector from '../components/ShapeFamilySelector'
import GeometryExporter from '../components/GeometryExporter'
import FieldVisualization from '../components/FieldVisualization'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

type Tab = 'overview' | 'runs' | 'candidates' | 'simulation' | 'analysis' | 'performance'

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [loading, setLoading] = useState(true)
  const [optimizing, setOptimizing] = useState(false)
  const [bestDesign, setBestDesign] = useState<any>(null)
  const [runs, setRuns] = useState<OptimizationRun[]>([])
  const [candidates, setCandidates] = useState<DesignCandidate[]>([])
  const [uploading, setUploading] = useState(false)
  const [meepStatus, setMeepStatus] = useState<MeepStatus | null>(null)
  const [simulating, setSimulating] = useState(false)
  const [simResult, setSimResult] = useState<any>(null)
  const [fieldData, setFieldData] = useState<any>(null)
  const [loadingFields, setLoadingFields] = useState(false)

  const [optConfig, setOptConfig] = useState<Partial<OptimizationConfig>>({
    design_type: 'patch',
    algorithm: 'ga',
    population_size: 30,
    generations: 40,
  })
  const [shapeFamily, setShapeFamily] = useState<string>('rectangular_patch')
  const [autoDesignParams, setAutoDesignParams] = useState<Record<string, number> | null>(null)

  useEffect(() => {
    if (id) {
      loadProject()
      loadBestDesign()
      loadMeepStatus()
      if (activeTab === 'runs') loadRuns()
      if (activeTab === 'candidates') loadCandidates()
    }
  }, [id, activeTab])

  // Poll for optimization status updates when there are running optimizations
  useEffect(() => {
    if (!id) return
    
    let previousRuns: OptimizationRun[] = []
    let pollInterval: NodeJS.Timeout | null = null
    
    const pollStatus = async () => {
      try {
        const data = await projectsApi.getRuns(parseInt(id!))
        
        // Check for status changes and show notifications
        if (previousRuns.length > 0) {
          data.forEach((newRun: OptimizationRun) => {
            const oldRun = previousRuns.find(r => r.id === newRun.id)
            if (oldRun && oldRun.status === 'running' && newRun.status === 'completed') {
              toast.success(`Optimization run #${newRun.id} completed!`, { duration: 5000 })
              // Refresh candidates and best design when optimization completes
              loadCandidates()
              loadBestDesign()
            } else if (oldRun && oldRun.status === 'running' && newRun.status === 'failed') {
              toast.error(`Optimization run #${newRun.id} failed.`, { duration: 5000 })
            }
          })
        }
        
        // Update runs state
        setRuns(data)
        previousRuns = data
        
        // Check if there are any running optimizations
        const hasRunningRuns = data.some((run: OptimizationRun) => run.status === 'running')
        
        // Stop polling if no running optimizations
        if (!hasRunningRuns && pollInterval) {
          clearInterval(pollInterval)
          pollInterval = null
        }
      } catch (error: any) {
        // Don't show error toast on every poll failure to avoid spam
        console.error('Failed to poll optimization status:', error)
      }
    }
    
    // Start polling
    pollStatus() // Initial check
    pollInterval = setInterval(pollStatus, 3000)
    
    // Cleanup interval on unmount
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]) // Only re-run when project id changes

  const loadMeepStatus = async () => {
    try {
      const status = await meepApi.getStatus()
      setMeepStatus(status)
    } catch (error) {
      // Meep endpoint not available - set default status
      console.log('Meep status check failed:', error)
      setMeepStatus({
        enabled: false,
        available: false,
        resolution: 20,
        error: 'Failed to connect to Meep service.'
      })
    }
  }

  const loadProject = async () => {
    try {
      const data = await projectsApi.get(parseInt(id!))
      setProject(data)
    } catch (error: any) {
      toast.error('Failed to load project')
      navigate('/')
    } finally {
      setLoading(false)
    }
  }

  const loadBestDesign = async () => {
    try {
      const data = await projectsApi.getBestDesign(parseInt(id!))
      if (data.candidate) {
        setBestDesign(data)
      }
    } catch (error) {
      // No best design yet
    }
  }

  const loadRuns = async () => {
    if (!id) return
    try {
      const data = await projectsApi.getRuns(parseInt(id))
      setRuns(data)
    } catch (error: any) {
      console.error('Failed to load optimization runs:', error)
      // Only show error on manual load, not during polling
      if (activeTab === 'runs') {
        toast.error('Failed to load optimization runs')
      }
    }
  }

  const loadCandidates = async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await simulationApi.getCandidates(parseInt(id))
      setCandidates(data)
      console.log('Loaded candidates:', data.length)
    } catch (error: any) {
      console.error('Failed to load candidates:', error)
      toast.error(error.response?.data?.detail || 'Failed to load design candidates')
      setCandidates([]) // Set empty array on error
    } finally {
      setLoading(false)
    }
  }

  const handleStartOptimization = async () => {
    if (!project) return

    setOptimizing(true)
    try {
      const result = await optimizationApi.start({
        project_id: project.id,
        design_type: optConfig.design_type!,
        algorithm: optConfig.algorithm!,
        population_size: optConfig.population_size!,
        generations: optConfig.generations!,
        constraints: {
          shape_family: shapeFamily,
          ...optConfig.constraints,
        },
      })

          toast.success(`Optimization run ${result.id} started! It will run in the background.`)
          setActiveTab('runs')
          loadRuns()
          // Auto-refresh candidates and best design after a delay
          setTimeout(() => {
            loadBestDesign()
            loadCandidates()
          }, 2000)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to start optimization')
    } finally {
      setOptimizing(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !id) return

    setUploading(true)
    try {
      await simulationApi.upload(parseInt(id), file, 'hfss')
      toast.success('Simulation data uploaded successfully!')
      if (activeTab === 'candidates') loadCandidates()
      e.target.value = '' // Reset input
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to upload simulation data')
    } finally {
      setUploading(false)
    }
  }

  if (loading || !project) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="px-4 py-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <BackButton to="/" label="Back to Dashboard" />
          <button
            onClick={async () => {
              if (!id) return
              try {
                toast.loading('Generating PDF report...', { id: 'pdf-download' })
                const blob = await projectsApi.downloadComprehensiveReport(parseInt(id))
                
                // Verify blob is valid
                if (!blob || blob.size === 0) {
                  throw new Error('Received empty PDF file')
                }
                
                // Verify it's a PDF
                const firstBytes = await blob.slice(0, 4).arrayBuffer()
                const header = String.fromCharCode(...new Uint8Array(firstBytes))
                if (header !== '%PDF') {
                  throw new Error('Downloaded file is not a valid PDF')
                }
                
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `antenna_design_report_${project.name.replace(/\s+/g, '_')}_${id}_${new Date().toISOString().split('T')[0]}.pdf`
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                URL.revokeObjectURL(url)
                
                toast.success('PDF report downloaded successfully!', { id: 'pdf-download' })
              } catch (error: any) {
                console.error('PDF download error:', error)
                const errorMsg = error.response?.data?.detail || error.message || 'Failed to download report'
                toast.error(errorMsg, { id: 'pdf-download' })
              }
            }}
            className="btn-primary inline-flex items-center shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-300"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download Full Report (PDF)
          </button>
        </div>
        <h1 className="text-3xl font-bold" style={{ color: '#3a606e' }}>{project.name}</h1>
        {project.description && <p className="mt-2" style={{ color: '#6b7a6b' }}>{project.description}</p>}
      </div>

      <div className="border-b mb-6" style={{ borderColor: 'rgba(130, 142, 130, 0.2)' }}>
        <nav className="-mb-px flex space-x-8">
          {(['overview', 'runs', 'candidates', 'simulation', 'analysis', 'performance'] as Tab[]).map((tab) => {
            // For analysis and performance, navigate to separate pages
            if (tab === 'analysis' || tab === 'performance') {
              return (
                <Link
                  key={tab}
                  to={tab === 'analysis' ? `/projects/${id}/analysis` : `/projects/${id}/performance`}
                  className={`${
                    activeTab === tab
                      ? 'border-primary text-primary-dark'
                      : 'border-transparent hover:text-primary-dark'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize transition-colors`}
                  style={activeTab !== tab ? { color: '#6b7a6b' } : {}}
                >
                  {tab}
                </Link>
              )
            }
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`${
                  activeTab === tab
                    ? 'border-primary text-primary-dark'
                    : 'border-transparent hover:text-primary-dark'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize transition-colors`}
                style={activeTab !== tab ? { color: '#6b7a6b' } : {}}
              >
                {tab}
              </button>
            )
          })}
        </nav>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-medium mb-4" style={{ color: '#3a606e' }}>Project Specifications</h2>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium" style={{ color: '#828e82' }}>Target Frequency</dt>
                <dd className="mt-1 text-sm font-semibold" style={{ color: '#3a606e' }}>{project.target_frequency_ghz} GHz</dd>
              </div>
              <div>
                <dt className="text-sm font-medium" style={{ color: '#828e82' }}>Bandwidth</dt>
                <dd className="mt-1 text-sm font-semibold" style={{ color: '#3a606e' }}>{project.bandwidth_mhz} MHz</dd>
              </div>
              <div>
                <dt className="text-sm font-medium" style={{ color: '#828e82' }}>Max Size</dt>
                <dd className="mt-1 text-sm font-semibold" style={{ color: '#3a606e' }}>{project.max_size_mm} mm</dd>
              </div>
              <div>
                <dt className="text-sm font-medium" style={{ color: '#828e82' }}>Substrate</dt>
                <dd className="mt-1 text-sm font-semibold" style={{ color: '#3a606e' }}>{project.substrate}</dd>
              </div>
            </dl>
          </div>

          {bestDesign && (
            <div className="card">
              <h2 className="text-lg font-medium mb-4" style={{ color: '#3a606e' }}>Best Design</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Metrics</h3>
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="text-sm text-gray-500">Fitness</dt>
                      <dd className="text-sm font-medium text-gray-900">{bestDesign.candidate.fitness.toFixed(2)}</dd>
                    </div>
                    {bestDesign.candidate.metrics && (
                      <>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Return Loss</dt>
                          <dd className="text-sm font-medium text-gray-900">{bestDesign.candidate.metrics.return_loss_dB?.toFixed(2)} dB</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Gain</dt>
                          <dd className="text-sm font-medium text-gray-900">{bestDesign.candidate.metrics.gain_estimate_dBi?.toFixed(2)} dBi</dd>
                        </div>
                      </>
                    )}
                  </dl>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Geometry</h3>
                  <div className="space-y-2">
                    <GeometryCanvas
                      shapeFamily={bestDesign.candidate.geometry_params?.shape_family || 'rectangular_patch'}
                      params={bestDesign.candidate.geometry_params}
                      width={300}
                      height={200}
                      showAnnotations={true}
                      showSubstrate={true}
                    />
                    <GeometryExporter
                      shapeFamily={bestDesign.candidate.geometry_params?.shape_family || 'rectangular_patch'}
                      parameters={bestDesign.candidate.geometry_params}
                      candidateId={bestDesign.candidate.id}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Start Optimization</h2>
            <div className="space-y-4">
              {/* Shape Family Selector */}
              <ShapeFamilySelector
                selectedFamily={shapeFamily}
                onFamilyChange={setShapeFamily}
                targetFrequencyGhz={project?.target_frequency_ghz}
                substrate={project?.substrate}
                substrateThicknessMm={project?.substrate_thickness_mm}
                initialParameters={autoDesignParams || undefined}
                onAutoDesign={(params) => {
                  setAutoDesignParams(params)
                  toast.success('Auto-design parameters generated!')
                }}
                onParametersChange={(params) => {
                  // Update parameters when user edits them
                  setAutoDesignParams(params)
                }}
              />
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Algorithm
                  </label>
                  <select
                    value={optConfig.algorithm}
                    onChange={(e) => setOptConfig({ ...optConfig, algorithm: e.target.value as Algorithm })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="ga">Genetic Algorithm</option>
                    <option value="pso">Particle Swarm Optimization</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Population Size
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="100"
                    value={optConfig.population_size}
                    onChange={(e) => setOptConfig({ ...optConfig, population_size: parseInt(e.target.value) })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Generations
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="200"
                    value={optConfig.generations}
                    onChange={(e) => setOptConfig({ ...optConfig, generations: parseInt(e.target.value) })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>
              <button
                onClick={handleStartOptimization}
                disabled={optimizing}
                className="btn-primary"
              >
                {optimizing ? 'Starting...' : 'Start Optimization'}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'runs' && (
        <div className="space-y-4">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Optimization Runs</h2>
            {runs.length === 0 ? (
              <p className="text-gray-500">No optimization runs yet. Start one from the Overview tab.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Algorithm</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Best Fitness</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {runs.map((run) => (
                      <tr key={run.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{run.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 uppercase">{run.algorithm}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-semibold rounded-full ${
                              run.status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : run.status === 'running'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {run.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {run.best_fitness?.toFixed(2) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(run.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <Link
                            to={`/runs/${run.id}`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            View Details
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'candidates' && (
        <div className="space-y-4">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Design Candidates</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Industry-grade multi-shape antenna design system with comparison and export capabilities
                </p>
              </div>
              {candidates.length > 0 && (
                <div className="text-right">
                  <div className="text-3xl font-bold text-blue-600">{candidates.length}</div>
                  <div className="text-sm text-gray-500">Candidates</div>
                </div>
              )}
            </div>
            
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <div className="text-gray-500">Loading candidates...</div>
                </div>
              </div>
            ) : candidates.length === 0 ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
                <p className="text-gray-700 mb-2">No design candidates yet.</p>
                <p className="text-sm text-gray-600 mb-4">
                  Start an optimization run from the Overview tab or upload simulation data to generate candidates.
                </p>
                <button
                  onClick={() => setActiveTab('overview')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Go to Overview →
                </button>
              </div>
                ) : (
                  <>
                    <CandidateComparison candidates={candidates} />
                    {candidates.length > 0 && (
                      <div className="mt-6 pt-6 border-t border-neutral-200">
                        <div className="flex gap-3 justify-center">
                          <button
                            onClick={() => setActiveTab('simulation')}
                            className="btn-primary inline-flex items-center"
                          >
                            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                            </svg>
                            Run Simulation →
                          </button>
                          <Link
                            to={`/projects/${id}/analysis`}
                            className="btn-secondary inline-flex items-center"
                          >
                            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            RF Analysis →
                          </Link>
                          <Link
                            to={`/projects/${id}/performance`}
                            className="btn-secondary inline-flex items-center"
                          >
                            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            Performance →
                          </Link>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

      {activeTab === 'analysis' && (
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">RF Analysis & Design Tools</h2>
            <p className="text-sm text-gray-700 mb-4">
              Professional-grade RF analysis tools for industry-level antenna design:
            </p>
            <ul className="list-disc list-inside space-y-2 text-sm text-gray-700 mb-6 ml-2">
              <li><strong>Smith Chart:</strong> Impedance matching visualization and analysis</li>
              <li><strong>Material Library:</strong> Industry-standard substrate materials (Rogers, Taconic, FR4)</li>
              <li><strong>Parameter Sweeps:</strong> Sensitivity analysis and design optimization</li>
              <li><strong>S-Parameter Analysis:</strong> Touchstone file export for compatibility with ADS, HFSS, CST</li>
              <li><strong>Impedance Matching:</strong> Automatic matching network design with component values</li>
            </ul>
            {id && (
              <Link
                to={`/projects/${id}/analysis`}
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-md hover:from-blue-700 hover:to-indigo-700 font-medium shadow-lg transition-all transform hover:scale-105"
              >
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Open RF Analysis Tools →
              </Link>
            )}
          </div>
        </div>
      )}

      {activeTab === 'simulation' && (
        <div className="space-y-4">
          {/* Meep Status - Always show, even if status is null */}
          <div className={`bg-white shadow-lg rounded-lg p-6 border-l-4 ${
            meepStatus?.available 
              ? 'border-green-500' 
              : 'border-yellow-500'
          } ${!meepStatus ? 'animate-pulse' : ''}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">⚡ Meep FDTD Integration</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {!meepStatus
                    ? '⏳ Checking Meep status...'
                    : meepStatus.available
                    ? (
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Real 3D FDTD simulations available (CST/HFSS-grade accuracy)
                      </span>
                    ) : (
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Using analytical models with mock field visualization. Install Meep for real FDTD simulations.
                      </span>
                    )}
                </p>
                {!meepStatus?.available && (
                  <div className="mt-3">
                    <a
                      href="https://meep.readthedocs.io/en/latest/Installation/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium inline-flex items-center"
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      Install Meep →
                    </a>
                    <span className="text-xs text-gray-500 ml-4">or: <code className="bg-gray-100 px-1 rounded">conda install -c conda-forge meep</code></span>
                  </div>
                )}
              </div>
              <div className="text-right">
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  meepStatus?.available
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {meepStatus?.available 
                    ? (
                      <span className="flex items-center text-green-600">
                        <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Available
                      </span>
                    ) : (
                      <span className="flex items-center text-yellow-600">
                        <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        Not Available
                      </span>
                    )}
                </span>
              </div>
            </div>
            
            {/* Show configuration details */}
            {meepStatus && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  <div>
                    <span className="text-gray-500">Enabled:</span>
                    <span className="ml-2 font-medium">{meepStatus.enabled ? 'Yes' : 'No'}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Resolution:</span>
                    <span className="ml-2 font-medium">{meepStatus.resolution}</span>
                  </div>
                  {meepStatus.note && (
                    <div className="col-span-full mt-2 text-yellow-800 bg-yellow-50 p-2 rounded-md">
                      <span className="font-medium">Note:</span> {meepStatus.note}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Run Meep Simulation - Always show, but disable if not available */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
              {meepStatus?.available ? 'Run Meep FDTD Simulation' : 'Run Simulation'}
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              {meepStatus?.available
                ? 'Run a real 3D FDTD simulation on the best design candidate for accurate S11, gain, and bandwidth. This provides CST/HFSS-grade accuracy but takes 30 seconds to 5 minutes per simulation.'
                : 'Run an analytical simulation on the best design candidate. This provides fast approximate results using analytical EM models.'}
            </p>
            
            {!bestDesign && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800 flex items-center">
                  <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  No design candidate available yet. Start an optimization run first to generate designs.
                </p>
              </div>
            )}
            
            {!meepStatus?.available && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-yellow-800 flex items-start">
                  <svg className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Meep is not installed. Install Meep with: <code className="bg-yellow-100 px-1 rounded">conda install -c conda-forge meep</code> or <code className="bg-yellow-100 px-1 rounded">pip install meep</code> to enable real FDTD simulations.
                </p>
              </div>
            )}
            
            <button
              onClick={async () => {
                if (!bestDesign || !id) {
                  toast.error('No design candidate available. Start an optimization first.')
                  return
                }
                setSimulating(true)
                try {
                  const result = await meepApi.simulate({
                    project_id: parseInt(id),
                    geometry_params: bestDesign.candidate.geometry_params,
                    target_frequency_ghz: project!.target_frequency_ghz,
                    use_meep: meepStatus?.available || false
                  })
                  setSimResult(result)
                  const method = result.simulation_method === 'Meep_FDTD' ? 'Meep FDTD' : 'analytical'
                  toast.success(`${method} simulation completed!`)
                } catch (error: any) {
                  toast.error(error.response?.data?.detail || 'Simulation failed.')
                } finally {
                  setSimulating(false)
                }
              }}
              disabled={simulating || !bestDesign}
              className="btn-primary"
            >
              {simulating ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running Simulation...
                </span>
              ) : (
                bestDesign
                  ? meepStatus?.available
                    ? (
                      <span className="flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        Run Meep FDTD Simulation
                      </span>
                    ) : (
                      <span className="flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                        </svg>
                        Run Analytical Simulation
                      </span>
                    )
                  : 'Run Simulation (No design available)'
              )}
            </button>
            {simulating && (
              <p className="mt-3 text-sm text-gray-600 flex items-center">
                <svg className="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                This may take 30 seconds to 5 minutes depending on simulation resolution...
              </p>
            )}

              {/* Simulation Results */}
              {simResult && (
                <div className="mt-6 space-y-4">
                  <div className="border-t border-gray-200 pt-4">
                    <h3 className="text-md font-medium text-gray-900 mb-3">
                      Simulation Results ({simResult.simulation_method || 'analytical'})
                    </h3>
                    {simResult.metrics && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <dt className="text-xs text-gray-500">Resonant Freq</dt>
                          <dd className="text-lg font-semibold text-gray-900">
                            {simResult.metrics.resonant_frequency_ghz?.toFixed(3) || 
                             simResult.metrics.frequency_ghz?.toFixed(3) || 
                             project?.target_frequency_ghz.toFixed(3) || 'N/A'} GHz
                          </dd>
                        </div>
                        <div>
                          <dt className="text-xs text-gray-500">Return Loss</dt>
                          <dd className="text-lg font-semibold text-gray-900">
                            {simResult.metrics.return_loss_dB?.toFixed(2) || 
                             simResult.metrics.s11_db?.toFixed(2) || 'N/A'} dB
                          </dd>
                        </div>
                        <div>
                          <dt className="text-xs text-gray-500">Bandwidth</dt>
                          <dd className="text-lg font-semibold text-gray-900">
                            {simResult.metrics.bandwidth_mhz?.toFixed(1) || 'N/A'} MHz
                          </dd>
                        </div>
                        <div>
                          <dt className="text-xs text-gray-500">Gain</dt>
                          <dd className="text-lg font-semibold text-gray-900">
                            {simResult.metrics.gain_dbi?.toFixed(2) || 
                             simResult.metrics.gain_estimate_dBi?.toFixed(2) || 'N/A'} dBi
                          </dd>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* S11 Plot - Only show if s11_data is available */}
                  {simResult.s11_data && Array.isArray(simResult.s11_data) && simResult.s11_data.length > 0 && (
                    <div className="border-t border-gray-200 pt-4">
                      <h3 className="text-md font-medium text-gray-900 mb-3">S11 (Return Loss) Curve</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={simResult.s11_data.map((d: any) => {
                          // Handle both array [freq, complex] and object formats
                          const freq = Array.isArray(d) ? d[0] : d.frequency;
                          const s11 = Array.isArray(d) ? d[1] : d.s11;
                          return {
                            frequency: (freq / 1e9).toFixed(2),
                            s11_db: typeof s11 === 'number' ? 20 * Math.log10(Math.abs(s11 || 1)) : s11
                          };
                        })}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="frequency" label={{ value: 'Frequency (GHz)', position: 'insideBottom', offset: -5 }} />
                          <YAxis label={{ value: 'S11 (dB)', angle: -90, position: 'insideLeft' }} />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="s11_db" stroke="#3b82f6" strokeWidth={2} name="Return Loss (dB)" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              )}

              {/* EM Field Visualization */}
              <div className="bg-white shadow rounded-lg p-6 mt-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-medium text-gray-900 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    EM Field Visualization
                  </h2>
                  <button
                    onClick={async () => {
                      if (!id) return
                      setLoadingFields(true)
                      try {
                        const data = await meepApi.getFieldVisualization(parseInt(id))
                        setFieldData(data)
                        toast.success('Field visualization loaded!')
                      } catch (error: any) {
                        toast.error(error.response?.data?.detail || 'Failed to load field visualization. Run a Meep simulation first.')
                      } finally {
                        setLoadingFields(false)
                      }
                    }}
                    disabled={loadingFields}
                    className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    {loadingFields ? (
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Loading...
                      </span>
                    ) : (
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        Load Field Visualization
                      </span>
                    )}
                  </button>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Visualize the electromagnetic fields generated by your antenna: electric field (E), magnetic field (H), and current distribution (J).
                  This shows how EM waves propagate and interact with your antenna structure.
                  {!meepStatus?.available && ' (Showing simulated field patterns - install Meep for real FDTD field data)'}
                </p>
                {fieldData?.simulation_method === 'FDTD_3D' && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                    <p className="text-sm text-green-800 flex items-start">
                      <svg className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span><strong>Industry-Grade 3D FDTD Simulation Active:</strong> Real finite-difference time-domain simulation with CST/HFSS-level accuracy. Physics-based field patterns calculated from antenna structure.</span>
                    </p>
                  </div>
                )}
                {fieldData?.simulation_method === 'analytical' && !meepStatus?.available && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <p className="text-sm text-blue-800">
                      <span className="inline-flex items-center mr-2">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </span>
                      <strong>Physics-Based Analytical Data:</strong> Field patterns calculated from antenna theory (TM10 mode). The system automatically uses FDTD when available.
                    </p>
                  </div>
                )}
                <FieldVisualization fieldData={fieldData} loading={loadingFields} />
              </div>
          </div>

          {/* STL Export - Always show */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
              Export Design to STL
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Export the 3D geometry of the best design candidate as an STL file for CAD or 3D printing.
            </p>
            {!bestDesign && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800 flex items-center">
                  <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  No design candidate available yet. Start an optimization run first.
                </p>
              </div>
            )}
            <button
              onClick={async () => {
                if (!bestDesign || !id) {
                  toast.error('No design candidate available for STL export.')
                  return
                }
                try {
                  const result = await meepApi.exportSTL({
                    project_id: parseInt(id),
                    geometry_params: bestDesign.candidate.geometry_params
                  })
                  
                  // Download STL file
                  const blob = new Blob(
                    [Uint8Array.from(atob(result.stl_file_base64), c => c.charCodeAt(0))],
                    { type: 'application/octet-stream' }
                  )
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = result.filename
                  document.body.appendChild(a)
                  a.click()
                  document.body.removeChild(a)
                  URL.revokeObjectURL(url)
                  
                  toast.success('STL file downloaded!')
                } catch (error: any) {
                  toast.error(error.response?.data?.detail || 'Export failed.')
                }
              }}
              disabled={!bestDesign}
              className={`${meepStatus?.available && bestDesign ? 'btn-secondary' : 'btn-secondary opacity-50 cursor-not-allowed'}`}
            >
              {bestDesign ? (
                <span className="flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Export STL File
                </span>
              ) : 'Export STL (No design available)'}
            </button>
          </div>

          {/* File Upload */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Upload External Simulation Data
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload HFSS or CST Simulation Results
                </label>
                <input
                  type="file"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  accept=".csv,.txt,.dat,.s2p"
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100
                    disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <p className="mt-2 text-sm text-gray-500">
                  Supported formats: CSV, TXT, DAT, S2P files from HFSS or CST simulations
                </p>
              </div>
              {uploading && (
                <div className="text-sm text-blue-600">Uploading and processing simulation data...</div>
              )}
            </div>
          </div>

          {/* STL Export */}
          {bestDesign && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Export for Fabrication</h2>
              <p className="text-sm text-gray-600 mb-4">
                Export antenna geometry as STL file for 3D printing or manufacturing.
              </p>
              <button
                onClick={async () => {
                  if (!bestDesign || !id) return
                  try {
                    const result = await meepApi.exportSTL({
                      project_id: parseInt(id),
                      geometry_params: bestDesign.candidate.geometry_params
                    })
                    
                    // Download STL file
                    const blob = new Blob(
                      [Uint8Array.from(atob(result.stl_file_base64), c => c.charCodeAt(0))],
                      { type: 'application/octet-stream' }
                    )
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = result.filename
                    document.body.appendChild(a)
                    a.click()
                    document.body.removeChild(a)
                    URL.revokeObjectURL(url)
                    
                    toast.success('STL file downloaded!')
                  } catch (error: any) {
                    toast.error(error.response?.data?.detail || 'Export failed')
                  }
                }}
                className="btn-secondary"
              >
                Export STL File
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}


