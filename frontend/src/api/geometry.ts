import apiClient from './client'

export interface ShapeFamily {
  family: string
  display_name: string
  description: string
  parameter_count: number
  auto_design_enabled: boolean
}

export interface ParameterDefinition {
  name: string
  min_value: number
  max_value: number
  default_value: number
  unit: string
  description: string
}

export interface ShapeFamilyDetails {
  family: string
  display_name: string
  description: string
  parameters: ParameterDefinition[]
  auto_design_enabled: boolean
}

export interface GeometryRenderRequest {
  shape_family: string
  parameters: Record<string, number>
  include_annotations?: boolean
  include_substrate?: boolean
}

export interface GeometryData {
  substrate?: {
    x: number
    y: number
    width: number
    height: number
  }
  patch: any
  slots: any[]
  feed: any
  feed_line?: any
  annotations: Array<{
    type: string
    label: string
    x: number
    y: number
    orientation: string
  }>
  bounds: {
    x_min: number
    y_min: number
    x_max: number
    y_max: number
  }
}

export interface AutoDesignRequest {
  shape_family: string
  target_frequency_ghz: number
  substrate?: string  // Substrate name (e.g., "FR4", "Rogers RT/duroid 5880")
  substrate_eps_r?: number  // Optional, will be looked up from substrate name if not provided
  substrate_height_mm?: number
}

export const geometryApi = {
  getShapeFamilies: async (): Promise<ShapeFamily[]> => {
    const response = await apiClient.get('/geometry/shape-families')
    return response.data.shape_families
  },

  getShapeFamilyDetails: async (
    familyName: string,
    substrate?: string,
    substrateThicknessMm?: number
  ): Promise<ShapeFamilyDetails> => {
    const params: any = {}
    if (substrate) params.substrate = substrate
    if (substrateThicknessMm) params.substrate_thickness_mm = substrateThicknessMm
    const response = await apiClient.get(`/geometry/shape-families/${familyName}`, { params })
    return response.data
  },

  autoDesign: async (request: AutoDesignRequest): Promise<{ shape_family: string; parameters: Record<string, number> }> => {
    const response = await apiClient.post('/geometry/auto-design', request)
    return response.data
  },

  renderGeometry: async (
    request: GeometryRenderRequest,
    format: 'json' | 'svg' = 'json'
  ): Promise<{ format: string; geometry: GeometryData; content?: string }> => {
    const response = await apiClient.post(`/geometry/render?format=${format}`, request)
    return response.data
  },

  validateParameters: async (
    shapeFamily: string,
    parameters: Record<string, number>
  ): Promise<{ valid: boolean; errors: string[] }> => {
    const response = await apiClient.post('/geometry/validate', parameters, {
      params: { shape_family: shapeFamily }
    })
    return response.data
  }
}



