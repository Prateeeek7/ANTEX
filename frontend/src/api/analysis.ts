import apiClient from './client'

export interface ImpedanceAnalysisRequest {
  project_id: number
  frequency_ghz: number
  impedance_real?: number
  impedance_imag?: number
  use_geometry?: boolean
}

export interface ImpedanceAnalysisResponse {
  impedance_real: number
  impedance_imag: number
  s11_real: number
  s11_imag: number
  vswr: number
  return_loss_db: number
  matched: boolean
  matching_networks: Array<{
    type: string
    description: string
    ai_recommendation?: string
    priority?: number
    [key: string]: any
  }>
  ai_recommendations?: {
    overall?: string
    resistance?: string
    reactance?: string
    best_practice?: string
    [key: string]: string | undefined
  }
}

export interface MaterialProperties {
  name: string
  eps_r: number
  loss_tan: number
  conductivity_s_m?: number
  thickness_mm?: number
  cost_tier: string
  application: string
}

export interface ParameterSweepRequest {
  project_id: number
  parameter_name: string
  start_value: number
  end_value: number
  num_points: number
  frequency_ghz: number
}

export interface ParameterSweepResult {
  parameter_name: string
  frequency_ghz: number
  sweep_range: [number, number]
  results: Array<{
    parameter_value: number
    impedance_real: number
    impedance_imag: number
    s11_magnitude: number
    s11_phase_deg: number
    vswr: number
    return_loss_db: number
    resonant_frequency_ghz: number
    bandwidth_mhz: number
    gain_dbi: number
  }>
}

export const analysisApi = {
  analyzeImpedance: async (request: ImpedanceAnalysisRequest): Promise<ImpedanceAnalysisResponse> => {
    const response = await apiClient.post('/analysis/impedance', request)
    return response.data
  },

  getMaterials: async (category?: 'substrate' | 'conductor'): Promise<Record<string, MaterialProperties>> => {
    const params = category ? { category } : {}
    const response = await apiClient.get('/analysis/materials', { params })
    return response.data.materials
  },

  getMaterial: async (materialName: string): Promise<MaterialProperties> => {
    const response = await apiClient.get(`/analysis/materials/${materialName}`)
    return response.data
  },

  parameterSweep: async (request: ParameterSweepRequest): Promise<ParameterSweepResult> => {
    const response = await apiClient.post('/analysis/sweep', request)
    return response.data
  },

  exportTouchstone: async (
    projectId: number,
    frequencyStartGhz: number,
    frequencyEndGhz: number,
    numPoints: number = 100
  ): Promise<{ filename: string; content: string; format: string; frequency_range_ghz: [number, number] }> => {
    const response = await apiClient.post(
      `/analysis/export-touchstone/${projectId}`,
      null,
      {
        params: {
          frequency_start_ghz: frequencyStartGhz,
          frequency_end_ghz: frequencyEndGhz,
          num_points: numPoints
        }
      }
    )
    return response.data
  }
}

