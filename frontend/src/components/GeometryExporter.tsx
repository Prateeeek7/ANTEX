import { useState } from 'react'
import { geometryApi } from '../api/geometry'
import toast from 'react-hot-toast'

interface GeometryExporterProps {
  shapeFamily: string
  parameters: Record<string, number>
  candidateId?: number
}

/**
 * Geometry Export Component.
 * 
 * Exports antenna geometries to:
 * - SVG (for reports and UI)
 * - DXF (for fabrication/CAD)
 * - JSON (for parameter storage)
 */
export default function GeometryExporter({
  shapeFamily,
  parameters,
  candidateId
}: GeometryExporterProps) {
  const [exporting, setExporting] = useState<string | null>(null)

  const handleExport = async (format: 'svg' | 'json' | 'dxf') => {
    if (!shapeFamily || !parameters) {
      toast.error('No geometry data to export')
      return
    }

    setExporting(format)
    try {
      if (format === 'svg') {
        const result = await geometryApi.renderGeometry(
          {
            shape_family: shapeFamily,
            parameters,
            include_annotations: true,
            include_substrate: true,
          },
          'svg'
        )

        // Download SVG
        const blob = new Blob([result.content || ''], { type: 'image/svg+xml' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `antenna_${candidateId || 'design'}.svg`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        toast.success('SVG file downloaded!')
      } else if (format === 'json') {
        const jsonData = {
          shape_family: shapeFamily,
          parameters,
          candidate_id: candidateId,
          exported_at: new Date().toISOString(),
        }
        const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `antenna_${candidateId || 'design'}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        toast.success('JSON file downloaded!')
      } else if (format === 'dxf') {
        // DXF export would require backend endpoint
        toast.info('DXF export coming soon - use SVG for now')
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || `Failed to export ${format.toUpperCase()}`)
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="flex gap-2 flex-wrap">
      <button
        onClick={() => handleExport('svg')}
        disabled={exporting !== null}
        className="inline-flex items-center px-4 py-2 text-white rounded-md disabled:opacity-50 text-sm font-medium transition-all duration-200 hover:shadow-md"
        style={{ 
          background: exporting === 'svg' ? 'linear-gradient(to right, #828e82, #9ba89b)' : 'linear-gradient(to right, #3a606e, #607b7d)',
          cursor: exporting !== null ? 'not-allowed' : 'pointer'
        }}
      >
        {exporting === 'svg' ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Exporting...
          </>
        ) : (
          <>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export SVG
          </>
        )}
      </button>
      <button
        onClick={() => handleExport('json')}
        disabled={exporting !== null}
        className="inline-flex items-center px-4 py-2 text-white rounded-md disabled:opacity-50 text-sm font-medium transition-all duration-200 hover:shadow-md"
        style={{ 
          background: exporting === 'json' ? 'linear-gradient(to right, #828e82, #9ba89b)' : 'linear-gradient(to right, #607b7d, #828e82)',
          cursor: exporting !== null ? 'not-allowed' : 'pointer'
        }}
      >
        {exporting === 'json' ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Exporting...
          </>
        ) : (
          <>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export JSON
          </>
        )}
      </button>
      <button
        onClick={() => handleExport('dxf')}
        disabled={exporting !== null}
        className="inline-flex items-center px-4 py-2 text-white rounded-md disabled:opacity-50 text-sm font-medium transition-all duration-200 hover:shadow-md"
        style={{ 
          background: exporting === 'dxf' ? 'linear-gradient(to right, #828e82, #9ba89b)' : 'linear-gradient(to right, #828e82, #aaae8e)',
          cursor: exporting !== null ? 'not-allowed' : 'pointer'
        }}
      >
        {exporting === 'dxf' ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Exporting...
          </>
        ) : (
          <>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export DXF
          </>
        )}
      </button>
    </div>
  )
}

