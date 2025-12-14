import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { projectsApi, CreateProjectRequest } from '../api/projects'
import toast from 'react-hot-toast'
import BackButton from '../components/BackButton'

const SUBSTRATES = ['FR4', 'Rogers RO4003', 'Rogers RT/duroid 5880', 'Rogers RT/duroid 6002', 'Custom']
const FEED_TYPES = ['microstrip', 'coaxial', 'inset', 'probe']
const POLARIZATIONS = [
  { value: 'linear_vertical', label: 'Linear Vertical' },
  { value: 'linear_horizontal', label: 'Linear Horizontal' },
  { value: 'circular_rhcp', label: 'Circular RHCP' },
  { value: 'circular_lhcp', label: 'Circular LHCP' }
]

export default function NewProjectPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [formData, setFormData] = useState<CreateProjectRequest>({
    name: '',
    description: '',
    target_frequency_ghz: 2.4,
    bandwidth_mhz: 100,
    max_size_mm: 50,
    substrate: 'FR4',
    substrate_thickness_mm: 1.6,
    feed_type: 'microstrip',
    polarization: 'linear_vertical',
    target_gain_dbi: 5.0,
    target_impedance_ohm: 50.0,
    conductor_thickness_um: 35.0,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const project = await projectsApi.create(formData)
      toast.success('Project created successfully! 🎉')
      navigate(`/projects/${project.id}`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof CreateProjectRequest, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }
  
  const handleNumberChange = (field: keyof CreateProjectRequest, value: string) => {
    // Handle empty string - allow temporarily for better UX
    if (value === '' || value === '-') {
      // Set to 0 for empty, but allow user to clear field
      handleChange(field, value === '' ? 0 : parseFloat(value) || 0)
      return
    }
    
    // Parse number and validate
    const numValue = parseFloat(value)
    if (!isNaN(numValue) && isFinite(numValue)) {
      handleChange(field, numValue)
    }
    // If invalid, don't update (keeps previous valid value)
  }
  
  // Helper to safely get number value for input (handles NaN)
  const getNumberValue = (value: number | undefined): string => {
    if (value === undefined || value === null || isNaN(value)) {
      return ''
    }
    return value.toString()
  }

  return (
    <div className="w-full max-w-none -mx-4 sm:-mx-6 lg:-mx-8">
      <div className="px-4 sm:px-6 lg:px-8 mb-8">
        <BackButton to="/" label="Back to Dashboard" className="mb-4" />
        <h1 className="text-4xl font-bold" style={{ background: 'linear-gradient(to right, #3a606e, #607b7d)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          New Project
        </h1>
        <p className="mt-2" style={{ color: '#6b7a6b' }}>Create a new antenna design project</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-8 mx-auto" style={{ minWidth: '800px', maxWidth: '900px' }}>
        <div className="border-b pb-4" style={{ borderColor: 'rgba(130, 142, 130, 0.2)' }}>
          <h2 className="text-xl font-semibold" style={{ color: '#3a606e' }}>Project Information</h2>
          <p className="mt-1 text-sm" style={{ color: '#828e82' }}>Basic details about your antenna project</p>
        </div>

        <div className="space-y-6">
          <div>
            <label htmlFor="name" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
              Project Name <span style={{ color: '#ef4444' }}>*</span>
              <div className="group relative">
                <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="absolute left-0 bottom-full mb-2 w-64 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                  A descriptive name for your antenna project. This helps you identify and organize multiple projects.
                </div>
              </div>
            </label>
            <input
              type="text"
              id="name"
              required
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className="input-field"
              placeholder="e.g., 2.4 GHz Patch Antenna"
            />
          </div>

          <div>
            <label htmlFor="description" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
              Description
              <div className="group relative">
                <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="absolute left-0 bottom-full mb-2 w-64 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                  Optional detailed description of your project, including application, requirements, or special considerations.
                </div>
              </div>
            </label>
            <textarea
              id="description"
              rows={3}
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              className="input-field"
              placeholder="Optional project description..."
            />
          </div>
        </div>

        <div className="border-t pt-6" style={{ borderColor: 'rgba(130, 142, 130, 0.2)' }}>
          <h2 className="text-xl font-semibold mb-4" style={{ color: '#3a606e' }}>Design Specifications</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="target_frequency_ghz" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                Target Frequency (GHz) <span style={{ color: '#ef4444' }}>*</span>
                <div className="group relative">
                  <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                    The desired resonant frequency for your antenna. This is the center frequency where the antenna will operate most efficiently. Common values: 2.4 GHz (WiFi), 5.8 GHz (WiFi), 28 GHz (5G).
                  </div>
                </div>
              </label>
              <div className="relative">
                <input
                  type="number"
                  id="target_frequency_ghz"
                  required
                  min="0.1"
                  max="100"
                  step="0.1"
                  value={getNumberValue(formData.target_frequency_ghz)}
                  onChange={(e) => handleNumberChange('target_frequency_ghz', e.target.value)}
                  className="input-field"
                />
                <span className="absolute right-4 top-3.5 text-sm" style={{ color: '#828e82' }}>GHz</span>
              </div>
            </div>

            <div>
              <label htmlFor="bandwidth_mhz" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                Target Bandwidth (MHz) <span style={{ color: '#ef4444' }}>*</span>
                <div className="group relative">
                  <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                    The frequency range over which the antenna maintains acceptable performance (typically defined by VSWR &lt; 2:1 or return loss &gt; 10 dB). Wider bandwidth allows operation over a larger frequency range.
                  </div>
                </div>
              </label>
              <div className="relative">
                <input
                  type="number"
                  id="bandwidth_mhz"
                  required
                  min="1"
                  max="10000"
                  step="1"
                  value={getNumberValue(formData.bandwidth_mhz)}
                  onChange={(e) => handleNumberChange('bandwidth_mhz', e.target.value)}
                  className="input-field"
                />
                <span className="absolute right-4 top-3.5 text-sm" style={{ color: '#828e82' }}>MHz</span>
              </div>
            </div>

            <div>
              <label htmlFor="max_size_mm" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                Max Size (mm) <span style={{ color: '#ef4444' }}>*</span>
                <div className="group relative">
                  <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                    Maximum physical dimension constraint for the antenna. The optimizer will ensure all design candidates fit within this size limit. Typical values: 20-100 mm for patch antennas.
                  </div>
                </div>
              </label>
              <div className="relative">
                <input
                  type="number"
                  id="max_size_mm"
                  required
                  min="1"
                  max="500"
                  step="1"
                  value={getNumberValue(formData.max_size_mm)}
                  onChange={(e) => handleNumberChange('max_size_mm', e.target.value)}
                  className="input-field"
                />
                <span className="absolute right-4 top-3.5 text-sm" style={{ color: '#828e82' }}>mm</span>
              </div>
            </div>

            <div>
              <label htmlFor="substrate" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                Substrate <span style={{ color: '#ef4444' }}>*</span>
                <div className="group relative">
                  <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                    The dielectric substrate material on which the antenna will be fabricated. Different substrates have different permittivity (εr) and loss tangent values, affecting antenna performance. FR4 is common for low-cost applications, Rogers materials offer better performance at higher frequencies.
                  </div>
                </div>
              </label>
              <select
                id="substrate"
                required
                value={formData.substrate}
                onChange={(e) => handleChange('substrate', e.target.value)}
                className="input-field"
              >
                {SUBSTRATES.map((sub) => (
                  <option key={sub} value={sub}>
                    {sub}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Advanced Parameters Section */}
        <div className="border-t pt-6" style={{ borderColor: 'rgba(130, 142, 130, 0.2)' }}>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center justify-between w-full text-left mb-4 group"
          >
            <div>
              <h2 className="text-xl font-semibold" style={{ color: '#3a606e' }}>Advanced Parameters</h2>
              <p className="text-sm mt-1" style={{ color: '#828e82' }}>
                Fine-tune substrate, feed, polarization, and performance targets
              </p>
            </div>
            <svg
              className={`w-6 h-6 transition-transform duration-200 ${showAdvanced ? 'transform rotate-180' : ''}`}
              style={{ color: '#607b7d' }}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAdvanced && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 space-y-0">
              <div>
                <label htmlFor="substrate_thickness_mm" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                  Substrate Thickness (mm)
                  <div className="group relative">
                    <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                      Thickness of the dielectric substrate. Affects resonant frequency, bandwidth, and impedance. Typical: 0.8mm (thin), 1.6mm (standard FR4), 3.2mm (thick).
                    </div>
                  </div>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    id="substrate_thickness_mm"
                    min="0.1"
                    max="10"
                    step="0.1"
                    value={getNumberValue(formData.substrate_thickness_mm)}
                    onChange={(e) => handleNumberChange('substrate_thickness_mm', e.target.value)}
                    className="input-field"
                  />
                  <span className="absolute right-4 top-3.5 text-sm" style={{ color: '#828e82' }}>mm</span>
                </div>
              </div>

              <div>
                <label htmlFor="feed_type" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                  Feed Type
                  <div className="group relative">
                    <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                      Antenna feeding method. Microstrip is most common, coaxial offers better impedance control, inset feed reduces mismatch, probe feed is used for thick substrates.
                    </div>
                  </div>
                </label>
                <select
                  id="feed_type"
                  value={formData.feed_type}
                  onChange={(e) => handleChange('feed_type', e.target.value)}
                  className="input-field"
                >
                  {FEED_TYPES.map((ft) => (
                    <option key={ft} value={ft}>
                      {ft.charAt(0).toUpperCase() + ft.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="polarization" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                  Polarization
                  <div className="group relative">
                    <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                      Antenna polarization type. Linear is simpler, circular (RHCP/LHCP) provides better performance for satellite/mobile applications and reduces orientation sensitivity.
                    </div>
                  </div>
                </label>
                <select
                  id="polarization"
                  value={formData.polarization}
                  onChange={(e) => handleChange('polarization', e.target.value)}
                  className="input-field"
                >
                  {POLARIZATIONS.map((pol) => (
                    <option key={pol.value} value={pol.value}>
                      {pol.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="target_gain_dbi" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                  Target Gain (dBi)
                  <div className="group relative">
                    <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                      Desired antenna gain in dBi (decibels relative to isotropic). Higher gain = more directional. Typical patch antennas: 5-8 dBi.
                    </div>
                  </div>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    id="target_gain_dbi"
                    min="0"
                    max="20"
                    step="0.1"
                    value={getNumberValue(formData.target_gain_dbi)}
                    onChange={(e) => handleNumberChange('target_gain_dbi', e.target.value)}
                    className="input-field"
                  />
                  <span className="absolute right-4 top-3.5 text-sm" style={{ color: '#828e82' }}>dBi</span>
                </div>
              </div>

              <div>
                <label htmlFor="target_impedance_ohm" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                  Target Impedance (Ω)
                  <div className="group relative">
                    <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                      Desired input impedance for matching. Standard is 50Ω for most RF systems. Used to optimize VSWR and return loss.
                    </div>
                  </div>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    id="target_impedance_ohm"
                    min="10"
                    max="200"
                    step="1"
                    value={getNumberValue(formData.target_impedance_ohm)}
                    onChange={(e) => handleNumberChange('target_impedance_ohm', e.target.value)}
                    className="input-field"
                  />
                  <span className="absolute right-4 top-3.5 text-sm" style={{ color: '#828e82' }}>Ω</span>
                </div>
              </div>

              <div>
                <label htmlFor="conductor_thickness_um" className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
                  Conductor Thickness (μm)
                  <div className="group relative">
                    <svg className="w-4 h-4 cursor-help" style={{ color: '#607b7d' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="absolute left-0 bottom-full mb-2 w-72 p-2 bg-neutral-800 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                      Thickness of the metal conductor (copper) layer. Thicker conductors reduce losses but increase cost. 1 oz = 35μm, 2 oz = 70μm.
                    </div>
                  </div>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    id="conductor_thickness_um"
                    min="5"
                    max="200"
                    step="1"
                    value={getNumberValue(formData.conductor_thickness_um)}
                    onChange={(e) => handleNumberChange('conductor_thickness_um', e.target.value)}
                    className="input-field"
                  />
                  <span className="absolute right-4 top-3.5 text-sm" style={{ color: '#828e82' }}>μm</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-4 pt-6 border-t" style={{ borderColor: 'rgba(130, 142, 130, 0.2)' }}>
          <Link
            to="/"
            className="btn-secondary"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating...
              </span>
            ) : (
              'Create Project'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
