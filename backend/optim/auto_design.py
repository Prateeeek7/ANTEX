"""
Auto-design functions to generate initial geometry parameters based on target frequency.
"""
import math
import logging
from typing import Dict, Any, Optional
from sim.material_properties import get_substrate_properties

logger = logging.getLogger(__name__)


def estimate_initial_patch_dimensions(
    target_frequency_ghz: float,
    substrate: str = "FR4",
    substrate_thickness_mm: float = 1.6,
    max_size_mm: Optional[float] = None
) -> Dict[str, float]:
    """
    Estimate initial patch antenna dimensions (L, W) based on target frequency.
    
    Uses the microstrip patch formula:
    f_res ≈ c / (2 * L_eff * sqrt(eps_eff))
    
    Where L_eff = L + 2*ΔL accounts for fringing fields.
    
    This provides a good starting point for optimization.
    
    Args:
        target_frequency_ghz: Target resonant frequency in GHz
        substrate: Substrate material name
        substrate_thickness_mm: Substrate thickness in mm
        max_size_mm: Maximum allowed size (constraint)
        
    Returns:
        Dict with estimated length_mm, width_mm, and other parameters
    """
    # Get material properties
    material_props = get_substrate_properties(substrate)
    eps_r = material_props["permittivity"]
    
    # Speed of light
    c = 299792458  # m/s
    
    # Initial estimate: assume L ≈ λ/2 in substrate
    # f = c / (2 * L * sqrt(eps_r))
    # L ≈ c / (2 * f * sqrt(eps_r))
    freq_hz = target_frequency_ghz * 1e9
    wavelength_m = c / freq_hz
    wavelength_mm = wavelength_m * 1000
    
    # Initial length estimate (without fringing correction)
    L_initial_mm = wavelength_mm / (2 * math.sqrt(eps_r))
    
    # Account for fringing fields (iterative refinement)
    # We need to solve: f_res = c / (2 * (L + 2*ΔL) * sqrt(eps_eff))
    # Start with L_initial, calculate ΔL, adjust L, repeat
    
    L_est = L_initial_mm
    W_est = L_est * 1.2  # Typical aspect ratio: W ≈ 1.2 * L
    
    # Iterate to refine estimate (accounting for fringing)
    for _ in range(5):  # 5 iterations should be enough
        h = substrate_thickness_mm
        W = W_est
        ratio_h_W = h / W if W > 0 else 0.01
        
        # Effective dielectric constant
        eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * ratio_h_W) ** (-0.5)
        
        # Fringing field extension
        ratio_W_h = W / h
        delta_L = 0.412 * h * (eps_eff + 0.3) * (ratio_W_h + 0.264) / ((eps_eff - 0.258) * (ratio_W_h + 0.8))
        
        # Effective length
        L_eff = L_est + 2 * delta_L
        
        # Calculate frequency with this geometry
        freq_calc_hz = c / (2 * L_eff * 1e-3 * math.sqrt(eps_eff))
        freq_calc_ghz = freq_calc_hz / 1e9
        
        # Adjust L to match target frequency
        L_est = L_est * (target_frequency_ghz / freq_calc_ghz)
        W_est = L_est * 1.2  # Maintain aspect ratio
        
        # Check convergence
        if abs(freq_calc_ghz - target_frequency_ghz) / target_frequency_ghz < 0.01:
            break
    
    # Apply max_size constraint
    if max_size_mm:
        L_est = min(L_est, max_size_mm)
        W_est = min(W_est, max_size_mm)
    
    # Ensure reasonable minimum size
    L_est = max(5.0, L_est)
    W_est = max(5.0, W_est)
    
    logger.info(
        f"Auto-design: target_f={target_frequency_ghz:.3f}GHz, "
        f"substrate={substrate} (ε_r={eps_r:.2f}), h={substrate_thickness_mm}mm, "
        f"estimated L={L_est:.2f}mm, W={W_est:.2f}mm"
    )
    
    return {
        "length_mm": L_est,
        "width_mm": W_est,
        "substrate_height_mm": substrate_thickness_mm,
        "eps_r": eps_r,
        "feed_offset_mm": 0.0,  # Start at center
    }


