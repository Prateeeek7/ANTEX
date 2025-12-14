import { useEffect, useRef } from 'react'

interface SmithChartProps {
  s11?: { real: number; imag: number } | number
  frequencies?: number[]
  s11Data?: Array<{ real: number; imag: number }>
  width?: number
  height?: number
}

/**
 * Industry-standard Smith Chart for RF impedance analysis.
 * 
 * Enhanced with:
 * - Accurate constant resistance and reactance circles
 * - VSWR circles
 * - Professional grid rendering
 * - High-resolution canvas rendering
 */
export default function SmithChart({ 
  s11, 
  frequencies, 
  s11Data, 
  width = 600, 
  height = 600 
}: SmithChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size with high DPI support
    const dpr = window.devicePixelRatio || 1
    canvas.width = width * dpr
    canvas.height = height * dpr
    canvas.style.width = `${width}px`
    canvas.style.height = `${height}px`
    ctx.scale(dpr, dpr)

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) * 0.38  // Adjusted to ensure full chart fits with padding

    // Helper function to convert reflection coefficient to Smith chart coordinates
    const gammaToXY = (gammaReal: number, gammaImag: number) => {
      const x = centerX + gammaReal * radius
      const y = centerY - gammaImag * radius  // Negative because canvas Y increases downward
      return { x, y }
    }

    // Background
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, width, height)
    
    // Draw outer circle (|Γ| = 1)
    ctx.strokeStyle = '#3a606e'  // Primary dark
    ctx.lineWidth = 2.5
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
    ctx.stroke()

    // Draw constant resistance circles (R/Z0 = 0.1, 0.2, 0.5, 1, 2, 5, 10)
    const rValues = [0.1, 0.2, 0.5, 1, 2, 5, 10]
    ctx.strokeStyle = '#607b7d'  // Primary color
    ctx.lineWidth = 1.2
    ctx.setLineDash([4, 3])

    rValues.forEach(r => {
      // Center: (r/(r+1), 0), Radius: 1/(r+1)
      const centerOffset = (r / (r + 1)) * radius
      const circleRadius = (1 / (r + 1)) * radius
      
      ctx.beginPath()
      ctx.arc(centerX - radius + centerOffset, centerY, circleRadius, 0, 2 * Math.PI)
      ctx.stroke()
    })

    // Draw constant reactance arcs (X/Z0 = ±0.2, 0.5, 1, 2, 5)
    ctx.strokeStyle = '#828e82'  // Secondary color
    ctx.lineWidth = 1
    const xValues = [0.2, 0.5, 1, 2, 5]
    
    xValues.forEach(x => {
      for (const sign of [1, -1]) {
        const xNorm = sign * x
        // Center: (1, ±1/x), Radius: 1/|x|
        const centerX_arc = centerX
        const centerY_arc = centerY - sign * (1 / x) * radius
        const arcRadius = (1 / Math.abs(x)) * radius
        
        // Draw arc from 0 to π (upper) or π to 2π (lower)
        const startAngle = sign > 0 ? Math.PI : 0
        const endAngle = sign > 0 ? 2 * Math.PI : Math.PI
        
        ctx.beginPath()
        ctx.arc(centerX_arc, centerY_arc, arcRadius, startAngle, endAngle)
        ctx.stroke()
      }
    })

    ctx.setLineDash([])

    // Draw VSWR circles (VSWR = 1.5, 2, 3, 5)
    ctx.strokeStyle = '#aaae8e'  // Accent color
    ctx.lineWidth = 1
    ctx.setLineDash([3, 3])
    const vswrValues = [1.5, 2, 3, 5]
    
    vswrValues.forEach(vswr => {
      const gamma_mag = (vswr - 1) / (vswr + 1)
      const vswrRadius = gamma_mag * radius
      
      ctx.beginPath()
      ctx.arc(centerX, centerY, vswrRadius, 0, 2 * Math.PI)
      ctx.stroke()
    })
    ctx.setLineDash([])

    // Draw horizontal line (real axis)
    ctx.strokeStyle = '#3a606e'  // Primary dark
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(centerX - radius, centerY)
    ctx.lineTo(centerX + radius, centerY)
    ctx.stroke()

    // Draw S11 data
    if (s11Data && frequencies && s11Data.length > 0) {
      // Frequency sweep - draw as smooth curve
      ctx.strokeStyle = '#607b7d'  // Primary color
      ctx.lineWidth = 3
      ctx.beginPath()

      s11Data.forEach((s, idx) => {
        const point = gammaToXY(s.real, s.imag)
        if (idx === 0) {
          ctx.moveTo(point.x, point.y)
        } else {
          ctx.lineTo(point.x, point.y)
        }
      })
      ctx.stroke()

      // Markers at key frequencies
      ctx.fillStyle = '#607b7d'  // Primary color
      s11Data.forEach((s, idx) => {
        if (idx % Math.max(1, Math.floor(s11Data.length / 8)) === 0) {
          const point = gammaToXY(s.real, s.imag)
          ctx.beginPath()
          ctx.arc(point.x, point.y, 6, 0, 2 * Math.PI)
          ctx.fill()
          
          // White border for visibility
          ctx.strokeStyle = '#ffffff'
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.arc(point.x, point.y, 6, 0, 2 * Math.PI)
          ctx.stroke()
          
          // Frequency label
          if (frequencies && frequencies[idx]) {
            ctx.fillStyle = '#3a606e'  // Primary dark for text
            ctx.font = 'bold 11px Arial'
            ctx.fillText(`${(frequencies[idx] / 1e9).toFixed(2)}GHz`, point.x + 10, point.y - 10)
            ctx.fillStyle = '#607b7d'
          }
        }
      })
    } else if (s11) {
      // Single point
      let s11Real: number, s11Imag: number
      if (typeof s11 === 'number') {
        s11Real = s11
        s11Imag = 0
      } else {
        s11Real = s11.real
        s11Imag = s11.imag
      }

      const point = gammaToXY(s11Real, s11Imag)
      
      // Draw point with professional styling
      ctx.fillStyle = '#607b7d'  // Primary color
      ctx.beginPath()
      ctx.arc(point.x, point.y, 10, 0, 2 * Math.PI)
      ctx.fill()
      
      // White border
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(point.x, point.y, 10, 0, 2 * Math.PI)
      ctx.stroke()
      
      // Center dot
      ctx.fillStyle = '#3a606e'  // Primary dark
      ctx.beginPath()
      ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI)
      ctx.fill()
    }

    // Mark 50 ohm center (perfect match)
    const centerPoint = gammaToXY(0, 0)
    ctx.strokeStyle = '#828e82'  // Secondary color for center marker
    ctx.lineWidth = 2.5
    ctx.beginPath()
    ctx.moveTo(centerPoint.x - 12, centerPoint.y)
    ctx.lineTo(centerPoint.x + 12, centerPoint.y)
    ctx.moveTo(centerPoint.x, centerPoint.y - 12)
    ctx.lineTo(centerPoint.x, centerPoint.y + 12)
    ctx.stroke()
    
    // Center circle
    ctx.beginPath()
    ctx.arc(centerPoint.x, centerPoint.y, 14, 0, 2 * Math.PI)
    ctx.stroke()

    // Labels with better positioning
    ctx.fillStyle = '#3a606e'  // Primary dark
    ctx.font = 'bold 13px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('50Ω', centerX + radius - 30, centerY - 10)
    ctx.textAlign = 'left'
    ctx.font = 'bold 11px Arial'
    ctx.fillText('0Ω', centerX - radius + 10, centerY - 8)
    ctx.fillText('∞Ω', centerX - radius - 20, centerY - 8)
    
    // VSWR labels with better positioning
    ctx.fillStyle = '#6b7a6b'  // Neutral color
    ctx.font = '10px Arial'
    ctx.textAlign = 'left'
    vswrValues.forEach((vswr, idx) => {
      const gamma_mag = (vswr - 1) / (vswr + 1)
      const labelX = centerX + gamma_mag * radius + 8
      const labelY = centerY - 8 + (idx * 15)  // Stagger labels vertically
      ctx.fillText(`VSWR=${vswr}`, labelX, labelY)
    })
    
    // Title
    ctx.fillStyle = '#3a606e'
    ctx.font = 'bold 14px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('Smith Chart', centerX, 20)

  }, [s11, frequencies, s11Data, width, height])

  return (
    <div className="flex justify-center items-center" style={{ width: `${width}px`, height: `${height}px`, flexShrink: 0, flexGrow: 0 }}>
      <canvas 
        ref={canvasRef}
        style={{ 
          width: `${width}px`, 
          height: `${height}px`, 
          display: 'block',
          flexShrink: 0,
          flexGrow: 0,
          maxWidth: `${width}px`,
          maxHeight: `${height}px`
        }}
      />
    </div>
  )
}
