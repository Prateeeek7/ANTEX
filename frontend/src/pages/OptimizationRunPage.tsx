import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { optimizationApi, OptimizationRun, DesignCandidate } from '../api/optimization'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import GeometryCanvas from '../components/GeometryCanvas'

export default function OptimizationRunPage() {
  const { runId } = useParams<{ runId: string }>()
  const [run, setRun] = useState<OptimizationRun | null>(null)
  const [candidates, setCandidates] = useState<DesignCandidate[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!runId) return

    const loadRun = async () => {
      try {
        const data = await optimizationApi.getRun(parseInt(runId))
        setRun(data)
      } catch (error: any) {
        console.error('Failed to load optimization run:', error)
        toast.error('Failed to load optimization run')
        setLoading(false)
      } finally {
        setLoading(false)
      }
    }

    const loadCandidates = async () => {
      try {
        const data = await optimizationApi.getCandidates(parseInt(runId))
        setCandidates(data)
      } catch (error) {
        // No candidates yet - this is ok
        console.warn('No candidates found for run:', runId)
      }
    }

    setLoading(true)
    loadRun()
    loadCandidates()
  }, [runId])

  if (loading || !run) {
    return <div className="text-center py-12">Loading...</div>
  }

  const history = run.log?.history || []
  const bestCandidate = candidates.find(c => c.is_best) || candidates[0]

  return (
    <div className="px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Optimization Run #{run.id}
      </h1>

      <div className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Run Details</h2>
          <dl className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Algorithm</dt>
              <dd className="mt-1 text-sm text-gray-900 uppercase">{run.algorithm}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1">
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
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Best Fitness</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {run.best_fitness?.toFixed(2) || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Population Size</dt>
              <dd className="mt-1 text-sm text-gray-900">{run.population_size}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Generations</dt>
              <dd className="mt-1 text-sm text-gray-900">{run.generations}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(run.created_at).toLocaleString()}
              </dd>
            </div>
          </dl>
        </div>

        {history.length > 0 && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Convergence History</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="generation" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="best_fitness" stroke="#2563eb" name="Best Fitness" />
                <Line type="monotone" dataKey="avg_fitness" stroke="#10b981" name="Average Fitness" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {bestCandidate && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Best Candidate</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Metrics</h3>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Fitness</dt>
                    <dd className="text-sm font-medium text-gray-900">{bestCandidate.fitness.toFixed(2)}</dd>
                  </div>
                  {bestCandidate.metrics && (
                    <>
                      <div className="flex justify-between">
                        <dt className="text-sm text-gray-500">Return Loss</dt>
                        <dd className="text-sm font-medium text-gray-900">
                          {bestCandidate.metrics.return_loss_dB?.toFixed(2)} dB
                        </dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-sm text-gray-500">Gain</dt>
                        <dd className="text-sm font-medium text-gray-900">
                          {bestCandidate.metrics.gain_estimate_dBi?.toFixed(2)} dBi
                        </dd>
                      </div>
                    </>
                  )}
                </dl>
                <h3 className="text-sm font-medium text-gray-700 mt-4 mb-2">Parameters</h3>
                <dl className="space-y-1 text-sm">
                  {Object.entries(bestCandidate.geometry_params || {}).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <dt className="text-gray-500">{key}</dt>
                      <dd className="text-gray-900">{typeof value === 'number' ? value.toFixed(2) : value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Geometry</h3>
                <GeometryCanvas
                  designType="patch"
                  shapeFamily={(bestCandidate.geometry_params as any)?.shape_family || 'rectangular_patch'}
                  params={bestCandidate.geometry_params}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}





