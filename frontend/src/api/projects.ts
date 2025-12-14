import apiClient from './client'

export interface Project {
  id: number
  name: string
  description?: string
  target_frequency_ghz: number
  bandwidth_mhz: number
  max_size_mm: number
  substrate: string
  substrate_thickness_mm?: number
  feed_type?: string
  polarization?: string
  target_gain_dbi?: number
  target_impedance_ohm?: number
  conductor_thickness_um?: number
  status: 'draft' | 'running' | 'completed' | 'failed'
  created_at: string
  updated_at?: string
}

export interface CreateProjectRequest {
  name: string
  description?: string
  target_frequency_ghz: number
  bandwidth_mhz: number
  max_size_mm: number
  substrate: string
  substrate_thickness_mm?: number
  feed_type?: string
  polarization?: string
  target_gain_dbi?: number
  target_impedance_ohm?: number
  conductor_thickness_um?: number
}

export interface ProjectListResponse {
  projects: Project[]
  total: number
}

export const projectsApi = {
  create: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await apiClient.post('/projects/', data)
    return response.data
  },

  list: async (): Promise<ProjectListResponse> => {
    const response = await apiClient.get('/projects/')
    return response.data
  },

  get: async (id: number): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}`)
    return response.data
  },

  update: async (id: number, data: Partial<CreateProjectRequest>): Promise<Project> => {
    const response = await apiClient.patch(`/projects/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/projects/${id}`)
  },

      getBestDesign: async (id: number) => {
        const response = await apiClient.get(`/projects/${id}/best-design`)
        return response.data
      },

      getRuns: async (id: number) => {
        const response = await apiClient.get(`/projects/${id}/runs`)
        return response.data
      },

      downloadComprehensiveReport: async (id: number): Promise<Blob> => {
        const response = await apiClient.get(`/projects/${id}/comprehensive-report`, {
          responseType: 'blob',
          headers: {
            'Accept': 'application/pdf'
          }
        })
        
        // Verify we got a PDF blob
        if (response.data instanceof Blob) {
          // Verify it's actually a PDF by checking the first few bytes
          const firstBytes = await response.data.slice(0, 4).arrayBuffer()
          const firstBytesArray = new Uint8Array(firstBytes)
          const pdfHeader = String.fromCharCode(...firstBytesArray)
          
          if (pdfHeader !== '%PDF') {
            throw new Error('Downloaded file is not a valid PDF')
          }
          
          return response.data
        }
        
        // If response.data is not a Blob, convert it
        const blob = new Blob([response.data], { type: 'application/pdf' })
        return blob
      },
    }
