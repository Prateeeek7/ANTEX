"""
Industry-standard material library for RF and antenna design.

Contains dielectric properties, loss tangents, and thermal properties
for commonly used substrate materials.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MaterialProperties:
    """Material properties for RF substrate."""
    name: str
    eps_r: float  # Relative permittivity (dielectric constant)
    loss_tan: float  # Loss tangent (tan δ)
    conductivity_s_m: Optional[float] = None  # Conductivity in S/m (for conductors)
    thickness_mm: Optional[float] = None  # Typical thickness in mm
    cost_tier: str = "standard"  # "budget", "standard", "premium"
    application: str = ""  # Application notes


# Industry-standard material database
MATERIAL_LIBRARY: Dict[str, MaterialProperties] = {
    # FR4 family (PCB substrates)
    "FR4": MaterialProperties(
        name="FR4",
        eps_r=4.4,
        loss_tan=0.02,
        thickness_mm=1.6,
        cost_tier="budget",
        application="General purpose PCB, cost-effective, moderate loss"
    ),
    "FR4_High_Tg": MaterialProperties(
        name="FR4 High Tg",
        eps_r=4.5,
        loss_tan=0.018,
        thickness_mm=1.6,
        cost_tier="standard",
        application="High temperature applications, improved stability"
    ),
    
    # Rogers Corporation materials (industry standard for RF)
    "RO4003C": MaterialProperties(
        name="Rogers RO4003C",
        eps_r=3.38,
        loss_tan=0.0027,
        thickness_mm=1.524,
        cost_tier="premium",
        application="High-performance RF, excellent for antennas, low loss"
    ),
    "RO4350B": MaterialProperties(
        name="Rogers RO4350B",
        eps_r=3.48,
        loss_tan=0.0037,
        thickness_mm=1.524,
        cost_tier="premium",
        application="High-frequency applications, automotive radar, 5G"
    ),
    "RO5880": MaterialProperties(
        name="Rogers RO5880",
        eps_r=2.2,
        loss_tan=0.0009,
        thickness_mm=0.787,
        cost_tier="premium",
        application="Ultra-low loss, aerospace, satellite communications"
    ),
    "RO3003": MaterialProperties(
        name="Rogers RO3003",
        eps_r=3.0,
        loss_tan=0.0013,
        thickness_mm=1.524,
        cost_tier="premium",
        application="Low loss, stable with temperature"
    ),
    "RO3010": MaterialProperties(
        name="Rogers RO3010",
        eps_r=10.2,
        loss_tan=0.0022,
        thickness_mm=1.27,
        cost_tier="premium",
        application="High permittivity for miniaturization, filters"
    ),
    
    # Taconic materials
    "TLX-8": MaterialProperties(
        name="Taconic TLX-8",
        eps_r=2.55,
        loss_tan=0.0019,
        thickness_mm=1.575,
        cost_tier="premium",
        application="Low loss, high frequency applications"
    ),
    "TLY-5": MaterialProperties(
        name="Taconic TLY-5",
        eps_r=2.2,
        loss_tan=0.0009,
        thickness_mm=0.787,
        cost_tier="premium",
        application="Ultra-low loss, millimeter-wave"
    ),
    
    # Arlon materials
    "AD250C": MaterialProperties(
        name="Arlon AD250C",
        eps_r=2.5,
        loss_tan=0.0014,
        thickness_mm=1.524,
        cost_tier="premium",
        application="Low loss, stable performance"
    ),
    
    # Polyimide
    "Polyimide": MaterialProperties(
        name="Polyimide (Kapton)",
        eps_r=3.5,
        loss_tan=0.002,
        thickness_mm=0.05,
        cost_tier="standard",
        application="Flexible substrates, thin film applications"
    ),
    
    # Air (reference)
    "Air": MaterialProperties(
        name="Air",
        eps_r=1.0,
        loss_tan=0.0,
        cost_tier="budget",
        application="Free space, reference medium"
    ),
    
    # Conductive materials
    "Copper": MaterialProperties(
        name="Copper",
        eps_r=1.0,
        loss_tan=0.0,
        conductivity_s_m=5.96e7,
        cost_tier="standard",
        application="Standard conductor for traces and patches"
    ),
    "Gold": MaterialProperties(
        name="Gold",
        eps_r=1.0,
        loss_tan=0.0,
        conductivity_s_m=4.1e7,
        cost_tier="premium",
        application="High reliability, low oxidation, wire bonding"
    ),
    "Silver": MaterialProperties(
        name="Silver",
        eps_r=1.0,
        loss_tan=0.0,
        conductivity_s_m=6.3e7,
        cost_tier="premium",
        application="Highest conductivity, RF connectors"
    ),
    "Aluminum": MaterialProperties(
        name="Aluminum",
        eps_r=1.0,
        loss_tan=0.0,
        conductivity_s_m=3.5e7,
        cost_tier="standard",
        application="Lightweight structures, cost-effective"
    ),
}


def get_material(name: str) -> Optional[MaterialProperties]:
    """Get material properties by name."""
    return MATERIAL_LIBRARY.get(name)


def list_materials(category: Optional[str] = None) -> Dict[str, MaterialProperties]:
    """
    List all materials, optionally filtered by category.
    
    Categories: "substrate", "conductor", "all"
    """
    if category == "substrate":
        return {k: v for k, v in MATERIAL_LIBRARY.items() if v.conductivity_s_m is None}
    elif category == "conductor":
        return {k: v for k, v in MATERIAL_LIBRARY.items() if v.conductivity_s_m is not None}
    else:
        return MATERIAL_LIBRARY.copy()


def get_effective_permittivity(
    material: MaterialProperties,
    width_mm: float,
    height_mm: float
) -> float:
    """
    Calculate effective permittivity for microstrip transmission line.
    
    Uses Wheeler's formula for microstrip:
    eps_eff = (eps_r + 1)/2 + (eps_r - 1)/2 * F(w/h)
    """
    if material.eps_r == 1.0:  # Air or conductor
        return 1.0
    
    w_h_ratio = width_mm / height_mm if height_mm > 0 else 1.0
    
    # Wheeler's formula
    if w_h_ratio < 1.0:
        # Narrow strip
        F = (1 + 12 / w_h_ratio) ** (-0.5) + 0.04 * (1 - w_h_ratio) ** 2
    else:
        # Wide strip
        F = (1 + 12 / w_h_ratio) ** (-0.5)
    
    eps_eff = (material.eps_r + 1) / 2 + (material.eps_r - 1) / 2 * F
    return eps_eff


def estimate_substrate_loss(
    material: MaterialProperties,
    frequency_ghz: float
) -> float:
    """
    Estimate substrate loss in dB/mm.
    
    Loss = 8.686 * pi * f * sqrt(eps_r) * tan(delta) / c
    """
    c = 299792458.0  # Speed of light in m/s
    f_hz = frequency_ghz * 1e9
    loss_db_per_m = 8.686 * 3.14159 * f_hz * (material.eps_r ** 0.5) * material.loss_tan / c
    loss_db_per_mm = loss_db_per_m / 1000.0
    return loss_db_per_mm




