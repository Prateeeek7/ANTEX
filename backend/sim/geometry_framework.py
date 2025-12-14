"""
Unified Geometry Definition Framework for Multi-Shape Antenna Design.

This module provides:
- Shape family definitions with parameter sets
- Bounds and constraints per parameter
- Auto-design formulas based on frequency
- Geometry rendering coordinates
- Export capabilities (SVG/DXF/JSON)
"""
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AntennaShapeFamily(str, Enum):
    """Supported antenna shape families."""
    RECTANGULAR_PATCH = "rectangular_patch"
    U_SLOT_PATCH = "u_slot_patch"
    E_SLOT_PATCH = "e_slot_patch"
    INSET_FEED_PATCH = "inset_feed_patch"
    MEANDERED_LINE = "meandered_line"
    PLANAR_MONOPOLE_ELLIPTICAL = "planar_monopole_elliptical"
    PLANAR_MONOPOLE_CIRCULAR = "planar_monopole_circular"
    PLANAR_MONOPOLE_HEXAGONAL = "planar_monopole_hexagonal"
    # Advanced/Complex Shapes
    ROUNDED_PATCH = "rounded_patch"
    BOWTIE_PATCH = "bowtie_patch"
    STAR_PATCH = "star_patch"
    RING_PATCH = "ring_patch"
    L_SLOT_PATCH = "l_slot_patch"
    CROSS_SLOT_PATCH = "cross_slot_patch"
    FRACTAL_KOCH = "fractal_koch"
    CURVED_MONOPOLE = "curved_monopole"


@dataclass
class ParameterDefinition:
    """Definition of a geometric parameter."""
    name: str
    min_value: float
    max_value: float
    default_value: float
    unit: str = "mm"
    description: str = ""
    auto_design_formula: Optional[str] = None  # Formula for auto-design


@dataclass
class ShapeFamilyDefinition:
    """Complete definition of an antenna shape family."""
    family: AntennaShapeFamily
    display_name: str
    description: str
    parameters: List[ParameterDefinition] = field(default_factory=list)
    auto_design_enabled: bool = True
    
    def get_parameter(self, name: str) -> Optional[ParameterDefinition]:
        """Get parameter definition by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def validate_parameters(self, params: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Validate parameter values against bounds."""
        errors = []
        for param in self.parameters:
            if param.name in params:
                value = params[param.name]
                if value < param.min_value or value > param.max_value:
                    errors.append(
                        f"{param.name}: {value} {param.unit} out of range "
                        f"[{param.min_value}, {param.max_value}]"
                    )
        return len(errors) == 0, errors


# Shape Family Definitions
SHAPE_FAMILIES: Dict[AntennaShapeFamily, ShapeFamilyDefinition] = {}

# 1. Rectangular Patch
SHAPE_FAMILIES[AntennaShapeFamily.RECTANGULAR_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.RECTANGULAR_PATCH,
    display_name="Rectangular Patch",
    description="Standard rectangular microstrip patch antenna",
    parameters=[
        ParameterDefinition("length_mm", 5.0, 200.0, 30.0, "mm", "Patch length (resonant dimension)"),
        ParameterDefinition("width_mm", 5.0, 200.0, 30.0, "mm", "Patch width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset from edge"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 2. U-Slot Patch
SHAPE_FAMILIES[AntennaShapeFamily.U_SLOT_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.U_SLOT_PATCH,
    display_name="U-Slot Patch",
    description="Dual-band patch antenna with U-shaped slot",
    parameters=[
        ParameterDefinition("length_mm", 10.0, 200.0, 40.0, "mm", "Patch length"),
        ParameterDefinition("width_mm", 10.0, 200.0, 40.0, "mm", "Patch width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("slot_width_mm", 1.0, 20.0, 3.0, "mm", "U-slot width"),
        ParameterDefinition("slot_depth_mm", 5.0, 50.0, 15.0, "mm", "U-slot depth"),
        ParameterDefinition("slot_offset_mm", -20.0, 20.0, 0.0, "mm", "U-slot center offset"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 3. E-Slot Patch
SHAPE_FAMILIES[AntennaShapeFamily.E_SLOT_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.E_SLOT_PATCH,
    display_name="E-Slot Patch",
    description="Wideband patch antenna with E-shaped slot",
    parameters=[
        ParameterDefinition("length_mm", 10.0, 200.0, 40.0, "mm", "Patch length"),
        ParameterDefinition("width_mm", 10.0, 200.0, 40.0, "mm", "Patch width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("left_slot_width_mm", 1.0, 15.0, 3.0, "mm", "Left slot width"),
        ParameterDefinition("right_slot_width_mm", 1.0, 15.0, 3.0, "mm", "Right slot width"),
        ParameterDefinition("center_slot_width_mm", 1.0, 15.0, 2.0, "mm", "Center slot width"),
        ParameterDefinition("slot_depth_mm", 5.0, 50.0, 15.0, "mm", "Slot depth"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 4. Inset-Feed Patch
SHAPE_FAMILIES[AntennaShapeFamily.INSET_FEED_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.INSET_FEED_PATCH,
    display_name="Inset-Feed Patch",
    description="Impedance-matched patch with inset feed line",
    parameters=[
        ParameterDefinition("length_mm", 10.0, 200.0, 35.0, "mm", "Patch length"),
        ParameterDefinition("width_mm", 10.0, 200.0, 35.0, "mm", "Patch width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("inset_depth_mm", 1.0, 30.0, 8.0, "mm", "Inset feed depth"),
        ParameterDefinition("inset_width_mm", 0.5, 10.0, 2.0, "mm", "Feed line width"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 5. Meandered Line
SHAPE_FAMILIES[AntennaShapeFamily.MEANDERED_LINE] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.MEANDERED_LINE,
    display_name="Meandered Line",
    description="Compact meandered line antenna",
    parameters=[
        ParameterDefinition("total_length_mm", 10.0, 200.0, 50.0, "mm", "Total meander length"),
        ParameterDefinition("line_width_mm", 0.5, 5.0, 1.0, "mm", "Line width"),
        ParameterDefinition("meander_segments", 2, 20, 5, "", "Number of meander segments"),
        ParameterDefinition("segment_length_mm", 5.0, 30.0, 10.0, "mm", "Length per segment"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 6. Planar Monopole - Elliptical
SHAPE_FAMILIES[AntennaShapeFamily.PLANAR_MONOPOLE_ELLIPTICAL] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.PLANAR_MONOPOLE_ELLIPTICAL,
    display_name="Elliptical Monopole",
    description="Planar elliptical monopole antenna",
    parameters=[
        ParameterDefinition("major_axis_mm", 10.0, 150.0, 40.0, "mm", "Ellipse major axis"),
        ParameterDefinition("minor_axis_mm", 5.0, 100.0, 20.0, "mm", "Ellipse minor axis"),
        ParameterDefinition("feed_width_mm", 0.5, 5.0, 2.0, "mm", "Feed line width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 7. Planar Monopole - Circular
SHAPE_FAMILIES[AntennaShapeFamily.PLANAR_MONOPOLE_CIRCULAR] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.PLANAR_MONOPOLE_CIRCULAR,
    display_name="Circular Monopole",
    description="Planar circular monopole antenna",
    parameters=[
        ParameterDefinition("radius_mm", 5.0, 100.0, 20.0, "mm", "Circle radius"),
        ParameterDefinition("feed_width_mm", 0.5, 5.0, 2.0, "mm", "Feed line width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 8. Planar Monopole - Hexagonal
SHAPE_FAMILIES[AntennaShapeFamily.PLANAR_MONOPOLE_HEXAGONAL] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.PLANAR_MONOPOLE_HEXAGONAL,
    display_name="Hexagonal Monopole",
    description="Planar hexagonal monopole antenna",
    parameters=[
        ParameterDefinition("side_length_mm", 5.0, 80.0, 20.0, "mm", "Hexagon side length"),
        ParameterDefinition("feed_width_mm", 0.5, 5.0, 2.0, "mm", "Feed line width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 9. Rounded Patch (curved corners)
SHAPE_FAMILIES[AntennaShapeFamily.ROUNDED_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.ROUNDED_PATCH,
    display_name="Rounded Patch",
    description="Rectangular patch with rounded corners for improved bandwidth",
    parameters=[
        ParameterDefinition("length_mm", 10.0, 200.0, 35.0, "mm", "Patch length"),
        ParameterDefinition("width_mm", 10.0, 200.0, 35.0, "mm", "Patch width"),
        ParameterDefinition("corner_radius_mm", 1.0, 20.0, 5.0, "mm", "Corner rounding radius"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 10. Bowtie Patch (diamond/bowtie shape)
SHAPE_FAMILIES[AntennaShapeFamily.BOWTIE_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.BOWTIE_PATCH,
    display_name="Bowtie Patch",
    description="Diamond/bowtie-shaped patch antenna for wideband operation",
    parameters=[
        ParameterDefinition("width_mm", 10.0, 200.0, 40.0, "mm", "Bowtie width (horizontal)"),
        ParameterDefinition("height_mm", 10.0, 200.0, 40.0, "mm", "Bowtie height (vertical)"),
        ParameterDefinition("apex_angle_deg", 30.0, 120.0, 60.0, "deg", "Apex angle (bowtie sharpness)"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 11. Star Patch (star-shaped polygon)
SHAPE_FAMILIES[AntennaShapeFamily.STAR_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.STAR_PATCH,
    display_name="Star Patch",
    description="Star-shaped patch antenna with multiple points",
    parameters=[
        ParameterDefinition("outer_radius_mm", 10.0, 150.0, 30.0, "mm", "Outer radius (points)"),
        ParameterDefinition("inner_radius_mm", 5.0, 100.0, 15.0, "mm", "Inner radius (indentations)"),
        ParameterDefinition("num_points", 4, 12, 5, "", "Number of star points"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 12. Ring Patch (annular ring - donut shape)
SHAPE_FAMILIES[AntennaShapeFamily.RING_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.RING_PATCH,
    display_name="Ring Patch",
    description="Annular ring patch antenna (circular with center hole)",
    parameters=[
        ParameterDefinition("outer_radius_mm", 10.0, 150.0, 30.0, "mm", "Outer ring radius"),
        ParameterDefinition("inner_radius_mm", 3.0, 50.0, 10.0, "mm", "Inner ring radius (hole)"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset from center"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 13. L-Slot Patch (L-shaped slot pattern)
SHAPE_FAMILIES[AntennaShapeFamily.L_SLOT_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.L_SLOT_PATCH,
    display_name="L-Slot Patch",
    description="Patch antenna with L-shaped slot for dual-band operation",
    parameters=[
        ParameterDefinition("length_mm", 10.0, 200.0, 40.0, "mm", "Patch length"),
        ParameterDefinition("width_mm", 10.0, 200.0, 40.0, "mm", "Patch width"),
        ParameterDefinition("slot_width_mm", 1.0, 15.0, 3.0, "mm", "L-slot width"),
        ParameterDefinition("horizontal_arm_mm", 5.0, 50.0, 15.0, "mm", "Horizontal arm length"),
        ParameterDefinition("vertical_arm_mm", 5.0, 50.0, 15.0, "mm", "Vertical arm length"),
        ParameterDefinition("slot_position_x_mm", -20.0, 20.0, 0.0, "mm", "Slot X position"),
        ParameterDefinition("slot_position_y_mm", -20.0, 20.0, 0.0, "mm", "Slot Y position"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 14. Cross-Slot Patch (cross-shaped slot)
SHAPE_FAMILIES[AntennaShapeFamily.CROSS_SLOT_PATCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.CROSS_SLOT_PATCH,
    display_name="Cross-Slot Patch",
    description="Patch antenna with cross-shaped slot for wideband operation",
    parameters=[
        ParameterDefinition("length_mm", 10.0, 200.0, 40.0, "mm", "Patch length"),
        ParameterDefinition("width_mm", 10.0, 200.0, 40.0, "mm", "Patch width"),
        ParameterDefinition("slot_width_mm", 1.0, 15.0, 3.0, "mm", "Cross-slot width"),
        ParameterDefinition("horizontal_arm_mm", 5.0, 50.0, 20.0, "mm", "Horizontal cross arm length"),
        ParameterDefinition("vertical_arm_mm", 5.0, 50.0, 20.0, "mm", "Vertical cross arm length"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 15. Fractal Koch (Koch snowflake fractal)
SHAPE_FAMILIES[AntennaShapeFamily.FRACTAL_KOCH] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.FRACTAL_KOCH,
    display_name="Koch Fractal",
    description="Koch snowflake fractal antenna for multi-band operation",
    parameters=[
        ParameterDefinition("base_length_mm", 10.0, 150.0, 40.0, "mm", "Base triangle side length"),
        ParameterDefinition("iterations", 1, 4, 2, "", "Fractal iteration level"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("feed_offset_mm", -50.0, 50.0, 0.0, "mm", "Feed point offset"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)

# 16. Curved Monopole (custom curved shape)
SHAPE_FAMILIES[AntennaShapeFamily.CURVED_MONOPOLE] = ShapeFamilyDefinition(
    family=AntennaShapeFamily.CURVED_MONOPOLE,
    display_name="Curved Monopole",
    description="Planar monopole with custom curved profile",
    parameters=[
        ParameterDefinition("width_mm", 10.0, 150.0, 40.0, "mm", "Monopole width"),
        ParameterDefinition("height_mm", 10.0, 150.0, 50.0, "mm", "Monopole height"),
        ParameterDefinition("curve_radius_mm", 5.0, 100.0, 30.0, "mm", "Curvature radius"),
        ParameterDefinition("curve_direction", -1.0, 1.0, 1.0, "", "Curve direction (1=convex, -1=concave)"),
        ParameterDefinition("feed_width_mm", 0.5, 5.0, 2.0, "mm", "Feed line width"),
        ParameterDefinition("substrate_height_mm", 0.1, 10.0, 1.6, "mm", "Substrate thickness"),
        ParameterDefinition("eps_r", 1.0, 20.0, 4.4, "", "Substrate dielectric constant"),
    ],
    auto_design_enabled=True
)


def auto_design_geometry(
    shape_family: AntennaShapeFamily,
    target_frequency_ghz: float,
    substrate_eps_r: float = 4.4,
    substrate_height_mm: float = 1.6
) -> Dict[str, float]:
    """
    Auto-design initial geometry based on target frequency.
    
    Uses analytical formulas to generate starting parameters.
    """
    c = 299792458  # Speed of light m/s
    freq_hz = target_frequency_ghz * 1e9
    wavelength_m = c / freq_hz
    wavelength_mm = wavelength_m * 1000
    
    # Effective dielectric constant
    eps_eff = (substrate_eps_r + 1) / 2 + (substrate_eps_r - 1) / 2 * (
        1 / np.sqrt(1 + 12 * substrate_height_mm / wavelength_mm)
    )
    
    params = {
        "eps_r": substrate_eps_r,
        "substrate_height_mm": substrate_height_mm,
    }
    
    if shape_family == AntennaShapeFamily.RECTANGULAR_PATCH:
        # Accurate patch design using effective length formula
        # L_eff = c / (2 * f_r * sqrt(eps_eff))
        # Accounting for fringing fields: L_eff = L + 2*ΔL
        
        # Calculate effective dielectric constant (Hammerstad & Jensen)
        u = wavelength_mm / (4 * substrate_height_mm)  # Normalized frequency
        a = 1 + (1/49) * np.log((u**4 + (u/52)**2) / (u**4 + 0.432)) + \
            (1/18.7) * np.log(1 + (u/18.1)**3)
        b = 0.564 * ((substrate_eps_r - 0.9) / (substrate_eps_r + 3))**0.053
        eps_eff = (substrate_eps_r + 1) / 2 + (substrate_eps_r - 1) / 2 * (1 + 10/u)**(-a*b)
        
        # Effective length for resonance
        L_eff = wavelength_mm / (2 * np.sqrt(eps_eff))
        
        # Fringing field extension (accurate formula)
        width_mm = wavelength_mm / (2 * np.sqrt((substrate_eps_r + 1) / 2))  # Optimal width for TM10 mode
        delta_L = 0.412 * substrate_height_mm * ((eps_eff + 0.3) * (width_mm/substrate_height_mm + 0.264)) / \
                  ((eps_eff - 0.258) * (width_mm/substrate_height_mm + 0.8))
        
        # Physical length accounting for fringing
        length_mm = L_eff - 2 * delta_L
        
        # Feed point for 50 ohm match (typically 1/3 to 1/2 from edge)
        # Using cavity model approximation
        feed_offset_mm = length_mm * 0.33  # Approximate for 50 ohm impedance
        
        params.update({
            "length_mm": max(5.0, length_mm),  # Ensure minimum size
            "width_mm": max(5.0, width_mm),
            "feed_offset_mm": feed_offset_mm,
        })
    
    elif shape_family == AntennaShapeFamily.U_SLOT_PATCH:
        # U-slot patch for dual-band operation
        # Base patch size (slightly larger due to slot loading)
        u = wavelength_mm / (4 * substrate_height_mm)
        a = 1 + (1/49) * np.log((u**4 + (u/52)**2) / (u**4 + 0.432)) + \
            (1/18.7) * np.log(1 + (u/18.1)**3)
        b = 0.564 * ((substrate_eps_r - 0.9) / (substrate_eps_r + 3))**0.053
        eps_eff = (substrate_eps_r + 1) / 2 + (substrate_eps_r - 1) / 2 * (1 + 10/u)**(-a*b)
        
        L_eff = wavelength_mm / (2 * np.sqrt(eps_eff))
        width_mm = wavelength_mm / (2 * np.sqrt((substrate_eps_r + 1) / 2))
        delta_L = 0.412 * substrate_height_mm * ((eps_eff + 0.3) * (width_mm/substrate_height_mm + 0.264)) / \
                  ((eps_eff - 0.258) * (width_mm/substrate_height_mm + 0.8))
        length_mm = L_eff - 2 * delta_L + length_mm * 0.05  # 5% compensation for slot loading
        
        # U-slot dimensions for dual-band (typically creates second resonance at ~1.8x frequency)
        slot_width_mm = length_mm * 0.10  # 10% of length (typical 2-5mm)
        slot_depth_mm = length_mm * 0.45  # 45% of length (creates dual-band resonance)
        slot_offset_mm = 0.0  # Centered for symmetric dual-band
        
        # Feed point optimized for dual-band matching
        feed_offset_mm = length_mm * 0.35
        
        params.update({
            "length_mm": max(10.0, length_mm),
            "width_mm": max(10.0, width_mm),
            "feed_offset_mm": feed_offset_mm,
            "slot_width_mm": max(1.0, slot_width_mm),
            "slot_depth_mm": max(5.0, min(50.0, slot_depth_mm)),
            "slot_offset_mm": slot_offset_mm,
        })
    
    elif shape_family == AntennaShapeFamily.E_SLOT_PATCH:
        # E-slot patch for wideband operation (typically 20-40% bandwidth improvement)
        u = wavelength_mm / (4 * substrate_height_mm)
        a = 1 + (1/49) * np.log((u**4 + (u/52)**2) / (u**4 + 0.432)) + \
            (1/18.7) * np.log(1 + (u/18.1)**3)
        b = 0.564 * ((substrate_eps_r - 0.9) / (substrate_eps_r + 3))**0.053
        eps_eff = (substrate_eps_r + 1) / 2 + (substrate_eps_r - 1) / 2 * (1 + 10/u)**(-a*b)
        
        L_eff = wavelength_mm / (2 * np.sqrt(eps_eff))
        width_mm = wavelength_mm / (2 * np.sqrt((substrate_eps_r + 1) / 2))
        delta_L = 0.412 * substrate_height_mm * ((eps_eff + 0.3) * (width_mm/substrate_height_mm + 0.264)) / \
                  ((eps_eff - 0.258) * (width_mm/substrate_height_mm + 0.8))
        length_mm = L_eff - 2 * delta_L
        
        # E-slot creates multiple resonances for wideband
        # Slot positions: left, right, and center
        slot_depth_mm = length_mm * 0.38  # Deeper slots for better bandwidth
        left_slot_width_mm = width_mm * 0.15  # Left slot width
        right_slot_width_mm = width_mm * 0.15  # Right slot width  
        center_slot_width_mm = width_mm * 0.12  # Center slot (slightly narrower)
        
        # Feed point for wideband matching
        feed_offset_mm = length_mm * 0.30
        
        params.update({
            "length_mm": max(10.0, length_mm),
            "width_mm": max(10.0, width_mm),
            "feed_offset_mm": feed_offset_mm,
            "left_slot_width_mm": max(1.0, left_slot_width_mm),
            "right_slot_width_mm": max(1.0, right_slot_width_mm),
            "center_slot_width_mm": max(1.0, center_slot_width_mm),
            "slot_depth_mm": max(5.0, min(50.0, slot_depth_mm)),
        })
    
    elif shape_family == AntennaShapeFamily.INSET_FEED_PATCH:
        # Inset-feed patch for precise impedance matching
        u = wavelength_mm / (4 * substrate_height_mm)
        a = 1 + (1/49) * np.log((u**4 + (u/52)**2) / (u**4 + 0.432)) + \
            (1/18.7) * np.log(1 + (u/18.1)**3)
        b = 0.564 * ((substrate_eps_r - 0.9) / (substrate_eps_r + 3))**0.053
        eps_eff = (substrate_eps_r + 1) / 2 + (substrate_eps_r - 1) / 2 * (1 + 10/u)**(-a*b)
        
        L_eff = wavelength_mm / (2 * np.sqrt(eps_eff))
        width_mm = wavelength_mm / (2 * np.sqrt((substrate_eps_r + 1) / 2))
        delta_L = 0.412 * substrate_height_mm * ((eps_eff + 0.3) * (width_mm/substrate_height_mm + 0.264)) / \
                  ((eps_eff - 0.258) * (width_mm/substrate_height_mm + 0.8))
        length_mm = L_eff - 2 * delta_L
        
        # Inset feed design for 50 ohm matching
        # Using transmission line model: Z_in = Z_patch * (cos^2(β*y) + j*Z_patch/Z0*sin(2β*y))
        # For 50 ohm match, typical inset depth is 0.15-0.25 * length
        inset_depth_mm = length_mm * 0.22  # Optimized for 50 ohm
        
        # Feed line width for 50 ohm (microstrip impedance formula)
        # Z0 ≈ (377/√eps_eff) * (h/W_eff) where h=substrate_height, W_eff=effective width
        # For 50 ohm: W_eff ≈ h * 377/(50*√eps_eff)
        Z0 = 50.0
        W_over_h = (377.0 / (Z0 * np.sqrt(eps_eff))) - 1  # Simplified formula
        if W_over_h > 2:
            W_over_h = (377.0 / (Z0 * np.sqrt(eps_eff)) - 2) + 1  # Correction for wide lines
        inset_width_mm = substrate_height_mm * W_over_h
        inset_width_mm = max(0.5, min(10.0, inset_width_mm))  # Practical limits
        
        params.update({
            "length_mm": max(10.0, length_mm),
            "width_mm": max(10.0, width_mm),
            "inset_depth_mm": max(1.0, min(30.0, inset_depth_mm)),
            "inset_width_mm": inset_width_mm,
        })
    
    elif shape_family == AntennaShapeFamily.MEANDERED_LINE:
        # Meandered line antenna for compact designs
        # Total length should be λ/4 in free space (or λ/4√eps_eff on substrate)
        eps_eff_meander = (substrate_eps_r + 1) / 2  # Effective for meander on substrate
        total_length_mm = wavelength_mm / (4 * np.sqrt(eps_eff_meander))
        
        # Optimal segment length (typically 0.05-0.1λ)
        segment_length_mm = wavelength_mm * 0.08  # 8% of wavelength per segment
        meander_segments = max(2, int(np.round(total_length_mm / segment_length_mm)))
        meander_segments = min(20, meander_segments)  # Practical limit
        segment_length_mm = total_length_mm / meander_segments  # Adjust to fit total length
        
        # Line width: typically 0.5-2mm, should be < λ/10 for good radiation
        line_width_mm = min(2.0, wavelength_mm / 20)  # λ/20 maximum
        line_width_mm = max(0.5, line_width_mm)  # Minimum 0.5mm for fabrication
        
        params.update({
            "total_length_mm": max(10.0, total_length_mm),
            "line_width_mm": line_width_mm,
            "meander_segments": meander_segments,
            "segment_length_mm": max(5.0, segment_length_mm),
        })
    
    elif shape_family == AntennaShapeFamily.PLANAR_MONOPOLE_ELLIPTICAL:
        # Elliptical monopole: resonant when perimeter ≈ λ/2
        # For ellipse: P ≈ π * sqrt(2 * (a² + b²)) where a=major, b=minor
        # Target perimeter for resonance: P ≈ λ/2
        target_perimeter_mm = wavelength_mm / 2
        
        # Typical aspect ratio for elliptical monopole: a/b ≈ 1.6-2.0
        aspect_ratio = 1.75
        # Solving: π * sqrt(2 * (a² + (a/1.75)²)) = λ/2
        # a² * (1 + 1/1.75²) * 2 = (λ/(2π))²
        coeff = 2 * (1 + 1 / (aspect_ratio**2))
        major_axis_mm = np.sqrt((target_perimeter_mm / np.pi)**2 / coeff)
        minor_axis_mm = major_axis_mm / aspect_ratio
        
        # Feed width for 50 ohm microstrip
        eps_eff_mono = (substrate_eps_r + 1) / 2
        Z0 = 50.0
        W_over_h = (377.0 / (Z0 * np.sqrt(eps_eff_mono))) - 1
        feed_width_mm = substrate_height_mm * W_over_h
        feed_width_mm = max(0.5, min(5.0, feed_width_mm))
        
        params.update({
            "major_axis_mm": max(10.0, major_axis_mm),
            "minor_axis_mm": max(5.0, minor_axis_mm),
            "feed_width_mm": feed_width_mm,
        })
    
    elif shape_family == AntennaShapeFamily.PLANAR_MONOPOLE_CIRCULAR:
        # Circular monopole: resonant when radius creates λ/2 perimeter
        # Perimeter = 2πr, target = λ/2
        # r = λ/(4π) ≈ 0.08λ for resonance
        # But for monopole over ground, effective radius is larger
        radius_mm = wavelength_mm / (4 * np.pi) * 1.2  # 20% larger for ground plane effect
        
        # Feed width for 50 ohm
        eps_eff_mono = (substrate_eps_r + 1) / 2
        Z0 = 50.0
        W_over_h = (377.0 / (Z0 * np.sqrt(eps_eff_mono))) - 1
        feed_width_mm = substrate_height_mm * W_over_h
        feed_width_mm = max(0.5, min(5.0, feed_width_mm))
        
        params.update({
            "radius_mm": max(5.0, radius_mm),
            "feed_width_mm": feed_width_mm,
        })
    
    elif shape_family == AntennaShapeFamily.PLANAR_MONOPOLE_HEXAGONAL:
        # Hexagonal monopole: perimeter = 6 * side_length
        # Target perimeter ≈ λ/2 for resonance
        target_perimeter_mm = wavelength_mm / 2
        side_length_mm = target_perimeter_mm / 6
        
        # Feed width for 50 ohm
        eps_eff_mono = (substrate_eps_r + 1) / 2
        Z0 = 50.0
        W_over_h = (377.0 / (Z0 * np.sqrt(eps_eff_mono))) - 1
        feed_width_mm = substrate_height_mm * W_over_h
        feed_width_mm = max(0.5, min(5.0, feed_width_mm))
        
        params.update({
            "side_length_mm": max(5.0, side_length_mm),
            "feed_width_mm": feed_width_mm,
        })
    
    # Validate and clamp to bounds
    family_def = SHAPE_FAMILIES.get(shape_family)
    if family_def:
        validated_params = {}
        for param_def in family_def.parameters:
            if param_def.name in params:
                value = params[param_def.name]
                value = max(param_def.min_value, min(param_def.max_value, value))
                validated_params[param_def.name] = value
            else:
                validated_params[param_def.name] = param_def.default_value
        return validated_params
    
    return params


def get_shape_family(family_name: str) -> Optional[ShapeFamilyDefinition]:
    """Get shape family definition by name."""
    try:
        family = AntennaShapeFamily(family_name)
        return SHAPE_FAMILIES.get(family)
    except ValueError:
        return None


def list_shape_families() -> List[Dict[str, Any]]:
    """List all available shape families."""
    return [
        {
            "family": family.value,
            "display_name": definition.display_name,
            "description": definition.description,
            "parameter_count": len(definition.parameters),
            "auto_design_enabled": definition.auto_design_enabled,
        }
        for family, definition in SHAPE_FAMILIES.items()
    ]


def validate_geometry_params(
    shape_family: str,
    params: Dict[str, float]
) -> Tuple[bool, List[str]]:
    """Validate geometry parameters for a shape family."""
    family_def = get_shape_family(shape_family)
    if not family_def:
        return False, [f"Unknown shape family: {shape_family}"]
    
    return family_def.validate_parameters(params)

