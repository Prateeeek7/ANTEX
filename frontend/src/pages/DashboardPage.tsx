import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi, Project } from '../api/projects'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const response = await projectsApi.list()
      setProjects(response.projects)
    } catch (error: any) {
      toast.error('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (projectId: number, projectName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
      return
    }

    try {
      await projectsApi.delete(projectId)
      toast.success('Project deleted successfully')
      loadProjects() // Reload the projects list
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete project')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          <p className="mt-4 text-neutral-600 font-medium">Loading projects...</p>
        </div>
      </div>
    )
  }

  const runningProjects = projects.filter(p => p.status === 'running').length
  const completedProjects = projects.filter(p => p.status === 'completed').length

  return (
    <div className="space-y-8">
      {/* Hero Section - Inspired by Ansys */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-dark via-primary to-primary-light p-12 shadow-2xl" style={{ minHeight: '400px' }}>
        <div className="relative z-10 max-w-4xl">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Industry-Grade Antenna Design & Simulation
          </h1>
          <p className="text-xl text-white/95 mb-8 leading-relaxed max-w-3xl">
            Understanding the factors affecting antenna performance when installed on real-world platforms is crucial to a sustainable design process. 
            ANTEX provides physics-based electromagnetic simulation to evaluate "what if" real-life scenarios and optimize antenna designs with AI-powered algorithms.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/projects/new"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold bg-white text-primary-dark hover:bg-primary-dark hover:text-white transition-all duration-300 rounded-lg shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
            >
              <svg className="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create New Project
            </Link>
            <Link
              to="/docs"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold bg-white text-primary-dark hover:bg-primary-dark hover:text-white transition-all duration-300 rounded-lg shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
            >
              <svg className="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              Learn More
            </Link>
          </div>
          
          {/* Key Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-12">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <div className="flex items-center mb-2">
                <svg className="w-6 h-6 text-white mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-white font-semibold">Component Design</h3>
              </div>
              <p className="text-white/80 text-sm">Optimize antenna geometries with AI algorithms</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <div className="flex items-center mb-2">
                <svg className="w-6 h-6 text-white mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-white font-semibold">FDTD Simulation</h3>
              </div>
              <p className="text-white/80 text-sm">Real 3D electromagnetic field simulation</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <div className="flex items-center mb-2">
                <svg className="w-6 h-6 text-white mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-white font-semibold">RF Analysis</h3>
              </div>
              <p className="text-white/80 text-sm">Smith Chart & impedance matching</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <div className="flex items-center mb-2">
                <svg className="w-6 h-6 text-white mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-white font-semibold">Performance Metrics</h3>
              </div>
              <p className="text-white/80 text-sm">Comprehensive design evaluation</p>
            </div>
          </div>
        </div>
        
        {/* Decorative background elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl -mr-48 -mt-48"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full blur-3xl -ml-48 -mb-48"></div>
      </div>

      {/* Stats Cards - Enhanced with vibrant colors */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-gradient-to-br from-primary/15 via-primary/10 to-primary-light/10 border-2 hover:border-primary/40 transition-all duration-300 transform hover:-translate-y-1 shadow-soft hover:shadow-medium" style={{ borderColor: 'rgba(96, 123, 125, 0.3)' }}>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-dark to-primary flex items-center justify-center shadow-md">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <div className="ml-5">
              <p className="text-sm font-semibold text-neutral-600 uppercase tracking-wide">Total Projects</p>
              <p className="text-4xl font-bold text-primary-dark mt-1">{projects.length}</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-accent/15 via-accent/10 to-accent-light/10 border-2 hover:border-accent/40 transition-all duration-300 transform hover:-translate-y-1 shadow-soft hover:shadow-medium" style={{ borderColor: 'rgba(170, 174, 142, 0.3)' }}>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-accent to-accent-light flex items-center justify-center shadow-md">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-5">
              <p className="text-sm font-semibold text-neutral-600 uppercase tracking-wide">Running</p>
              <p className="text-4xl font-bold text-primary-dark mt-1">{runningProjects}</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-secondary/15 via-secondary/10 to-secondary-light/10 border-2 hover:border-secondary/40 transition-all duration-300 transform hover:-translate-y-1 shadow-soft hover:shadow-medium" style={{ borderColor: 'rgba(130, 142, 130, 0.3)' }}>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-secondary to-secondary-light flex items-center justify-center shadow-md">
                <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-5">
              <p className="text-sm font-semibold text-neutral-600 uppercase tracking-wide">Completed</p>
              <p className="text-4xl font-bold text-primary-dark mt-1">{completedProjects}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Projects Table */}
      <div className="card shadow-medium border-2" style={{ borderColor: 'rgba(96, 123, 125, 0.2)' }}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-primary-dark to-primary bg-clip-text text-transparent">Your Projects</h2>
        </div>
        {projects.length === 0 ? (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-primary/20 to-primary-light/20 mb-6 border-2" style={{ borderColor: 'rgba(96, 123, 125, 0.3)' }}>
              <svg className="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-dark mb-2">No projects yet</h3>
            <p className="text-neutral-600 mb-6 font-medium">Get started by creating your first antenna design project</p>
            <Link to="/projects/new" className="btn-primary inline-flex items-center shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-300">
              <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Project
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-neutral-200">
              <thead className="bg-gradient-to-r from-primary-dark/5 to-primary/5">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-primary-dark uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-primary-dark uppercase tracking-wider">
                    Frequency
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-primary-dark uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-primary-dark uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-primary-dark uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-neutral-200">
                {projects.map((project) => (
                  <tr key={project.id} className="hover:bg-gradient-to-r hover:from-primary/5 hover:to-primary-light/5 transition-all duration-200 cursor-pointer border-l-4 border-transparent hover:border-primary">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        to={`/projects/${project.id}`}
                        className="text-sm font-bold text-primary hover:text-primary-dark transition-colors"
                      >
                        {project.name}
                      </Link>
                      {project.description && (
                        <p className="text-xs text-neutral-600 mt-1">{project.description}</p>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-neutral-900">
                        {project.target_frequency_ghz} GHz
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full ${
                          project.status === 'completed'
                            ? 'badge-secondary'
                            : project.status === 'running'
                            ? 'badge-accent'
                            : project.status === 'failed'
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : 'badge-primary'
                        }`}
                      >
                        {project.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600 font-medium">
                      {new Date(project.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(project.id, project.name)
                        }}
                        className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all duration-200 border border-transparent hover:border-red-200"
                        title="Delete project"
                      >
                        <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
