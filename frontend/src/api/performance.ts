import apiClient from './client'

export interface PerformanceMetrics {
  resonant_frequency_ghz: number
  target_frequency_ghz: number
  frequency_error_ghz: number
  frequency_error_percent: number
  bandwidth_mhz: number
  target_bandwidth_mhz: number
  bandwidth_ratio: number
  fractional_bandwidth_percent: number
  gain_dbi: number
  directivity_dbi: number
  efficiency_percent: number
  radiation_efficiency_percent: number
  impedance_real: number
  impedance_imag: number
  vswr: number
  return_loss_db: number
  matched: boolean
  beamwidth_e_plane_deg: number
  beamwidth_h_plane_deg: number
  front_to_back_ratio_db: number
  overall_score: number
  score_breakdown: Record<string, number>
}

export interface RadiationPatternData {
  theta: number[]
  phi: number[]
  gain_pattern: number[][]
  gain_dbi: number
  directivity_dbi: number
  efficiency: number
  beamwidth_e_plane_deg: number
  beamwidth_h_plane_deg: number
  max_gain_theta_deg: number
  max_gain_phi_deg: number
  frequency_ghz: number
}

export const performanceApi = {
  getMetrics: async (projectId: number, frequencyGhz?: number): Promise<PerformanceMetrics> => {
    const params = frequencyGhz ? { frequency_ghz: frequencyGhz } : {}
    const response = await apiClient.get(`/performance/metrics/${projectId}`, { params })
    return response.data
  },

  getRadiationPattern: async (
    projectId: number,
    frequencyGhz?: number,
    thetaPoints?: number,
    phiPoints?: number
  ): Promise<RadiationPatternData> => {
    const params: Record<string, number> = {}
    if (frequencyGhz) params.frequency_ghz = frequencyGhz
    if (thetaPoints) params.theta_points = thetaPoints
    if (phiPoints) params.phi_points = phiPoints
    
    const response = await apiClient.get(`/performance/radiation-pattern/${projectId}`, { params })
    return response.data
  },

  exportPDF: async (projectId: number): Promise<Blob> => {
    const response = await apiClient.get(`/performance/export-pdf/${projectId}`, {
      responseType: 'blob'
    })
    return response.data
  }
}




