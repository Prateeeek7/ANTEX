import apiClient from './client'

export type DesignType = 'patch' | 'slot' | 'fractal' | 'custom'
export type Algorithm = 'ga' | 'pso' | 'hybrid'

export interface OptimizationConfig {
  project_id: number
  design_type: DesignType
  algorithm: Algorithm
  population_size?: number
  generations?: number
  constraints?: Record<string, any>
}

export interface OptimizationHistory {
  generation: number
  best_fitness: number
  avg_fitness: number
}

export interface OptimizationResult {
  run_id: number
  best_candidate: {
    params: Record<string, number>
    fitness: number
    freq_error_ghz?: number
    bandwidth_error_mhz?: number
    gain_estimate_dBi?: number
    return_loss_dB?: number
  }
  history: OptimizationHistory[]
  metrics: Record<string, any>
}

export interface OptimizationRun {
  id: number
  project_id: number
  algorithm: Algorithm
  population_size: number
  generations: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  best_fitness?: number
  log?: {
    history?: OptimizationHistory[]
  }
  created_at: string
  updated_at?: string
}

export interface DesignCandidate {
  id: number
  optimization_run_id?: number
  geometry_params: Record<string, any>
  fitness: number
  metrics: Record<string, any>
  is_best: boolean
  created_at: string
}

export const optimizationApi = {
  start: async (config: OptimizationConfig): Promise<OptimizationRun> => {
    const response = await apiClient.post('/optimize/start', config)
    return response.data
  },

  getRun: async (runId: number): Promise<OptimizationRun> => {
    const response = await apiClient.get(`/optimize/run/${runId}`)
    return response.data
  },

  getCandidates: async (runId: number): Promise<DesignCandidate[]> => {
    const response = await apiClient.get(`/optimize/run/${runId}/candidates`)
    return response.data
  },
}

export const simulationApi = {
  upload: async (projectId: number, file: File, tool: 'hfss' | 'cst' = 'hfss') => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post(`/sim/upload/${projectId}?simulation_tool=${tool}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getCandidates: async (projectId: number): Promise<DesignCandidate[]> => {
    const response = await apiClient.get(`/sim/candidates/${projectId}`)
    return response.data
  },
}


