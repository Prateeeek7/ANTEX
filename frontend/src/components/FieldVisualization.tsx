import { useEffect, useRef, useState } from 'react'
import { FieldVisualizationData } from '../api/meep'

interface FieldVisualizationProps {
  fieldData: FieldVisualizationData | null
  loading?: boolean
}

// Professional colormap function (Jet-like for engineering)
function getJetColor(value: number): string {
  // Normalize value to 0-1
  const v = Math.max(0, Math.min(1, value))
  
  let r, g, b
  if (v < 0.125) {
    r = 0
    g = 0
    b = 0.5 + 4 * v // 0.5 to 1
  } else if (v < 0.375) {
    r = 0
    g = 4 * (v - 0.125) // 0 to 1
    b = 1
  } else if (v < 0.625) {
    r = 4 * (v - 0.375) // 0 to 1
    g = 1
    b = 1 - 4 * (v - 0.375) // 1 to 0
  } else if (v < 0.875) {
    r = 1
    g = 1 - 4 * (v - 0.625) // 1 to 0
    b = 0
  } else {
    r = 1 - 4 * (v - 0.875) // 1 to 0.5
    g = 0
    b = 0
  }
  
  return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`
}

// Viridis-like colormap (modern scientific standard)
function getViridisColor(value: number): string {
  const v = Math.max(0, Math.min(1, value))
  // Simplified viridis approximation
  const r = v < 0.5 ? 0 : (v - 0.5) * 2
  const g = v < 0.25 ? v * 4 : (v < 0.75 ? 1 : (1 - v) * 4)
  const b = v < 0.5 ? 0.5 + v * 2 : 1 - (v - 0.5) * 2
  return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`
}

export default function FieldVisualization({ fieldData, loading }: FieldVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [selectedField, setSelectedField] = useState<'E_field' | 'H_field' | 'current'>('E_field')
  const [viewMode, setViewMode] = useState<'magnitude' | 'vector'>('magnitude')
  const [showAllLines, setShowAllLines] = useState<boolean>(true)
  const [selectedLineIndices, setSelectedLineIndices] = useState<Set<number>>(new Set())
  const [colormap, setColormap] = useState<'jet' | 'viridis'>('jet')
  const [showGrid, setShowGrid] = useState<boolean>(true)
  const [showAxes, setShowAxes] = useState<boolean>(true)
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number; value?: number } | null>(null)

  useEffect(() => {
    if (!fieldData?.field_data || !canvasRef.current) return

    try {
      const canvas = canvasRef.current
      // Set fixed canvas dimensions
      if (!canvas.width || !canvas.height) {
        canvas.width = 800
        canvas.height = 600
      }
      
      const ctx = canvas.getContext('2d')
      if (!ctx) return

    // Set high-quality rendering
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'

    const width = canvas.width || 800
    const height = canvas.height || 600
    const padding = 60 // Space for axes and labels
    const plotWidth = width - padding - 40 // Reserve space for colorbar
    const plotHeight = height - padding
    const plotX = padding
    const plotY = 20

    // Clear with white background
    ctx.fillStyle = '#FFFFFF'
    ctx.fillRect(0, 0, width, height)

    const field = fieldData.field_data[selectedField]
    if (!field) {
      ctx.fillStyle = '#333'
      ctx.font = 'bold 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('No field data available', width / 2, height / 2)
      return
    }

    // Validate field data
    if (viewMode === 'magnitude' && (!field.magnitude || !Array.isArray(field.magnitude) || field.magnitude.length === 0)) {
      ctx.fillStyle = '#333'
      ctx.font = 'bold 14px Arial'
      ctx.textAlign = 'center'
      ctx.fillText('No magnitude data available', width / 2, height / 2)
      return
    }
    
    if (viewMode === 'vector' && (!field.Ex || !Array.isArray(field.Ex) || field.Ex.length === 0)) {
      ctx.fillStyle = '#333'
      ctx.font = 'bold 14px Arial'
      ctx.textAlign = 'center'
      ctx.fillText('No vector data available', width / 2, height / 2)
      return
    }

    // Get color function
    const getColor = colormap === 'jet' ? getJetColor : getViridisColor

    if (viewMode === 'magnitude' && field.magnitude) {
      // Draw magnitude as heatmap
      const magnitude = field.magnitude
      const maxMag = Math.max(...magnitude)
      const minMag = Math.min(...magnitude)
      const range = maxMag - minMag || 1

      // Create a 2D grid
      const gridSize = Math.sqrt(magnitude.length)
      if (!isFinite(gridSize) || gridSize <= 0) {
        throw new Error('Invalid grid size')
      }
      
      const cellWidth = plotWidth / gridSize
      const cellHeight = plotHeight / gridSize

      // Draw heatmap
      for (let i = 0; i < magnitude.length; i++) {
        const row = Math.floor(i / gridSize)
        const col = i % gridSize
        if (row >= gridSize || col >= gridSize) continue // Safety check
        
        const value = range > 0 ? (magnitude[i] - minMag) / range : 0
        const x = plotX + col * cellWidth
        const y = plotY + row * cellHeight

        ctx.fillStyle = getColor(Math.max(0, Math.min(1, value)))
        ctx.fillRect(x, y, Math.ceil(cellWidth) + 1, Math.ceil(cellHeight) + 1) // Slight overlap to avoid gaps
      }

      // Draw grid overlay
      if (showGrid) {
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
        ctx.lineWidth = 0.5
        const gridStepX = plotWidth / 10
        const gridStepY = plotHeight / 10
        for (let i = 0; i <= 10; i++) {
          // Vertical lines
          ctx.beginPath()
          ctx.moveTo(plotX + i * gridStepX, plotY)
          ctx.lineTo(plotX + i * gridStepX, plotY + plotHeight)
          ctx.stroke()
          // Horizontal lines
          ctx.beginPath()
          ctx.moveTo(plotX, plotY + i * gridStepY)
          ctx.lineTo(plotX + plotWidth, plotY + i * gridStepY)
          ctx.stroke()
        }
      }

      // Draw coordinate axes
      if (showAxes) {
        ctx.strokeStyle = '#333'
        ctx.lineWidth = 2
        // X-axis
        ctx.beginPath()
        ctx.moveTo(plotX, plotY + plotHeight)
        ctx.lineTo(plotX + plotWidth, plotY + plotHeight)
        ctx.stroke()
        // Y-axis
        ctx.beginPath()
        ctx.moveTo(plotX, plotY)
        ctx.lineTo(plotX, plotY + plotHeight)
        ctx.stroke()

        // Axis labels
        ctx.fillStyle = '#333'
        ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText('X', plotX + plotWidth / 2, height - 10)
        ctx.textAlign = 'left'
        ctx.save()
        ctx.translate(15, plotY + plotHeight / 2)
        ctx.rotate(-Math.PI / 2)
        ctx.fillText('Y', 0, 0)
        ctx.restore()
      }

      // Professional colorbar with gradient
      const barWidth = 25
      const barHeight = plotHeight
      const barX = plotX + plotWidth + 10
      const barY = plotY

      // Draw gradient colorbar
      const gradient = ctx.createLinearGradient(barX, barY, barX, barY + barHeight)
      for (let i = 0; i <= 20; i++) {
        const val = i / 20
        gradient.addColorStop(1 - val, getColor(val))
      }
      ctx.fillStyle = gradient
      ctx.fillRect(barX, barY, barWidth, barHeight)

      // Colorbar border
      ctx.strokeStyle = '#333'
      ctx.lineWidth = 1
      ctx.strokeRect(barX, barY, barWidth, barHeight)

      // Colorbar labels
      ctx.fillStyle = '#333'
      ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace'
      ctx.textAlign = 'left'
      
      // Format values with proper scientific notation
      const formatValue = (val: number | undefined | null) => {
        if (val === null || val === undefined || typeof val !== 'number' || !isFinite(val)) {
          return 'N/A'
        }
        if (Math.abs(val) >= 1000 || (Math.abs(val) < 0.01 && val !== 0)) {
          return val.toExponential(2)
        }
        return val.toFixed(3)
      }

      const maxMagNum = typeof maxMag === 'number' && isFinite(maxMag) ? maxMag : 0
      const minMagNum = typeof minMag === 'number' && isFinite(minMag) ? minMag : 0
      ctx.fillText(formatValue(maxMagNum), barX + barWidth + 5, barY + 12)
      ctx.fillText(formatValue((maxMagNum + minMagNum) / 2), barX + barWidth + 5, barY + barHeight / 2)
      ctx.fillText(formatValue(minMagNum), barX + barWidth + 5, barY + barHeight - 3)

      // Unit label
      ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.fillText('Magnitude', barX + barWidth / 2, barY - 5)

      // Show cursor value if hovering
      if (cursorPos && cursorPos.value !== undefined) {
        const x = cursorPos.x
        const y = cursorPos.y
        if (x >= plotX && x <= plotX + plotWidth && y >= plotY && y <= plotY + plotHeight) {
          const col = Math.floor((x - plotX) / cellWidth)
          const row = Math.floor((y - plotY) / cellHeight)
          const idx = row * gridSize + col
          if (idx >= 0 && idx < magnitude.length) {
            const val = magnitude[idx]
            
            // Draw crosshair
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
            ctx.lineWidth = 1
            ctx.setLineDash([5, 5])
            ctx.beginPath()
            ctx.moveTo(x, plotY)
            ctx.lineTo(x, plotY + plotHeight)
            ctx.moveTo(plotX, y)
            ctx.lineTo(plotX + plotWidth, y)
            ctx.stroke()
            ctx.setLineDash([])

            // Tooltip
            const tooltipText = `${formatValue(typeof val === 'number' ? val : undefined)}`
            const tooltipPadding = 8
            const tooltipWidth = ctx.measureText(tooltipText).width + tooltipPadding * 2
            const tooltipX = Math.min(x + 15, width - tooltipWidth - 10)
            const tooltipY = Math.max(y - 30, 10)

            ctx.fillStyle = 'rgba(0, 0, 0, 0.85)'
            ctx.fillRect(tooltipX, tooltipY - 20, tooltipWidth, 25)
            ctx.fillStyle = '#FFF'
            ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace'
            ctx.textAlign = 'left'
            ctx.fillText(tooltipText, tooltipX + tooltipPadding, tooltipY - 5)
          }
        }
      }

    } else if (viewMode === 'vector' && field.Ex && field.Ey) {
      // Draw vector field with enhanced arrows
      const Ex = field.Ex
      const Ey = field.Ey || new Array(Ex.length).fill(0)
      const gridSize = Math.sqrt(Ex.length)
      if (!isFinite(gridSize) || gridSize <= 0) {
        throw new Error('Invalid grid size for vector field')
      }
      
      const cellWidth = plotWidth / gridSize
      const cellHeight = plotHeight / gridSize

      // Calculate magnitudes for color coding
      const magnitudes = Ex.map((x, i) => Math.sqrt(x ** 2 + (Ey[i] || 0) ** 2))
      const maxMag = Math.max(...magnitudes)
      const minMag = Math.min(...magnitudes)
      const magRange = maxMag - minMag || 1

      // Vector scale
      const scale = maxMag > 0 ? Math.min(cellWidth, cellHeight) * 0.25 / maxMag : 0

      for (let i = 0; i < Ex.length; i++) {
        const row = Math.floor(i / gridSize)
        const col = i % gridSize
        if (row >= gridSize || col >= gridSize) continue // Safety check
        
        const x = plotX + col * cellWidth + cellWidth / 2
        const y = plotY + row * cellHeight + cellHeight / 2

        const vx = (Ex[i] || 0) * scale
        const vy = (Ey[i] || 0) * scale
        const mag = magnitudes[i]
        const colorVal = magRange > 0 ? (mag - minMag) / magRange : 0

        // Draw arrow with color based on magnitude
        ctx.strokeStyle = getColor(colorVal)
        ctx.fillStyle = getColor(colorVal)
        ctx.lineWidth = 1.5

        // Arrow shaft
        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.lineTo(x + vx, y + vy)
        ctx.stroke()

        // Arrowhead
        const angle = Math.atan2(vy, vx)
        const arrowLength = 6
        const arrowAngle = Math.PI / 6

        ctx.beginPath()
        ctx.moveTo(x + vx, y + vy)
        ctx.lineTo(
          x + vx - arrowLength * Math.cos(angle - arrowAngle),
          y + vy - arrowLength * Math.sin(angle - arrowAngle)
        )
        ctx.lineTo(
          x + vx - arrowLength * Math.cos(angle + arrowAngle),
          y + vy - arrowLength * Math.sin(angle + arrowAngle)
        )
        ctx.closePath()
        ctx.fill()
      }

      // Draw axes and grid for vector view
      if (showAxes) {
        ctx.strokeStyle = '#333'
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(plotX, plotY + plotHeight)
        ctx.lineTo(plotX + plotWidth, plotY + plotHeight)
        ctx.moveTo(plotX, plotY)
        ctx.lineTo(plotX, plotY + plotHeight)
        ctx.stroke()
      }
    }

    // Draw field lines if available
    if (field._field_lines && Array.isArray(field._field_lines)) {
      const fieldLines = field._field_lines
      const x_points = field.x || []
      const y_points = field.y || []

      if (x_points.length > 0 && y_points.length > 0) {
        const x_min = Math.min(...x_points)
        const x_max = Math.max(...x_points)
        const y_min = Math.min(...y_points)
        const y_max = Math.max(...y_points)
        const x_range = x_max - x_min || 1
        const y_range = y_max - y_min || 1

        const scale_x = plotWidth / x_range
        const scale_y = plotHeight / y_range
        const offset_x = plotX - x_min * scale_x
        const offset_y = plotY - y_min * scale_y

        fieldLines.forEach((line, lineIndex) => {
          if (!showAllLines && !selectedLineIndices.has(lineIndex)) {
            return
          }

          if (line && Array.isArray(line) && line.length > 1) {
            ctx.strokeStyle = `hsl(${(lineIndex * 137.5) % 360}, 75%, 45%)`
            ctx.lineWidth = 2.5
            ctx.beginPath()

            line.forEach((point, pointIndex) => {
              if (Array.isArray(point) && point.length >= 2) {
                const canvasX = point[0] * scale_x + offset_x
                const canvasY = point[1] * scale_y + offset_y

                if (pointIndex === 0) {
                  ctx.moveTo(canvasX, canvasY)
                } else {
                  ctx.lineTo(canvasX, canvasY)
                }
              }
            })

            ctx.stroke()
          }
        })
      }
    }

    // Professional title
    ctx.fillStyle = '#1a1a1a'
    ctx.font = 'bold 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    ctx.textAlign = 'left'
    const fieldLabel = selectedField.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    const modeLabel = viewMode.charAt(0).toUpperCase() + viewMode.slice(1)
      ctx.fillText(`${fieldLabel} - ${modeLabel}`, plotX, 15)
    } catch (error) {
      console.error('Error rendering field visualization:', error)
      // Fallback: draw error message
      try {
        const fallbackCanvas = canvasRef.current
        if (fallbackCanvas) {
          const fallbackCtx = fallbackCanvas.getContext('2d')
          if (fallbackCtx) {
            fallbackCtx.fillStyle = '#FF0000'
            fallbackCtx.font = '16px Arial'
            fallbackCtx.fillText('Error rendering visualization', 20, 50)
          }
        }
      } catch (e) {
        // Ignore errors in error handler
        console.error('Error in error handler:', e)
      }
    }
  }, [fieldData, selectedField, viewMode, showAllLines, selectedLineIndices, colormap, showGrid, showAxes, cursorPos])

  // Handle mouse move for cursor position
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !fieldData?.field_data) return
    try {
      const canvas = canvasRef.current
      const rect = canvas.getBoundingClientRect()
      const scaleX = canvas.width / rect.width
      const scaleY = canvas.height / rect.height
      const x = (e.clientX - rect.left) * scaleX
      const y = (e.clientY - rect.top) * scaleY

      const field = fieldData.field_data[selectedField]
      if (field && field.magnitude && viewMode === 'magnitude') {
        const gridSize = Math.sqrt(field.magnitude.length)
        if (isFinite(gridSize) && gridSize > 0) {
          const padding = 60
          const plotWidth = canvas.width - padding - 40
          const plotHeight = canvas.height - padding
          const cellWidth = plotWidth / gridSize
          const cellHeight = plotHeight / gridSize

          if (x >= padding && x <= padding + plotWidth && y >= 20 && y <= 20 + plotHeight) {
            const col = Math.floor((x - padding) / cellWidth)
            const row = Math.floor((y - 20) / cellHeight)
            const idx = row * gridSize + col
            if (idx >= 0 && idx < field.magnitude.length) {
              setCursorPos({ x: e.clientX - rect.left, y: e.clientY - rect.top, value: field.magnitude[idx] })
              canvas.style.cursor = 'crosshair'
              return
            }
          }
        }
      }
      setCursorPos(null)
      canvas.style.cursor = 'default'
    } catch (error) {
      console.error('Error in handleMouseMove:', error)
      setCursorPos(null)
    }
  }

  // Export canvas as PNG
  const handleExport = () => {
    if (!canvasRef.current) return
    const canvas = canvasRef.current
    const url = canvas.toDataURL('image/png')
    const link = document.createElement('a')
    link.download = `field_visualization_${selectedField}_${viewMode}.png`
    link.href = url
    link.click()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-neutral-50 to-neutral-100 rounded-lg border-2" style={{ borderColor: 'rgba(96, 123, 125, 0.2)' }}>
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <div className="text-neutral-600 font-medium">Loading field visualization...</div>
        </div>
      </div>
    )
  }

  if (!fieldData?.field_data) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-neutral-50 to-neutral-100 rounded-lg border-2" style={{ borderColor: 'rgba(96, 123, 125, 0.2)' }}>
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <div className="text-neutral-600 font-medium">No field data available</div>
          <div className="text-sm text-neutral-500 mt-2">Run an FDTD simulation first to generate field data</div>
        </div>
      </div>
    )
  }

  const isMockData = fieldData.field_data._is_mock === true
  const isRealData = fieldData.field_data[selectedField]?._is_real_data === true
  const isAnalytical = fieldData.field_data[selectedField]?._is_analytical === true
  const fieldLines = fieldData.field_data[selectedField]?._field_lines || []
  const hasFieldLines = Array.isArray(fieldLines) && fieldLines.length > 0

  return (
    <div className="space-y-4">
      {/* Status banners */}
      {isMockData && (
        <div className="bg-amber-50 border-l-4 border-amber-400 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-amber-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <p className="text-sm font-medium text-amber-800">
              <strong>Demo Mode:</strong> Showing simulated field patterns. Run FDTD simulation for real data.
            </p>
          </div>
        </div>
      )}
      {isRealData && !isAnalytical && (
        <div className="bg-emerald-50 border-l-4 border-emerald-500 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-emerald-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <p className="text-sm font-medium text-emerald-800">
              <strong>FDTD Simulation Data:</strong> Real finite-difference time-domain simulation results.
            </p>
          </div>
        </div>
      )}
      {isAnalytical && (
        <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
            <p className="text-sm font-medium text-blue-800">
              <strong>Analytical Model:</strong> Physics-based calculation from antenna theory.
            </p>
          </div>
        </div>
      )}

      {/* Enhanced controls */}
      <div className="bg-white rounded-lg border-2 shadow-sm p-4" style={{ borderColor: 'rgba(96, 123, 125, 0.2)' }}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
              Field Type
            </label>
            <select
              value={selectedField}
              onChange={(e) => {
                setSelectedField(e.target.value as any)
                setSelectedLineIndices(new Set())
              }}
              className="w-full px-3 py-2 border-2 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
              style={{ borderColor: 'rgba(96, 123, 125, 0.3)' }}
            >
              {fieldData.field_data.E_field && <option value="E_field">Electric Field (E)</option>}
              {fieldData.field_data.H_field && <option value="H_field">Magnetic Field (H)</option>}
              {fieldData.field_data.current && <option value="current">Current Density (J)</option>}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
              View Mode
            </label>
            <select
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value as any)}
              className="w-full px-3 py-2 border-2 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
              style={{ borderColor: 'rgba(96, 123, 125, 0.3)' }}
            >
              <option value="magnitude">Magnitude (Heatmap)</option>
              <option value="vector">Vector Field</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>
              Colormap
            </label>
            <select
              value={colormap}
              onChange={(e) => setColormap(e.target.value as any)}
              className="w-full px-3 py-2 border-2 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-colors"
              style={{ borderColor: 'rgba(96, 123, 125, 0.3)' }}
            >
              <option value="jet">Jet (Engineering)</option>
              <option value="viridis">Viridis (Scientific)</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleExport}
              className="w-full px-4 py-2 bg-primary text-white font-semibold rounded-lg hover:bg-primary-dark transition-colors shadow-md hover:shadow-lg flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export PNG
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 items-center">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showGrid}
              onChange={(e) => setShowGrid(e.target.checked)}
              className="w-4 h-4 rounded border-2 border-primary text-primary focus:ring-2 focus:ring-primary"
            />
            <span className="text-sm font-medium" style={{ color: '#3a606e' }}>Show Grid</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showAxes}
              onChange={(e) => setShowAxes(e.target.checked)}
              className="w-4 h-4 rounded border-2 border-primary text-primary focus:ring-2 focus:ring-primary"
            />
            <span className="text-sm font-medium" style={{ color: '#3a606e' }}>Show Axes</span>
          </label>

          {hasFieldLines && (
            <>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showAllLines}
                  onChange={(e) => {
                    setShowAllLines(e.target.checked)
                    if (e.target.checked) {
                      setSelectedLineIndices(new Set())
                    }
                  }}
                  className="w-4 h-4 rounded border-2 border-primary text-primary focus:ring-2 focus:ring-primary"
                />
                <span className="text-sm font-medium" style={{ color: '#3a606e' }}>Show All Field Lines</span>
              </label>

              {!showAllLines && (
                <div className="flex flex-wrap gap-2 items-center">
                  <span className="text-sm font-medium" style={{ color: '#3a606e' }}>Select Lines:</span>
                  {fieldLines.map((_, index) => (
                    <label key={index} className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedLineIndices.has(index)}
                        onChange={(e) => {
                          const newSet = new Set(selectedLineIndices)
                          if (e.target.checked) {
                            newSet.add(index)
                          } else {
                            newSet.delete(index)
                          }
                          setSelectedLineIndices(newSet)
                        }}
                        className="w-3 h-3 rounded border border-primary text-primary focus:ring-1 focus:ring-primary"
                      />
                      <span className="w-4 h-4 rounded border" style={{
                        backgroundColor: `hsl(${(index * 137.5) % 360}, 75%, 45%)`
                      }}></span>
                    </label>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Enhanced canvas container */}
      <div className="bg-white rounded-lg border-2 shadow-lg overflow-hidden" style={{ borderColor: 'rgba(96, 123, 125, 0.3)' }}>
        <canvas
          ref={canvasRef}
          width={800}
          height={600}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setCursorPos(null)}
          className="w-full h-auto block"
          style={{ maxWidth: '100%', height: 'auto' }}
        />
      </div>

      {fieldData.field_data.probe && (
        <div className="bg-white rounded-lg border-2 p-4 shadow-sm" style={{ borderColor: 'rgba(96, 123, 125, 0.2)' }}>
          <h4 className="text-sm font-semibold mb-2" style={{ color: '#3a606e' }}>Time-Domain Field at Probe</h4>
          <p className="text-xs mb-2" style={{ color: '#828e82' }}>
            Field magnitude over time at a point above the antenna
          </p>
          {fieldData.field_data.probe.time && (
            <div className="text-xs font-mono" style={{ color: '#607b7d' }}>
              Time range: {fieldData.field_data.probe.time[0]?.toFixed(3)}s -{' '}
              {fieldData.field_data.probe.time[fieldData.field_data.probe.time.length - 1]?.toFixed(3)}s
            </div>
          )}
        </div>
      )}
    </div>
  )
}
