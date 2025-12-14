import apiClient from './client'

export interface MeepStatus {
  enabled: boolean
  available: boolean
  resolution: number
  note?: string
  error?: string
}

export interface SimulationRequest {
  project_id: number
  geometry_params: {
    length_mm: number
    width_mm: number
    substrate_height_mm?: number
    eps_r?: number
  }
  target_frequency_ghz: number
  use_meep?: boolean
}

export interface SimulationResult {
  success: boolean
  simulation_method: 'analytical' | 'Meep_FDTD'
  metrics: {
    resonant_frequency_ghz: number
    return_loss_dB: number
    frequency_error_ghz?: number
    bandwidth_mhz: number
    gain_dbi: number
  }
  s11_data?: Array<[number, number]> // [frequency, S11_complex]
  field_data?: FieldVisualizationData['field_data']
}

export interface STLExportRequest {
  project_id: number
  candidate_id?: number
  geometry_params: {
    length_mm: number
    width_mm: number
    substrate_height_mm?: number
    eps_r?: number
  }
}

export interface STLExportResult {
  success: boolean
  stl_file_base64: string
  filename: string
}

export interface FieldVisualizationData {
  success: boolean
  field_data: {
    E_field?: {
      Ex: number[] | number[][]
      Ey?: number[] | number[][]
      Ez?: number[] | number[][]
      magnitude: number[] | number[][]
      x?: number[]
      y?: number[]
      z?: number[]
    }
    H_field?: {
      Hx: number[] | number[][]
      Hy?: number[] | number[][]
      Hz?: number[] | number[][]
      magnitude: number[] | number[][]
      x?: number[]
      y?: number[]
      z?: number[]
    }
    current?: {
      Jx: number[] | number[][]
      Jy?: number[] | number[][]
      Jz?: number[] | number[][]
      magnitude: number[] | number[][]
      x?: number[]
      y?: number[]
      z?: number[]
    }
    probe?: {
      time?: number[]
      Ex?: number[]
      Ey?: number[]
      Ez?: number[]
    }
  }
  geometry_params: Record<string, any>
  metrics: Record<string, any>
  note?: string
}

export const meepApi = {
  getStatus: async (): Promise<MeepStatus> => {
    const response = await apiClient.get('/meep/status')
    return response.data
  },

  simulate: async (request: SimulationRequest): Promise<SimulationResult> => {
    const response = await apiClient.post('/meep/simulate', request)
    return response.data
  },

  exportSTL: async (request: STLExportRequest): Promise<STLExportResult> => {
    const response = await apiClient.post('/meep/export-stl', request)
    return response.data
  },

  getFieldVisualization: async (projectId: number, candidateId?: number): Promise<FieldVisualizationData> => {
    const params = candidateId ? { candidate_id: candidateId } : {}
    const response = await apiClient.get(`/meep/fields/${projectId}`, { params })
    return response.data
  },
}




