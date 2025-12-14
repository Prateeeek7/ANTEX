import { useEffect, useRef, useState } from 'react'
import { geometryApi, GeometryData } from '../api/geometry'

interface GeometryCanvasProps {
  designType?: string
  shapeFamily?: string
  params: Record<string, any>
  width?: number
  height?: number
  showAnnotations?: boolean
  showSubstrate?: boolean
  scale?: number
}

/**
 * Industry-Grade Geometry Canvas for Multi-Shape Antenna Visualization.
 * 
 * Features:
 * - Supports all antenna shape families
 * - CAD-like visualization with annotations
 * - Accurate dimensional scaling
 * - Substrate, patch, slots, and feed representation
 * - Export capabilities
 */
export default function GeometryCanvas({
  designType = 'patch',
  shapeFamily,
  params,
  width = 400,
  height = 400,
  showAnnotations = true,
  showSubstrate = true,
  scale
}: GeometryCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [geometry, setGeometry] = useState<GeometryData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Determine shape family
  const family = shapeFamily || (designType === 'patch' ? 'rectangular_patch' : designType)

  useEffect(() => {
    if (!params || Object.keys(params).length === 0) {
      setGeometry(null)
      return
    }

    loadGeometry()
  }, [family, params, showAnnotations, showSubstrate])

  const loadGeometry = async () => {
    setLoading(true)
    setError(null)
    try {
      // Filter out non-numeric parameters (like shape_family, design_type)
      const numericParams: Record<string, number> = {}
      for (const [key, value] of Object.entries(params || {})) {
        if (typeof value === 'number' && key !== 'shape_family' && key !== 'design_type') {
          numericParams[key] = value
        }
      }

      const result = await geometryApi.renderGeometry({
        shape_family: family,
        parameters: numericParams,
        include_annotations: showAnnotations,
        include_substrate: showSubstrate,
      })
      setGeometry(result.geometry)
    } catch (err: any) {
      console.error('Failed to render geometry:', err)
      const errorDetail = err.response?.data?.detail
      const errorMsg = Array.isArray(errorDetail) 
        ? errorDetail.map((e: any) => e.msg || String(e)).join(', ')
        : (typeof errorDetail === 'string' ? errorDetail : 'Failed to render geometry')
      setError(errorMsg)
      // Fallback to simple rendering
      renderSimpleGeometry()
    } finally {
      setLoading(false)
    }
  }

  const renderSimpleGeometry = () => {
    // Fallback simple rendering for backward compatibility
    if (designType === 'patch' && params) {
      const length = params.length_mm || 30
      const width = params.width_mm || 25
      const feedOffset = params.feed_offset_mm || 0

      const simpleGeometry: GeometryData = {
        patch: {
          type: 'rectangle',
          x: -length / 2,
          y: -width / 2,
          width: length,
          height: width,
        },
        feed: {
          type: 'point',
          x: length / 2 + feedOffset,
          y: width / 2,
          radius: 1.0,
        },
        slots: [],
        annotations: [],
        bounds: {
          x_min: -length / 2,
          y_min: -width / 2,
          x_max: length / 2,
          y_max: width / 2,
        },
      }
      setGeometry(simpleGeometry)
    }
  }

  useEffect(() => {
    if (!geometry || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Calculate scale and viewport
    const bounds = geometry.bounds
    const boundsWidth = bounds.x_max - bounds.x_min
    const boundsHeight = bounds.y_max - bounds.y_min
    const margin = Math.max(boundsWidth, boundsHeight) * 0.2

    const viewWidth = boundsWidth + 2 * margin
    const viewHeight = boundsHeight + 2 * margin
    const viewX = bounds.x_min - margin
    const viewY = bounds.y_min - margin

    // Set canvas size
    canvas.width = width
    canvas.height = height

    // Calculate scale to fit
    const scaleX = width / viewWidth
    const scaleY = height / viewHeight
    const finalScale = Math.min(scaleX, scaleY) * (scale || 1)

    // Transform to center and scale
    ctx.save()
    ctx.translate(width / 2, height / 2)
    ctx.scale(finalScale, finalScale)
    ctx.translate(-(bounds.x_min + bounds.x_max) / 2, -(bounds.y_min + bounds.y_max) / 2)

    // Clear
    ctx.clearRect(viewX, viewY, viewWidth, viewHeight)

    // Draw substrate
    if (showSubstrate && geometry.substrate) {
      const sub = geometry.substrate
      ctx.fillStyle = '#e0e0e0'
      ctx.strokeStyle = '#999'
      ctx.lineWidth = 0.5 / finalScale
      ctx.globalAlpha = 0.3
      ctx.fillRect(sub.x, sub.y, sub.width, sub.height)
      ctx.globalAlpha = 1.0
      ctx.strokeRect(sub.x, sub.y, sub.width, sub.height)
    }

    // Draw patch
    if (geometry.patch) {
      drawShape(ctx, geometry.patch, '#3b82f6', '#1e40af', 0.5 / finalScale)
    }

    // Draw slots (cutouts)
    geometry.slots.forEach(slot => {
      drawShape(ctx, slot, '#ffffff', '#999', 0.3 / finalScale, 0.9)
    })

        // Draw ground plane (for monopoles)
        if (geometry.ground_plane) {
          drawShape(ctx, geometry.ground_plane, '#888888', '#666666', 0.3 / finalScale, 0.8)
        }
        
        // Draw feed line
        if (geometry.feed_line) {
          drawShape(ctx, geometry.feed_line, '#ff6b6b', '#cc0000', 0.3 / finalScale)
        }

    // Draw feed point
    if (geometry.feed) {
      const feed = geometry.feed
      ctx.fillStyle = '#ff0000'
      ctx.strokeStyle = '#cc0000'
      ctx.lineWidth = 0.2 / finalScale
      ctx.beginPath()
      ctx.arc(feed.x, feed.y, feed.radius, 0, 2 * Math.PI)
      ctx.fill()
      ctx.stroke()
    }

    // Draw annotations
    if (showAnnotations) {
      geometry.annotations.forEach(ann => {
        ctx.fillStyle = '#333'
        ctx.font = `${3 / finalScale}px Arial`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(ann.label, ann.x, ann.y)
      })
    }

    // Draw centerlines
    ctx.strokeStyle = '#ccc'
    ctx.lineWidth = 0.2 / finalScale
    ctx.setLineDash([2 / finalScale, 2 / finalScale])
    ctx.beginPath()
    ctx.moveTo(bounds.x_min, 0)
    ctx.lineTo(bounds.x_max, 0)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(0, bounds.y_min)
    ctx.lineTo(0, bounds.y_max)
    ctx.stroke()
    ctx.setLineDash([])

    ctx.restore()
  }, [geometry, width, height, showAnnotations, showSubstrate, scale])

    const drawShape = (
    ctx: CanvasRenderingContext2D,
    shape: any,
    fillColor: string,
    strokeColor: string,
    lineWidth: number,
    opacity: number = 1.0
  ) => {
    ctx.fillStyle = fillColor
    ctx.strokeStyle = strokeColor
    ctx.lineWidth = lineWidth
    ctx.globalAlpha = opacity

    if (shape.type === 'rectangle') {
      ctx.fillRect(shape.x, shape.y, shape.width, shape.height)
      ctx.strokeRect(shape.x, shape.y, shape.width, shape.height)
    } else if (shape.type === 'circle') {
      ctx.beginPath()
      ctx.arc(shape.cx, shape.cy, shape.r, 0, 2 * Math.PI)
      ctx.fill()
      ctx.stroke()
    } else if (shape.type === 'ellipse') {
      ctx.beginPath()
      ctx.ellipse(shape.cx, shape.cy, shape.rx, shape.ry, 0, 0, 2 * Math.PI)
      ctx.fill()
      ctx.stroke()
    } else if (shape.type === 'polygon' && shape.points) {
      ctx.beginPath()
      shape.points.forEach((point: number[], idx: number) => {
        if (idx === 0) {
          ctx.moveTo(point[0], point[1])
        } else {
          ctx.lineTo(point[0], point[1])
        }
      })
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
    } else if (shape.type === 'polyline' && shape.points) {
      // Enhanced polyline rendering for meandered lines
      const lineW = (shape.width || 1.0) / (scale || 1)
      ctx.lineWidth = lineW
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      
      ctx.beginPath()
      shape.points.forEach((point: number[], idx: number) => {
        if (idx === 0) {
          ctx.moveTo(point[0], point[1])
        } else {
          ctx.lineTo(point[0], point[1])
        }
      })
      ctx.stroke()
      
      // If segments are available (for meandered lines), draw them as rectangles for better visibility
      if (shape.segments && Array.isArray(shape.segments)) {
        shape.segments.forEach((seg: any) => {
          if (seg.type === 'rectangle') {
            ctx.fillRect(seg.x, seg.y, seg.width, seg.height)
            ctx.strokeRect(seg.x, seg.y, seg.width, seg.height)
          }
        })
      }
    } else if (shape.type === 'rounded_rectangle') {
      // Rounded rectangle with corner radius
      const r = shape.corner_radius || 0
      const x = shape.x
      const y = shape.y
      const w = shape.width
      const h = shape.height
      
      ctx.beginPath()
      ctx.moveTo(x + r, y)
      ctx.lineTo(x + w - r, y)
      ctx.quadraticCurveTo(x + w, y, x + w, y + r)
      ctx.lineTo(x + w, y + h - r)
      ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
      ctx.lineTo(x + r, y + h)
      ctx.quadraticCurveTo(x, y + h, x, y + h - r)
      ctx.lineTo(x, y + r)
      ctx.quadraticCurveTo(x, y, x + r, y)
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
    }

    ctx.globalAlpha = 1.0
    ctx.lineCap = 'butt' // Reset
    ctx.lineJoin = 'miter' // Reset
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-gray-500 text-sm">Rendering geometry...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-red-500 text-sm">{error}</div>
      </div>
    )
  }

  if (!geometry) {
    return (
      <div className="flex items-center justify-center border border-gray-300 rounded" style={{ width, height }}>
        <div className="text-gray-500 text-sm">No geometry data</div>
      </div>
    )
  }

  return (
    <div className="border border-gray-300 rounded bg-white">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{ width: '100%', height: 'auto', display: 'block' }}
      />
    </div>
  )
}
