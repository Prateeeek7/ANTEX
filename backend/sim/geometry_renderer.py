"""
Geometry Renderer for Multi-Shape Antenna Visualization.

Generates coordinate sets for rendering antenna geometries in:
- SVG format
- DXF format
- Canvas coordinates
- JSON export
"""
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import json
import logging
from .geometry_framework import AntennaShapeFamily, get_shape_family

logger = logging.getLogger(__name__)


class GeometryRenderer:
    """Renders antenna geometries to various formats."""
    
    def __init__(self, scale_mm_per_pixel: float = 1.0):
        """
        Initialize renderer.
        
        Args:
            scale_mm_per_pixel: Scale factor (mm per pixel/unit)
        """
        self.scale = scale_mm_per_pixel
    
    def render_geometry(
        self,
        shape_family: str,
        params: Dict[str, float],
        include_annotations: bool = True,
        include_substrate: bool = True
    ) -> Dict[str, Any]:
        """
        Render complete geometry with all components.
        
        Returns:
            Dictionary with:
            - substrate: Substrate outline coordinates
            - patch: Patch/radiator coordinates
            - slots: Slot cutout coordinates (if applicable)
            - feed: Feed line/point coordinates
            - annotations: Dimensional annotations
            - bounds: Bounding box [x_min, y_min, x_max, y_max]
        """
        try:
            family = AntennaShapeFamily(shape_family)
        except ValueError:
            logger.error(f"Unknown shape family: {shape_family}")
            return self._empty_geometry()
        
        # Get substrate bounds
        substrate = self._get_substrate_bounds(params) if include_substrate else None
        
        # Render based on family
        if family == AntennaShapeFamily.RECTANGULAR_PATCH:
            return self._render_rectangular_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.U_SLOT_PATCH:
            return self._render_u_slot_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.E_SLOT_PATCH:
            return self._render_e_slot_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.INSET_FEED_PATCH:
            return self._render_inset_feed_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.MEANDERED_LINE:
            return self._render_meandered_line(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.PLANAR_MONOPOLE_ELLIPTICAL:
            return self._render_elliptical_monopole(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.PLANAR_MONOPOLE_CIRCULAR:
            return self._render_circular_monopole(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.PLANAR_MONOPOLE_HEXAGONAL:
            return self._render_hexagonal_monopole(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.ROUNDED_PATCH:
            return self._render_rounded_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.BOWTIE_PATCH:
            return self._render_bowtie_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.STAR_PATCH:
            return self._render_star_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.RING_PATCH:
            return self._render_ring_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.L_SLOT_PATCH:
            return self._render_l_slot_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.CROSS_SLOT_PATCH:
            return self._render_cross_slot_patch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.FRACTAL_KOCH:
            return self._render_fractal_koch(params, substrate, include_annotations)
        elif family == AntennaShapeFamily.CURVED_MONOPOLE:
            return self._render_curved_monopole(params, substrate, include_annotations)
        else:
            return self._empty_geometry()
    
    def _get_substrate_bounds(self, params: Dict[str, float]) -> Dict[str, float]:
        """Get substrate bounds (typically 2x patch size for margin)."""
        # Default substrate size
        max_dim = max(
            params.get("length_mm", 50),
            params.get("width_mm", 50),
            params.get("major_axis_mm", 50) * 2,
            params.get("radius_mm", 50) * 2,
            params.get("side_length_mm", 50) * 2,
        )
        margin = max_dim * 0.5  # 50% margin
        size = max_dim + 2 * margin
        
        return {
            "x": -size / 2,
            "y": -size / 2,
            "width": size,
            "height": size,
        }
    
    def _render_rectangular_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render rectangular patch antenna."""
        length = params.get("length_mm", 30.0)
        width = params.get("width_mm", 30.0)
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        # Patch centered at origin
        patch_x = -length / 2
        patch_y = -width / 2
        
        patch = {
            "type": "rectangle",
            "x": patch_x,
            "y": patch_y,
            "width": length,
            "height": width,
        }
        
        # Feed point
        feed_x = patch_x + length / 2 + feed_offset
        feed_y = patch_y + width / 2
        
        feed = {
            "type": "point",
            "x": feed_x,
            "y": feed_y,
            "radius": 1.0,  # 1mm feed point
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"L={length:.1f}mm", "x": patch_x, "y": patch_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"W={width:.1f}mm", "x": patch_x - 3, "y": patch_y, "orientation": "vertical"},
            ]
        
        bounds = {
            "x_min": patch_x,
            "y_min": patch_y,
            "x_max": patch_x + length,
            "y_max": patch_y + width,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_u_slot_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render U-slot patch antenna with accurate U-slot geometry."""
        length = params.get("length_mm", 40.0)
        width = params.get("width_mm", 40.0)
        feed_offset = params.get("feed_offset_mm", 0.0)
        slot_width = params.get("slot_width_mm", 3.0)
        slot_depth = params.get("slot_depth_mm", 15.0)
        slot_offset = params.get("slot_offset_mm", 0.0)
        
        # Base patch
        patch_x = -length / 2
        patch_y = -width / 2
        
        patch = {
            "type": "rectangle",
            "x": patch_x,
            "y": patch_y,
            "width": length,
            "height": width,
        }
        
        # U-slot geometry (accurate U-shape with opening at bottom)
        slot_center_x = slot_offset
        slot_center_y = 0  # Center of patch vertically
        
        # U-slot: vertical left arm, horizontal bottom, vertical right arm
        slot_left_x = slot_center_x - slot_depth / 2
        slot_right_x = slot_center_x + slot_depth / 2
        slot_top_y = slot_center_y - slot_width / 2
        slot_bottom_y = slot_center_y + slot_width / 2
        
        # Create U-slot as polygon path (left vertical, bottom horizontal, right vertical)
        slot_points = [
            [slot_left_x, slot_top_y],  # Top-left of left arm
            [slot_left_x, slot_bottom_y],  # Bottom-left (start of horizontal)
            [slot_right_x, slot_bottom_y],  # Bottom-right (end of horizontal)
            [slot_right_x, slot_top_y],  # Top-right of right arm
        ]
        
        slot = {
            "type": "polygon",
            "points": slot_points,
        }
        
        # Feed point (on bottom edge, offset from center)
        feed_x = patch_x + length / 2 + feed_offset
        feed_y = patch_y + width / 2
        
        feed = {
            "type": "point",
            "x": feed_x,
            "y": feed_y,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"L={length:.1f}mm", "x": patch_x, "y": patch_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"W={width:.1f}mm", "x": patch_x - 3, "y": patch_y, "orientation": "vertical"},
                {"type": "dimension", "label": f"Slot W={slot_width:.1f}mm", "x": slot_center_x, "y": slot_top_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"Slot D={slot_depth:.1f}mm", "x": slot_right_x + 3, "y": slot_center_y, "orientation": "vertical"},
            ]
        
        bounds = {
            "x_min": patch_x,
            "y_min": patch_y,
            "x_max": patch_x + length,
            "y_max": patch_y + width,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [slot],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_e_slot_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render E-slot patch antenna with accurate E-shaped slot geometry."""
        length = params.get("length_mm", 40.0)
        width = params.get("width_mm", 40.0)
        feed_offset = params.get("feed_offset_mm", 0.0)
        left_slot_w = params.get("left_slot_width_mm", 3.0)
        right_slot_w = params.get("right_slot_width_mm", 3.0)
        center_slot_w = params.get("center_slot_width_mm", 2.0)
        slot_depth = params.get("slot_depth_mm", 15.0)
        
        # Base patch
        patch_x = -length / 2
        patch_y = -width / 2
        
        patch = {
            "type": "rectangle",
            "x": patch_x,
            "y": patch_y,
            "width": length,
            "height": width,
        }
        
        # E-slot: three vertical slots connected by horizontal bar (creating E shape)
        slot_center_y = 0  # Vertical center
        slot_top = slot_center_y - slot_depth / 2
        slot_bottom = slot_center_y + slot_depth / 2
        horizontal_bar_y = slot_center_y + slot_depth / 3  # Horizontal connecting bar
        
        # Left slot (vertical)
        left_slot_x = -width / 3
        left_slot = {
            "type": "polygon",
            "points": [
                [left_slot_x - left_slot_w/2, slot_top],
                [left_slot_x - left_slot_w/2, slot_bottom],
                [left_slot_x + left_slot_w/2, slot_bottom],
                [left_slot_x + left_slot_w/2, slot_top],
            ],
        }
        
        # Right slot (vertical)
        right_slot_x = width / 3
        right_slot = {
            "type": "polygon",
            "points": [
                [right_slot_x - right_slot_w/2, slot_top],
                [right_slot_x - right_slot_w/2, slot_bottom],
                [right_slot_x + right_slot_w/2, slot_bottom],
                [right_slot_x + right_slot_w/2, slot_top],
            ],
        }
        
        # Center slot (vertical, extends from top to horizontal bar)
        center_slot = {
            "type": "polygon",
            "points": [
                [-center_slot_w/2, slot_top],
                [-center_slot_w/2, horizontal_bar_y],
                [center_slot_w/2, horizontal_bar_y],
                [center_slot_w/2, slot_top],
            ],
        }
        
        # Horizontal connecting bar (forms the E shape)
        bar_slot = {
            "type": "rectangle",
            "x": left_slot_x - left_slot_w/2,
            "y": horizontal_bar_y - center_slot_w/2,
            "width": (right_slot_x + right_slot_w/2) - (left_slot_x - left_slot_w/2),
            "height": center_slot_w,
        }
        
        # Feed point
        feed_x = patch_x + length / 2 + feed_offset
        feed_y = patch_y + width / 2
        
        feed = {
            "type": "point",
            "x": feed_x,
            "y": feed_y,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"L={length:.1f}mm", "x": patch_x, "y": patch_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"W={width:.1f}mm", "x": patch_x - 3, "y": patch_y, "orientation": "vertical"},
                {"type": "dimension", "label": f"Slot D={slot_depth:.1f}mm", "x": right_slot_x + 5, "y": slot_center_y, "orientation": "vertical"},
            ]
        
        bounds = {
            "x_min": patch_x,
            "y_min": patch_y,
            "x_max": patch_x + length,
            "y_max": patch_y + width,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [left_slot, right_slot, center_slot, bar_slot],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_inset_feed_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render inset-feed patch antenna."""
        length = params.get("length_mm", 35.0)
        width = params.get("width_mm", 35.0)
        inset_depth = params.get("inset_depth_mm", 8.0)
        inset_width = params.get("inset_width_mm", 2.0)
        
        # Patch
        patch_x = -length / 2
        patch_y = -width / 2
        
        patch = {
            "type": "rectangle",
            "x": patch_x,
            "y": patch_y,
            "width": length,
            "height": width,
        }
        
        # Inset cutout (notch in patch)
        inset_x = patch_x + length / 2 - inset_depth
        inset_y = patch_y + width / 2 - inset_width / 2
        
        inset_slot = {
            "type": "rectangle",
            "x": inset_x,
            "y": inset_y,
            "width": inset_depth,
            "height": inset_width,
        }
        
        # Feed line
        feed_line = {
            "type": "rectangle",
            "x": patch_x + length / 2,
            "y": patch_y + width / 2 - inset_width / 2,
            "width": 10.0,  # Feed line extends beyond patch
            "height": inset_width,
        }
        
        # Feed point (at end of feed line)
        feed = {
            "type": "point",
            "x": patch_x + length / 2 + 10.0,
            "y": patch_y + width / 2,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"L={length:.1f}mm", "x": patch_x, "y": patch_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"Inset={inset_depth:.1f}mm", "x": inset_x, "y": patch_y + width + 3, "orientation": "horizontal"},
            ]
        
        bounds = {
            "x_min": patch_x,
            "y_min": patch_y,
            "x_max": patch_x + length + 10.0,  # Include feed line
            "y_max": patch_y + width,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [inset_slot],
            "feed": feed,
            "feed_line": feed_line,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_meandered_line(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render meandered line antenna."""
        total_length = params.get("total_length_mm", 50.0)
        line_width = params.get("line_width_mm", 1.0)
        segments = int(params.get("meander_segments", 5))
        segment_length = params.get("segment_length_mm", 10.0)
        
        # Generate meander path
        points = []
        x, y = 0, 0
        direction = 1  # 1 = right, -1 = left
        
        for i in range(segments):
            # Horizontal segment
            x_end = x + segment_length * direction
            points.append([x, y])
            points.append([x_end, y])
            x = x_end
            
            # Vertical turn (if not last segment)
            if i < segments - 1:
                y += line_width * 2
                points.append([x, y])
        
        # Convert to polygon (thick line)
        meander_path = {
            "type": "polyline",
            "points": points,
            "width": line_width,
        }
        
        # Feed point (start of meander)
        feed = {
            "type": "point",
            "x": 0,
            "y": 0,
            "radius": 1.0,
        }
        
        bounds = {
            "x_min": min(p[0] for p in points) - line_width,
            "y_min": min(p[1] for p in points) - line_width,
            "x_max": max(p[0] for p in points) + line_width,
            "y_max": max(p[1] for p in points) + line_width,
        }
        
        return {
            "substrate": substrate,
            "patch": meander_path,
            "slots": [],
            "feed": feed,
            "annotations": [],
            "bounds": bounds,
        }
    
    def _render_elliptical_monopole(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render elliptical monopole antenna."""
        major_axis = params.get("major_axis_mm", 40.0)
        minor_axis = params.get("minor_axis_mm", 20.0)
        feed_width = params.get("feed_width_mm", 2.0)
        
        # Ellipse centered at origin
        ellipse = {
            "type": "ellipse",
            "cx": 0,
            "cy": 0,
            "rx": major_axis / 2,
            "ry": minor_axis / 2,
        }
        
        # Feed line (vertical, below ellipse)
        feed_line = {
            "type": "rectangle",
            "x": -feed_width / 2,
            "y": -minor_axis / 2 - 10.0,
            "width": feed_width,
            "height": 10.0,
        }
        
        # Feed point
        feed = {
            "type": "point",
            "x": 0,
            "y": -minor_axis / 2 - 10.0,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"Major={major_axis:.1f}mm", "x": 0, "y": -minor_axis/2 - 5, "orientation": "horizontal"},
                {"type": "dimension", "label": f"Minor={minor_axis:.1f}mm", "x": major_axis/2 + 3, "y": 0, "orientation": "vertical"},
            ]
        
        bounds = {
            "x_min": -major_axis / 2,
            "y_min": -minor_axis / 2 - 10.0,
            "x_max": major_axis / 2,
            "y_max": minor_axis / 2,
        }
        
        return {
            "substrate": substrate,
            "patch": ellipse,
            "slots": [],
            "feed": feed,
            "feed_line": feed_line,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_circular_monopole(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render circular monopole antenna."""
        radius = params.get("radius_mm", 20.0)
        feed_width = params.get("feed_width_mm", 2.0)
        
        # Circle centered at origin
        circle = {
            "type": "circle",
            "cx": 0,
            "cy": 0,
            "r": radius,
        }
        
        # Feed line
        feed_line = {
            "type": "rectangle",
            "x": -feed_width / 2,
            "y": -radius - 10.0,
            "width": feed_width,
            "height": 10.0,
        }
        
        # Feed point
        feed = {
            "type": "point",
            "x": 0,
            "y": -radius - 10.0,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"R={radius:.1f}mm", "x": radius + 3, "y": 0, "orientation": "horizontal"},
            ]
        
        bounds = {
            "x_min": -radius,
            "y_min": -radius - 10.0,
            "x_max": radius,
            "y_max": radius,
        }
        
        return {
            "substrate": substrate,
            "patch": circle,
            "slots": [],
            "feed": feed,
            "feed_line": feed_line,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_hexagonal_monopole(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render hexagonal monopole antenna."""
        side_length = params.get("side_length_mm", 20.0)
        feed_width = params.get("feed_width_mm", 2.0)
        
        # Generate hexagon points
        import math
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 6  # Rotate so flat side is on top
            x = side_length * math.cos(angle)
            y = side_length * math.sin(angle)
            points.append([x, y])
        
        hexagon = {
            "type": "polygon",
            "points": points,
        }
        
        # Feed line
        feed_line = {
            "type": "rectangle",
            "x": -feed_width / 2,
            "y": -side_length - 10.0,
            "width": feed_width,
            "height": 10.0,
        }
        
        # Feed point
        feed = {
            "type": "point",
            "x": 0,
            "y": -side_length - 10.0,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"Side={side_length:.1f}mm", "x": side_length + 3, "y": 0, "orientation": "horizontal"},
            ]
        
        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)
        min_x = min(p[0] for p in points)
        min_y = min(p[1] for p in points)
        
        bounds = {
            "x_min": min_x,
            "y_min": min_y - 10.0,
            "x_max": max_x,
            "y_max": max_y,
        }
        
        return {
            "substrate": substrate,
            "patch": hexagon,
            "slots": [],
            "feed": feed,
            "feed_line": feed_line,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_rounded_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render rounded patch antenna (rectangle with rounded corners)."""
        length = params.get("length_mm", 35.0)
        width = params.get("width_mm", 35.0)
        corner_radius = params.get("corner_radius_mm", 5.0)
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        patch_x = -length / 2
        patch_y = -width / 2
        
        # Rounded rectangle as polygon (approximated with multiple points)
        import math
        points = []
        num_segments = 8  # Segments per corner
        corner_radius = min(corner_radius, min(length, width) / 2)  # Limit radius
        
        # Top-left corner
        for i in range(num_segments + 1):
            angle = math.pi / 2 * (i / num_segments)
            x = patch_x + corner_radius - corner_radius * math.cos(angle)
            y = patch_y + corner_radius - corner_radius * math.sin(angle)
            points.append([x, y])
        
        # Top edge
        points.append([patch_x + length - corner_radius, patch_y])
        
        # Top-right corner
        for i in range(num_segments + 1):
            angle = math.pi / 2 + math.pi / 2 * (i / num_segments)
            x = patch_x + length - corner_radius + corner_radius * math.cos(angle)
            y = patch_y + corner_radius - corner_radius * math.sin(angle)
            points.append([x, y])
        
        # Right edge
        points.append([patch_x + length, patch_y + width - corner_radius])
        
        # Bottom-right corner
        for i in range(num_segments + 1):
            angle = math.pi + math.pi / 2 * (i / num_segments)
            x = patch_x + length - corner_radius + corner_radius * math.cos(angle)
            y = patch_y + width - corner_radius + corner_radius * math.sin(angle)
            points.append([x, y])
        
        # Bottom edge
        points.append([patch_x + corner_radius, patch_y + width])
        
        # Bottom-left corner
        for i in range(num_segments + 1):
            angle = 3 * math.pi / 2 + math.pi / 2 * (i / num_segments)
            x = patch_x + corner_radius - corner_radius * math.cos(angle)
            y = patch_y + width - corner_radius + corner_radius * math.sin(angle)
            points.append([x, y])
        
        # Left edge
        points.append([patch_x, patch_y + corner_radius])
        
        patch = {
            "type": "polygon",
            "points": points,
        }
        
        feed_x = patch_x + length / 2 + feed_offset
        feed_y = patch_y + width / 2
        
        feed = {
            "type": "point",
            "x": feed_x,
            "y": feed_y,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"L={length:.1f}mm", "x": patch_x, "y": patch_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"R={corner_radius:.1f}mm", "x": patch_x + corner_radius, "y": patch_y + corner_radius + 3, "orientation": "horizontal"},
            ]
        
        bounds = {
            "x_min": patch_x,
            "y_min": patch_y,
            "x_max": patch_x + length,
            "y_max": patch_y + width,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_bowtie_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render bowtie patch antenna (diamond/bowtie shape)."""
        width = params.get("width_mm", 40.0)
        height = params.get("height_mm", 40.0)
        apex_angle = params.get("apex_angle_deg", 60.0) * np.pi / 180  # Convert to radians
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        # Bowtie: two triangles meeting at center
        # Top triangle
        top_points = [
            [0, -height / 2],  # Top apex
            [-width / 2, 0],   # Left point
            [width / 2, 0],    # Right point
        ]
        
        # Bottom triangle
        bottom_points = [
            [0, height / 2],   # Bottom apex
            [-width / 2, 0],   # Left point
            [width / 2, 0],    # Right point
        ]
        
        # Combine into bowtie polygon
        bowtie_points = top_points + bottom_points[1:]  # Skip duplicate center points
        
        patch = {
            "type": "polygon",
            "points": bowtie_points,
        }
        
        feed_x = feed_offset
        feed_y = 0
        
        feed = {
            "type": "point",
            "x": feed_x,
            "y": feed_y,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"W={width:.1f}mm", "x": 0, "y": -height/2 - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"H={height:.1f}mm", "x": width/2 + 3, "y": 0, "orientation": "vertical"},
            ]
        
        bounds = {
            "x_min": -width / 2,
            "y_min": -height / 2,
            "x_max": width / 2,
            "y_max": height / 2,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_star_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render star patch antenna."""
        outer_radius = params.get("outer_radius_mm", 30.0)
        inner_radius = params.get("inner_radius_mm", 15.0)
        num_points = int(params.get("num_points", 5))
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        import math
        points = []
        for i in range(num_points * 2):
            angle = (i * math.pi) / num_points - math.pi / 2
            if i % 2 == 0:
                # Outer point
                r = outer_radius
            else:
                # Inner point
                r = inner_radius
            x = r * math.cos(angle) + feed_offset
            y = r * math.sin(angle)
            points.append([x, y])
        
        patch = {
            "type": "polygon",
            "points": points,
        }
        
        feed = {
            "type": "point",
            "x": feed_offset,
            "y": 0,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"R_out={outer_radius:.1f}mm", "x": outer_radius + 3, "y": 0, "orientation": "horizontal"},
                {"type": "dimension", "label": f"R_in={inner_radius:.1f}mm", "x": inner_radius + 3, "y": 0, "orientation": "horizontal"},
            ]
        
        bounds = {
            "x_min": -outer_radius,
            "y_min": -outer_radius,
            "x_max": outer_radius,
            "y_max": outer_radius,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_ring_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render annular ring patch antenna (donut shape)."""
        outer_radius = params.get("outer_radius_mm", 30.0)
        inner_radius = params.get("inner_radius_mm", 10.0)
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        # Ring is represented as two circles (outer and inner cutout)
        outer_circle = {
            "type": "circle",
            "cx": feed_offset,
            "cy": 0,
            "r": outer_radius,
        }
        
        inner_circle = {
            "type": "circle",
            "cx": feed_offset,
            "cy": 0,
            "r": inner_radius,
        }
        
        patch = outer_circle  # Main patch
        ring_cutout = inner_circle  # Inner hole
        
        feed = {
            "type": "point",
            "x": feed_offset + outer_radius * 0.7,
            "y": 0,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"R_out={outer_radius:.1f}mm", "x": outer_radius + 3, "y": 0, "orientation": "horizontal"},
                {"type": "dimension", "label": f"R_in={inner_radius:.1f}mm", "x": inner_radius + 3, "y": 0, "orientation": "horizontal"},
            ]
        
        bounds = {
            "x_min": -outer_radius,
            "y_min": -outer_radius,
            "x_max": outer_radius,
            "y_max": outer_radius,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [ring_cutout],  # Inner circle as cutout
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_l_slot_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render L-slot patch antenna."""
        length = params.get("length_mm", 40.0)
        width = params.get("width_mm", 40.0)
        slot_width = params.get("slot_width_mm", 3.0)
        horizontal_arm = params.get("horizontal_arm_mm", 15.0)
        vertical_arm = params.get("vertical_arm_mm", 15.0)
        slot_x = params.get("slot_position_x_mm", 0.0)
        slot_y = params.get("slot_position_y_mm", 0.0)
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        patch_x = -length / 2
        patch_y = -width / 2
        
        patch = {
            "type": "rectangle",
            "x": patch_x,
            "y": patch_y,
            "width": length,
            "height": width,
        }
        
        # L-slot: horizontal and vertical arms
        slot_center_x = slot_x
        slot_center_y = slot_y
        
        # Horizontal arm (left to right)
        horizontal_slot = {
            "type": "rectangle",
            "x": slot_center_x - horizontal_arm / 2,
            "y": slot_center_y - slot_width / 2,
            "width": horizontal_arm,
            "height": slot_width,
        }
        
        # Vertical arm (top to bottom, connected to horizontal)
        vertical_slot = {
            "type": "rectangle",
            "x": slot_center_x + horizontal_arm / 2 - slot_width / 2,
            "y": slot_center_y - slot_width / 2,
            "width": slot_width,
            "height": vertical_arm,
        }
        
        feed_x = patch_x + length / 2 + feed_offset
        feed_y = patch_y + width / 2
        
        feed = {
            "type": "point",
            "x": feed_x,
            "y": feed_y,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"L={length:.1f}mm", "x": patch_x, "y": patch_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"L-slot", "x": slot_center_x, "y": slot_center_y - vertical_arm - 3, "orientation": "horizontal"},
            ]
        
        bounds = {
            "x_min": patch_x,
            "y_min": patch_y,
            "x_max": patch_x + length,
            "y_max": patch_y + width,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [horizontal_slot, vertical_slot],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_cross_slot_patch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render cross-slot patch antenna."""
        length = params.get("length_mm", 40.0)
        width = params.get("width_mm", 40.0)
        slot_width = params.get("slot_width_mm", 3.0)
        horizontal_arm = params.get("horizontal_arm_mm", 20.0)
        vertical_arm = params.get("vertical_arm_mm", 20.0)
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        patch_x = -length / 2
        patch_y = -width / 2
        
        patch = {
            "type": "rectangle",
            "x": patch_x,
            "y": patch_y,
            "width": length,
            "height": width,
        }
        
        # Cross-slot: horizontal and vertical arms crossing at center
        slot_center_x = 0
        slot_center_y = 0
        
        # Horizontal arm
        horizontal_slot = {
            "type": "rectangle",
            "x": slot_center_x - horizontal_arm / 2,
            "y": slot_center_y - slot_width / 2,
            "width": horizontal_arm,
            "height": slot_width,
        }
        
        # Vertical arm
        vertical_slot = {
            "type": "rectangle",
            "x": slot_center_x - slot_width / 2,
            "y": slot_center_y - vertical_arm / 2,
            "width": slot_width,
            "height": vertical_arm,
        }
        
        feed_x = patch_x + length / 2 + feed_offset
        feed_y = patch_y + width / 2
        
        feed = {
            "type": "point",
            "x": feed_x,
            "y": feed_y,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"L={length:.1f}mm", "x": patch_x, "y": patch_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"Cross-slot", "x": 0, "y": -vertical_arm/2 - 3, "orientation": "horizontal"},
            ]
        
        bounds = {
            "x_min": patch_x,
            "y_min": patch_y,
            "x_max": patch_x + length,
            "y_max": patch_y + width,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [horizontal_slot, vertical_slot],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_fractal_koch(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render Koch fractal antenna."""
        base_length = params.get("base_length_mm", 40.0)
        iterations = int(params.get("iterations", 2))
        feed_offset = params.get("feed_offset_mm", 0.0)
        
        import math
        
        def koch_curve(start, end, depth):
            """Generate Koch curve points recursively."""
            if depth == 0:
                return [start, end]
            
            # Divide line into 3 segments
            p1 = start
            p4 = end
            
            dx = (end[0] - start[0]) / 3
            dy = (end[1] - start[1]) / 3
            
            p2 = [start[0] + dx, start[1] + dy]
            p4_temp = [start[0] + 2*dx, start[1] + 2*dy]
            
            # Calculate third point (apex of equilateral triangle)
            angle = math.atan2(dy, dx)
            side_length = math.sqrt(dx**2 + dy**2)
            apex_angle = angle + math.pi / 3
            p3 = [
                p2[0] + side_length * math.cos(apex_angle),
                p2[1] + side_length * math.sin(apex_angle)
            ]
            
            # Recursively generate points
            points = []
            points.extend(koch_curve(p1, p2, depth - 1)[:-1])
            points.extend(koch_curve(p2, p3, depth - 1)[:-1])
            points.extend(koch_curve(p3, p4_temp, depth - 1)[:-1])
            points.extend(koch_curve(p4_temp, p4, depth - 1))
            
            return points
        
        # Generate triangle base points
        center_x = feed_offset
        center_y = 0
        height = base_length * math.sqrt(3) / 2
        
        # Triangle vertices
        v1 = [center_x, center_y - 2*height/3]
        v2 = [center_x - base_length/2, center_y + height/3]
        v3 = [center_x + base_length/2, center_y + height/3]
        
        # Generate Koch snowflake
        all_points = []
        all_points.extend(koch_curve(v1, v2, iterations)[:-1])
        all_points.extend(koch_curve(v2, v3, iterations)[:-1])
        all_points.extend(koch_curve(v3, v1, iterations)[:-1])
        
        patch = {
            "type": "polygon",
            "points": all_points,
        }
        
        feed = {
            "type": "point",
            "x": feed_offset,
            "y": center_y,
            "radius": 1.0,
        }
        
        max_x = max(p[0] for p in all_points)
        min_x = min(p[0] for p in all_points)
        max_y = max(p[1] for p in all_points)
        min_y = min(p[1] for p in all_points)
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"Base={base_length:.1f}mm", "x": center_x, "y": min_y - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"Iter={iterations}", "x": max_x + 3, "y": center_y, "orientation": "vertical"},
            ]
        
        bounds = {
            "x_min": min_x,
            "y_min": min_y,
            "x_max": max_x,
            "y_max": max_y,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [],
            "feed": feed,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _render_curved_monopole(
        self,
        params: Dict[str, float],
        substrate: Optional[Dict[str, float]],
        include_annotations: bool
    ) -> Dict[str, Any]:
        """Render curved monopole antenna."""
        width = params.get("width_mm", 40.0)
        height = params.get("height_mm", 50.0)
        curve_radius = params.get("curve_radius_mm", 30.0)
        curve_direction = params.get("curve_direction", 1.0)
        feed_width = params.get("feed_width_mm", 2.0)
        
        import math
        
        # Generate curved profile
        num_points = 20
        points = []
        
        if curve_direction > 0:  # Convex (bulging outward)
            for i in range(num_points + 1):
                x = -width / 2 + (width * i / num_points)
                # Parabolic curve
                t = i / num_points
                y_offset = 4 * curve_radius * t * (1 - t)  # Parabolic curve
                y = -height / 2 + y_offset
                points.append([x, y])
        else:  # Concave (curving inward)
            for i in range(num_points + 1):
                x = -width / 2 + (width * i / num_points)
                t = i / num_points
                y_offset = -4 * curve_radius * t * (1 - t)  # Inverted parabola
                y = -height / 2 - y_offset
                points.append([x, y])
        
        # Add bottom edge (flat)
        points.append([width / 2, height / 2])
        points.append([-width / 2, height / 2])
        
        patch = {
            "type": "polygon",
            "points": points,
        }
        
        # Feed line
        feed_line = {
            "type": "rectangle",
            "x": -feed_width / 2,
            "y": height / 2,
            "width": feed_width,
            "height": 10.0,
        }
        
        feed = {
            "type": "point",
            "x": 0,
            "y": height / 2 + 10.0,
            "radius": 1.0,
        }
        
        annotations = []
        if include_annotations:
            annotations = [
                {"type": "dimension", "label": f"W={width:.1f}mm", "x": 0, "y": -height/2 - 3, "orientation": "horizontal"},
                {"type": "dimension", "label": f"H={height:.1f}mm", "x": width/2 + 3, "y": 0, "orientation": "vertical"},
            ]
        
        bounds = {
            "x_min": -width / 2,
            "y_min": -height / 2,
            "x_max": width / 2,
            "y_max": height / 2 + 10.0,
        }
        
        return {
            "substrate": substrate,
            "patch": patch,
            "slots": [],
            "feed": feed,
            "feed_line": feed_line,
            "annotations": annotations,
            "bounds": bounds,
        }
    
    def _empty_geometry(self) -> Dict[str, Any]:
        """Return empty geometry structure."""
        return {
            "substrate": None,
            "patch": None,
            "slots": [],
            "feed": None,
            "annotations": [],
            "bounds": {"x_min": 0, "y_min": 0, "x_max": 0, "y_max": 0},
        }
    
    def to_svg(
        self,
        geometry: Dict[str, Any],
        width: int = 800,
        height: int = 600
    ) -> str:
        """Convert geometry to SVG format."""
        bounds = geometry.get("bounds", {})
        x_min = bounds.get("x_min", 0)
        y_min = bounds.get("y_min", 0)
        x_max = bounds.get("x_max", 100)
        y_max = bounds.get("y_max", 100)
        
        # Calculate viewBox
        margin = 20
        view_width = (x_max - x_min) + 2 * margin
        view_height = (y_max - y_min) + 2 * margin
        view_x = x_min - margin
        view_y = y_min - margin
        
        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="{view_x} {view_y} {view_width} {view_height}" xmlns="http://www.w3.org/2000/svg">',
        ]
        
        # Substrate
        if geometry.get("substrate"):
            sub = geometry["substrate"]
            svg_parts.append(
                f'<rect x="{sub["x"]}" y="{sub["y"]}" width="{sub["width"]}" height="{sub["height"]}" '
                f'fill="#e0e0e0" stroke="#999" stroke-width="0.5" opacity="0.3"/>'
            )
        
        # Patch
        patch = geometry.get("patch")
        if patch:
            svg_parts.append(self._patch_to_svg(patch))
        
        # Slots (cutouts)
        for slot in geometry.get("slots", []):
            svg_parts.append(self._slot_to_svg(slot))
        
        # Feed line
        if geometry.get("feed_line"):
            feed_line = geometry["feed_line"]
            svg_parts.append(
                f'<rect x="{feed_line["x"]}" y="{feed_line["y"]}" width="{feed_line["width"]}" height="{feed_line["height"]}" '
                f'fill="#ff6b6b" stroke="#cc0000" stroke-width="0.3"/>'
            )
        
        # Feed point
        feed = geometry.get("feed")
        if feed:
            svg_parts.append(
                f'<circle cx="{feed["x"]}" cy="{feed["y"]}" r="{feed["radius"]}" fill="#ff0000" stroke="#cc0000" stroke-width="0.2"/>'
            )
        
        # Annotations
        for ann in geometry.get("annotations", []):
            svg_parts.append(
                f'<text x="{ann["x"]}" y="{ann["y"]}" font-size="3" fill="#333" text-anchor="middle">{ann["label"]}</text>'
            )
        
        svg_parts.append("</svg>")
        return "\n".join(svg_parts)
    
    def _patch_to_svg(self, patch: Dict[str, Any]) -> str:
        """Convert patch to SVG element."""
        if patch["type"] == "rectangle":
            return (
                f'<rect x="{patch["x"]}" y="{patch["y"]}" width="{patch["width"]}" height="{patch["height"]}" '
                f'fill="#3b82f6" stroke="#1e40af" stroke-width="0.5"/>'
            )
        elif patch["type"] == "circle":
            return (
                f'<circle cx="{patch["cx"]}" cy="{patch["cy"]}" r="{patch["r"]}" '
                f'fill="#3b82f6" stroke="#1e40af" stroke-width="0.5"/>'
            )
        elif patch["type"] == "ellipse":
            return (
                f'<ellipse cx="{patch["cx"]}" cy="{patch["cy"]}" rx="{patch["rx"]}" ry="{patch["ry"]}" '
                f'fill="#3b82f6" stroke="#1e40af" stroke-width="0.5"/>'
            )
        elif patch["type"] == "polygon":
            points_str = " ".join([f"{p[0]},{p[1]}" for p in patch["points"]])
            return (
                f'<polygon points="{points_str}" '
                f'fill="#3b82f6" stroke="#1e40af" stroke-width="0.5"/>'
            )
        elif patch["type"] == "polyline":
            points_str = " ".join([f"{p[0]},{p[1]}" for p in patch["points"]])
            return (
                f'<polyline points="{points_str}" '
                f'fill="none" stroke="#3b82f6" stroke-width="{patch.get("width", 1.0)}"/>'
            )
        return ""
    
    def _slot_to_svg(self, slot: Dict[str, Any]) -> str:
        """Convert slot to SVG element (cutout, so subtract from patch)."""
        if slot["type"] == "rectangle":
            return (
                f'<rect x="{slot["x"]}" y="{slot["y"]}" width="{slot["width"]}" height="{slot["height"]}" '
                f'fill="#ffffff" stroke="#999" stroke-width="0.3" opacity="0.9"/>'
            )
        elif slot["type"] == "polygon":
            points_str = " ".join([f"{p[0]},{p[1]}" for p in slot["points"]])
            return (
                f'<polygon points="{points_str}" '
                f'fill="#ffffff" stroke="#999" stroke-width="0.3" opacity="0.9"/>'
            )
        elif slot["type"] == "circle":
            return (
                f'<circle cx="{slot["cx"]}" cy="{slot["cy"]}" r="{slot["r"]}" '
                f'fill="#ffffff" stroke="#999" stroke-width="0.3" opacity="0.9"/>'
            )
        return ""
    
    def to_json(self, geometry: Dict[str, Any]) -> str:
        """Convert geometry to JSON format."""
        return json.dumps(geometry, indent=2)


def export_geometry_dxf(geometry: Dict[str, Any], filename: str) -> str:
    """
    Export geometry to DXF format (simplified).
    
    Note: Full DXF export would require dxfwrite library.
    This is a placeholder that returns a basic DXF structure.
    """
    # This is a simplified DXF export
    # For production, use dxfwrite library: pip install dxfwrite
    dxf_lines = [
        "0",
        "SECTION",
        "2",
        "HEADER",
        "0",
        "ENDSEC",
        "0",
        "SECTION",
        "2",
        "ENTITIES",
    ]
    
    # Add entities (patches, slots, etc.)
    # This is simplified - full implementation would convert all shapes
    
    dxf_lines.extend([
        "0",
        "ENDSEC",
        "0",
        "EOF",
    ])
    
    return "\n".join(dxf_lines)

