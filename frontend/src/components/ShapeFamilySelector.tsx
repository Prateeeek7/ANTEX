import { useState, useEffect } from 'react'
import { geometryApi, ShapeFamily, ShapeFamilyDetails } from '../api/geometry'
import toast from 'react-hot-toast'

interface ShapeFamilySelectorProps {
  selectedFamily: string
  onFamilyChange: (family: string) => void
  targetFrequencyGhz?: number
  substrate?: string  // Substrate name (e.g., "FR4", "Rogers RT/duroid 5880")
  substrateThicknessMm?: number  // Substrate thickness in mm
  onAutoDesign?: (params: Record<string, number>) => void
  onParametersChange?: (params: Record<string, number>) => void  // Callback when parameters are edited
  initialParameters?: Record<string, number>  // Initial parameter values
}

/**
 * Shape Family Selector with Auto-Design.
 * 
 * Features:
 * - All 8 antenna shape families
 * - Auto-design based on frequency
 * - Family descriptions
 */
export default function ShapeFamilySelector({
  selectedFamily,
  onFamilyChange,
  targetFrequencyGhz,
  substrate,
  substrateThicknessMm,
  onAutoDesign,
  onParametersChange,
  initialParameters
}: ShapeFamilySelectorProps) {
  const [families, setFamilies] = useState<ShapeFamily[]>([])
  const [familyDetails, setFamilyDetails] = useState<ShapeFamilyDetails | null>(null)
  const [loading, setLoading] = useState(false)
  const [autoDesigning, setAutoDesigning] = useState(false)
  const [parameters, setParameters] = useState<Record<string, number>>({})

  useEffect(() => {
    loadFamilies()
  }, [])

  useEffect(() => {
    if (selectedFamily) {
      loadFamilyDetails(selectedFamily)
    }
  }, [selectedFamily, substrate, substrateThicknessMm])

  // Initialize parameters from defaults or provided values
  // CRITICAL: Update eps_r when substrate changes (use default_value from API which is correct for substrate)
  useEffect(() => {
    if (familyDetails) {
      const initial: Record<string, number> = { ...parameters } // Start with current values
      let needsUpdate = false
      
      familyDetails.parameters.forEach(param => {
        if (param.name === 'eps_r' && substrate) {
          // eps_r is determined by substrate - use the default_value from API (which was looked up from substrate)
          if (initial[param.name] !== param.default_value) {
            initial[param.name] = param.default_value
            needsUpdate = true
          }
        } else if (param.name === 'substrate_height_mm' && substrateThicknessMm) {
          // Use project's substrate thickness
          if (initial[param.name] !== substrateThicknessMm) {
            initial[param.name] = substrateThicknessMm
            needsUpdate = true
          }
        } else if (!(param.name in initial)) {
          // Initialize with provided values or defaults
          initial[param.name] = initialParameters?.[param.name] ?? param.default_value
          needsUpdate = true
        }
      })
      
      if (needsUpdate || Object.keys(parameters).length === 0) {
        setParameters(initial)
        onParametersChange?.(initial)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [familyDetails, substrate, substrateThicknessMm])

  const loadFamilies = async () => {
    try {
      const data = await geometryApi.getShapeFamilies()
      setFamilies(data)
    } catch (error: any) {
      toast.error('Failed to load shape families')
    }
  }

  const loadFamilyDetails = async (familyName: string) => {
    try {
      // Pass substrate info to get correct default eps_r
      const details = await geometryApi.getShapeFamilyDetails(
        familyName,
        substrate,
        substrateThicknessMm
      )
      setFamilyDetails(details)
    } catch (error: any) {
      console.error('Failed to load family details:', error)
    }
  }

  const handleAutoDesign = async () => {
    if (!targetFrequencyGhz) {
      toast.error('Target frequency required for auto-design')
      return
    }

    setAutoDesigning(true)
    try {
      const result = await geometryApi.autoDesign({
        shape_family: selectedFamily,
        target_frequency_ghz: targetFrequencyGhz,
        substrate: substrate,  // Pass substrate name so backend can look up eps_r
        substrate_height_mm: substrateThicknessMm || 1.6,
      })
      // Update parameters with auto-designed values
      setParameters(result.parameters)
      onAutoDesign?.(result.parameters)
      onParametersChange?.(result.parameters)
      toast.success('Auto-design completed! Parameters generated from target frequency.')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Auto-design failed')
    } finally {
      setAutoDesigning(false)
    }
  }

  const handleParameterChange = (paramName: string, value: number) => {
    const updated = { ...parameters, [paramName]: value }
    setParameters(updated)
    onParametersChange?.(updated)
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2" style={{ color: '#3a606e' }}>
          Antenna Shape Family
        </label>
        <select
          value={selectedFamily}
          onChange={(e) => onFamilyChange(e.target.value)}
          className="input-field"
        >
          {families.map(family => (
            <option key={family.family} value={family.family}>
              {family.display_name}
            </option>
          ))}
        </select>
        {familyDetails && (
          <p className="mt-2 text-sm" style={{ color: '#6b7a6b' }}>{familyDetails.description}</p>
        )}
      </div>

      {targetFrequencyGhz && familyDetails?.auto_design_enabled && (
        <div className="rounded-lg p-4 border" style={{ backgroundColor: 'rgba(96, 123, 125, 0.08)', borderColor: 'rgba(96, 123, 125, 0.2)' }}>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium" style={{ color: '#3a606e' }}>Auto-Design Available</h4>
              <p className="text-xs mt-1" style={{ color: '#6b7a6b' }}>
                Generate initial parameters automatically from target frequency ({targetFrequencyGhz} GHz)
              </p>
            </div>
            <button
              onClick={handleAutoDesign}
              disabled={autoDesigning}
              className="px-4 py-2 text-white rounded-md disabled:opacity-50 text-sm font-medium transition-all duration-200 hover:shadow-md"
              style={{ 
                background: autoDesigning ? 'linear-gradient(to right, #828e82, #9ba89b)' : 'linear-gradient(to right, #3a606e, #607b7d)',
                cursor: autoDesigning ? 'not-allowed' : 'pointer'
              }}
            >
              {autoDesigning ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Designing...
                </span>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  Auto-Design
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {familyDetails && familyDetails.parameters.length > 0 && (
        <div className="rounded-lg p-4 border" style={{ backgroundColor: 'rgba(130, 142, 130, 0.05)', borderColor: 'rgba(130, 142, 130, 0.15)' }}>
          <h4 className="text-sm font-medium mb-3" style={{ color: '#3a606e' }}>Shape Parameters</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {familyDetails.parameters.map(param => {
              const value = parameters[param.name] ?? param.default_value
              const displayName = param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
              
              return (
                <div key={param.name}>
                  <label 
                    htmlFor={`param-${param.name}`}
                    className="block text-xs font-medium mb-1" 
                    style={{ color: '#3a606e' }}
                  >
                    {displayName}
                    {param.unit && <span className="ml-1" style={{ color: '#828e82', fontWeight: 'normal' }}>({param.unit})</span>}
                  </label>
                  <input
                    id={`param-${param.name}`}
                    type="number"
                    min={param.min_value}
                    max={param.max_value}
                    step={param.name === 'eps_r' ? 0.1 : param.name.includes('mm') ? 0.1 : 0.01}
                    value={value}
                    onChange={(e) => {
                      const newValue = parseFloat(e.target.value) || 0
                      handleParameterChange(param.name, newValue)
                    }}
                    className="w-full px-3 py-1.5 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-opacity-50 transition-all"
                    style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      borderColor: 'rgba(130, 142, 130, 0.3)',
                      color: '#2d3748'
                    }}
                    readOnly={param.name === 'eps_r' && substrate ? true : false} // eps_r is read-only if substrate is selected
                    title={param.name === 'eps_r' && substrate ? `Read-only: Determined by substrate "${substrate}"` : param.description}
                  />
                  {param.description && (
                    <p className="text-xs mt-0.5" style={{ color: '#828e82' }}>
                      {param.description}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
          {substrate && (
            <p className="text-xs mt-2 italic" style={{ color: '#828e82' }}>
              Note: ε_r is automatically set based on selected substrate "{substrate}"
            </p>
          )}
        </div>
      )}
    </div>
  )
}

