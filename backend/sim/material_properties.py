"""
Material properties database for substrate materials.
Provides permittivity (εr), loss tangent (tan δ), and other properties.
"""
from typing import Dict, Optional

# Material properties database
# Values are typical at 2.4 GHz, may vary with frequency
MATERIAL_PROPERTIES: Dict[str, Dict[str, float]] = {
    "FR4": {
        "permittivity": 4.4,
        "loss_tangent": 0.02,
        "conductivity_s_per_m": 5.8e7,  # Copper
    },
    "Rogers RO4003": {
        "permittivity": 3.38,
        "loss_tangent": 0.0027,
        "conductivity_s_per_m": 5.8e7,
    },
    "Rogers RT/duroid 5880": {
        "permittivity": 2.2,
        "loss_tangent": 0.0009,
        "conductivity_s_per_m": 5.8e7,
    },
    "Rogers RT/duroid 6002": {
        "permittivity": 2.94,
        "loss_tangent": 0.0012,
        "conductivity_s_per_m": 5.8e7,
    },
    "Custom": {
        "permittivity": 4.4,  # Default to FR4
        "loss_tangent": 0.02,
        "conductivity_s_per_m": 5.8e7,
    },
}


def get_substrate_properties(substrate_name: str) -> Dict[str, float]:
    """
    Get material properties for a substrate material.
    
    Args:
        substrate_name: Name of the substrate material
        
    Returns:
        Dictionary with permittivity, loss_tangent, and conductivity
    """
    return MATERIAL_PROPERTIES.get(substrate_name, MATERIAL_PROPERTIES["FR4"])


def get_effective_permittivity(
    eps_r: float,
    substrate_thickness_mm: float,
    trace_width_mm: float
) -> float:
    """
    Calculate effective permittivity for microstrip line.
    
    Uses Hammerstad and Jensen formula for microstrip effective permittivity.
    
    Args:
        eps_r: Substrate relative permittivity
        substrate_thickness_mm: Substrate thickness in mm
        trace_width_mm: Trace width in mm
        
    Returns:
        Effective permittivity
    """
    h = substrate_thickness_mm
    w = trace_width_mm
    
    if w / h < 1:
        # Narrow microstrip
        eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (
            (1 + 12 * h / w) ** (-0.5) + 0.04 * (1 - w / h) ** 2
        )
    else:
        # Wide microstrip
        eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * h / w) ** (-0.5)
    
    return eps_eff


def calculate_skin_depth(frequency_hz: float, conductivity_s_per_m: float) -> float:
    """
    Calculate skin depth for conductor losses.
    
    Args:
        frequency_hz: Frequency in Hz
        conductivity_s_per_m: Conductivity in S/m (Siemens per meter)
        
    Returns:
        Skin depth in meters
    """
    import math
    mu_0 = 4 * math.pi * 1e-7  # Permeability of free space
    omega = 2 * math.pi * frequency_hz
    delta = math.sqrt(2 / (omega * mu_0 * conductivity_s_per_m))
    return delta


def calculate_conductor_loss(
    frequency_hz: float,
    trace_width_mm: float,
    trace_length_mm: float,
    conductor_thickness_um: float,
    conductivity_s_per_m: float = 5.8e7
) -> float:
    """
    Calculate conductor losses in dB.
    
    Uses skin effect and surface roughness models.
    
    Args:
        frequency_hz: Frequency in Hz
        trace_width_mm: Trace width in mm
        trace_length_mm: Trace length in mm
        conductor_thickness_um: Conductor thickness in micrometers
        conductivity_s_per_m: Conductivity (default: copper)
        
    Returns:
        Loss in dB
    """
    import math
    
    # Skin depth
    delta = calculate_skin_depth(frequency_hz, conductivity_s_per_m)
    delta_um = delta * 1e6  # Convert to micrometers
    
    # Effective conductor thickness (accounting for skin effect)
    if conductor_thickness_um > 2 * delta_um:
        # Thick conductor - skin effect dominates
        effective_thickness = delta_um
    else:
        # Thin conductor - use actual thickness
        effective_thickness = conductor_thickness_um
    
    # Surface resistance (ohms per square)
    R_s = 1 / (conductivity_s_per_m * effective_thickness * 1e-6)
    
    # Loss calculation (simplified)
    # For microstrip: α_c ≈ R_s / (Z_0 * w)
    # Approximate Z_0 for microstrip (simplified)
    w_m = trace_width_mm * 1e-3
    Z_0_approx = 50.0  # Simplified - would need full microstrip calculation
    
    # Loss per unit length (Np/m)
    alpha_c = R_s / (Z_0_approx * w_m)
    
    # Total loss in dB
    length_m = trace_length_mm * 1e-3
    loss_db = 8.686 * alpha_c * length_m  # Convert Np to dB
    
    return loss_db


def calculate_dielectric_loss(
    frequency_hz: float,
    loss_tangent: float,
    eps_r: float,
    substrate_thickness_mm: float,
    trace_length_mm: float
) -> float:
    """
    Calculate dielectric losses in dB.
    
    Args:
        frequency_hz: Frequency in Hz
        loss_tangent: Substrate loss tangent
        eps_r: Substrate permittivity
        substrate_thickness_mm: Substrate thickness in mm
        trace_length_mm: Trace length in mm
        
    Returns:
        Loss in dB
    """
    import math
    
    # Dielectric loss per unit length (Np/m)
    # For microstrip: α_d ≈ (π * f * sqrt(eps_eff) * tan(δ)) / c
    c = 299792458  # Speed of light
    eps_eff = get_effective_permittivity(eps_r, substrate_thickness_mm, 2.0)  # Approximate width
    
    alpha_d = (math.pi * frequency_hz * math.sqrt(eps_eff) * loss_tangent) / c
    
    # Total loss in dB
    length_m = trace_length_mm * 1e-3
    loss_db = 8.686 * alpha_d * length_m  # Convert Np to dB
    
    return loss_db



