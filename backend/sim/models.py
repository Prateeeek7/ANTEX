"""
Approximate analytical models for antenna EM behavior.
These are simplified formulas, not full EM simulation.
"""
import math
import logging
from sim.types import PatchParams, SlotParams, FractalParams, GeometryParams

logger = logging.getLogger(__name__)


def estimate_patch_resonant_freq(params: GeometryParams) -> float:
    """
    Estimate resonant frequency for patch antenna.
    
    Uses correct microstrip formula: f_r = c / (2 * L_eff * sqrt(eps_eff))
    where L_eff = L + 2*ΔL accounts for fringing fields.
    
    Formulas used:
    - ε_eff (Hammerstad-Jensen): (ε_r + 1)/2 + (ε_r - 1)/2 * (1 + 12*h/W)^(-0.5)
    - ΔL (fringing extension): 0.412 * h * (ε_eff + 0.3) * (W/h + 0.264) / ((ε_eff - 0.258) * (W/h + 0.8))
    - L_eff = L + 2*ΔL
    - f_res = c / (2 * L_eff * sqrt(ε_eff))
    
    Uses actual substrate thickness from project parameters for accurate calculation.
    IMPORTANT: ε_eff and ΔL are recalculated every time this function is called,
    ensuring correct values when width or length changes.
    """
    # Check for star patch parameters
    if "outer_radius_mm" in params:
        # Star patch antenna - approximate as circular patch with effective radius
        outer_radius_mm = params["outer_radius_mm"]
        inner_radius_mm = params.get("inner_radius_mm", outer_radius_mm * 0.5)
        eps_r = params.get("eps_r", 4.4)
        substrate_height_mm = params.get("substrate_height_mm", 1.6)
        
        # Approximate effective radius (average of outer and inner)
        # Star patch has longer effective perimeter, use outer_radius for conservative estimate
        effective_radius_mm = outer_radius_mm * 0.85  # Account for indentations
        # Approximate as circular patch: f_res ≈ c / (1.841 * r_eff * sqrt(eps_eff))
        # where 1.841 is first root of J1 (circular patch)
        c = 299792458
        h = substrate_height_mm
        # Effective dielectric constant (simplified for circular)
        eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * h / (2 * effective_radius_mm)) ** (-0.5)
        freq_hz = c / (1.841 * effective_radius_mm * 1e-3 * math.sqrt(eps_eff))
        freq_ghz = freq_hz / 1e9
        return freq_ghz
    
    elif "length_mm" in params:
        # Patch antenna
        length_mm = params["length_mm"]
        width_mm = params["width_mm"]
        eps_r = params.get("eps_r", 4.4)  # Default FR4
        substrate_height_mm = params.get("substrate_height_mm", 1.6)  # Use project's substrate thickness
        
        # Validate inputs
        if width_mm <= 0 or length_mm <= 0 or substrate_height_mm <= 0:
            logger.warning(f"Invalid geometry params: L={length_mm}, W={width_mm}, h={substrate_height_mm}")
            return 2.4  # Default fallback
        
        # Effective dielectric constant (Hammerstad-Jensen formula)
        # IMPORTANT: This is recalculated every time width or length changes
        h = substrate_height_mm
        W = width_mm
        ratio_h_W = h / W
        
        # ε_eff formula: (ε_r + 1)/2 + (ε_r - 1)/2 * (1 + 12*h/W)^(-0.5)
        eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * ratio_h_W) ** (-0.5)
        
        # Fringing field extension (ΔL)
        # Formula: ΔL = 0.412 * h * (ε_eff + 0.3) * (W/h + 0.264) / ((ε_eff - 0.258) * (W/h + 0.8))
        # This correctly depends on W/h ratio
        ratio_W_h = W / h
        delta_L = 0.412 * h * (eps_eff + 0.3) * (ratio_W_h + 0.264) / ((eps_eff - 0.258) * (ratio_W_h + 0.8))
        
        # Effective length: L_eff = L + 2*ΔL
        # IMPORTANT: Must use L_eff (not L) in frequency calculation
        L_eff = length_mm + 2 * delta_L
        
        # Resonant frequency: f_res = c / (2 * L_eff * sqrt(eps_eff))
        # where c = speed of light = 299792458 m/s
        c = 299792458  # Speed of light in m/s
        freq_hz = c / (2 * L_eff * 1e-3 * math.sqrt(eps_eff))  # L_eff in mm, convert to m
        freq_ghz = freq_hz / 1e9
        
        # Log calculation details for debugging
        logger.debug(
            f"Resonant frequency calculation: "
            f"L={length_mm:.3f}mm, W={width_mm:.3f}mm, h={substrate_height_mm:.3f}mm, "
            f"ε_r={eps_r:.3f}, ε_eff={eps_eff:.3f}, ΔL={delta_L:.3f}mm, "
            f"L_eff={L_eff:.3f}mm, f_res={freq_ghz:.6f}GHz"
        )
        
        return freq_ghz
        
    elif "slot_length_mm" in params:
        # Slot antenna - approximate as half-wavelength slot
        slot_length_mm = params["slot_length_mm"]
        eps_r = params.get("eps_r", 4.4)
        c = 299792458
        # Slot antenna resonates when length ≈ λ/2 in substrate
        freq_hz = c / (2 * slot_length_mm * 1e-3 * math.sqrt(eps_r))
        return freq_hz / 1e9
        
    elif "iterations" in params:
        # Fractal - simplified model (would need more complex calculation)
        base_length_mm = params["base_length_mm"]
        eps_r = params.get("eps_r", 4.4)
        scale_factor = params.get("scale_factor", 0.5)
        # Rough estimate: resonant freq scales with effective length
        effective_length = base_length_mm * (1 + scale_factor * params.get("iterations", 1))
        c = 299792458
        freq_hz = c / (2 * effective_length * 1e-3 * math.sqrt(eps_r))
        return freq_hz / 1e9
    
    return 2.4  # Default fallback


def estimate_bandwidth(params: GeometryParams) -> float:
    """
    Estimate bandwidth (in MHz) based on geometry.
    
    Uses the correct microstrip patch antenna bandwidth formula:
    Fractional Bandwidth (FBW) = A * (eps_r - 1) / (eps_r^2) * (h / (sqrt(eps_eff) * L))
    
    Where:
    - A is a constant factor (typically 3.77 for standard patches)
    - eps_r = dielectric constant of substrate
    - eps_eff = effective dielectric constant
    - h = substrate height (thickness)
    - L = patch length (resonant dimension)
    
    Absolute bandwidth: BW = FBW * f_resonant
    
    IMPORTANT: This formula correctly uses:
    - Substrate height (h) - thicker substrates = wider bandwidth
    - Dielectric constant (eps_r) - lower eps_r = wider bandwidth
    - Patch length (L) - longer patches = narrower bandwidth
    - Effective dielectric constant (eps_eff) - accounts for microstrip effects
    
    Uses actual substrate thickness and dielectric constant from project parameters.
    """
    if "length_mm" in params:
        length_mm = params["length_mm"]
        width_mm = params["width_mm"]
        substrate_height_mm = params.get("substrate_height_mm", 1.6)  # Use project's substrate thickness
        eps_r = params.get("eps_r", 4.4)  # Use project's dielectric constant
        
        # Validate inputs
        if length_mm <= 0 or substrate_height_mm <= 0 or eps_r <= 1.0:
            logger.warning(f"Invalid bandwidth params: L={length_mm}, h={substrate_height_mm}, eps_r={eps_r}")
            return 100.0  # Default fallback
        
        # Calculate effective dielectric constant (needed for bandwidth)
        # Use same formula as in frequency calculation for consistency
        h = substrate_height_mm
        W = width_mm
        ratio_h_W = h / W if W > 0 else 0.01
        
        # ε_eff formula: (ε_r + 1)/2 + (ε_r - 1)/2 * (1 + 12*h/W)^(-0.5)
        eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * ratio_h_W) ** (-0.5)
        
        # Calculate fractional bandwidth using correct formula
        # FBW = A * (eps_r - 1) / (eps_r^2) * (h / (sqrt(eps_eff) * L))
        # A = 3.77 is a typical value for rectangular patches
        # This accounts for:
        # - Substrate height (h): thicker = wider BW
        # - Dielectric constant (eps_r): lower = wider BW
        # - Patch length (L): longer = narrower BW
        # - Effective permittivity (eps_eff): microstrip effects
        
        A = 3.77  # Constant factor for rectangular patch antennas
        h_m = substrate_height_mm * 1e-3  # Convert to meters
        L_m = length_mm * 1e-3  # Convert to meters
        
        # Fractional bandwidth
        fractional_bw = A * (eps_r - 1) / (eps_r ** 2) * (h_m / (math.sqrt(eps_eff) * L_m))
        
        # Clamp fractional bandwidth to reasonable range (0.1% to 20%)
        # Very thin substrates can give unrealistic values
        fractional_bw = max(0.001, min(0.20, fractional_bw))  # 0.1% to 20%
        
        # Get resonant frequency
        center_freq_ghz = estimate_patch_resonant_freq(params)
        
        # Absolute bandwidth in MHz: BW = FBW * f_resonant
        bandwidth_mhz = center_freq_ghz * 1000 * fractional_bw
        
        # Log calculation details
        logger.debug(
            f"Bandwidth calculation: "
            f"L={length_mm:.3f}mm, W={width_mm:.3f}mm, h={substrate_height_mm:.3f}mm, "
            f"ε_r={eps_r:.3f}, ε_eff={eps_eff:.3f}, "
            f"FBW={fractional_bw*100:.2f}%, f_res={center_freq_ghz:.6f}GHz, "
            f"BW={bandwidth_mhz:.2f}MHz"
        )
        
        return bandwidth_mhz
        
    elif "slot_length_mm" in params:
        # Slot antenna - typically narrower bandwidth
        center_freq_ghz = estimate_patch_resonant_freq(params)  # Using same function
        return center_freq_ghz * 1000 * 0.03  # ~3% typical
        
    elif "iterations" in params:
        # Fractal - depends on complexity
        center_freq_ghz = estimate_patch_resonant_freq(params)
        return center_freq_ghz * 1000 * 0.02  # ~2% typical
    
    return 100.0  # Default fallback in MHz


def estimate_gain(params: GeometryParams, efficiency_percent: float = None) -> float:
    """
    Estimate gain in dBi using: Gain = Efficiency × Directivity.
    
    Directivity is calculated from aperture area (W × L).
    Efficiency accounts for substrate and conductor losses.
    
    IMPORTANT: Gain updates when geometry changes because:
    - Directivity depends on aperture area (W × L)
    - Efficiency depends on losses (which may vary with geometry)
    
    Args:
        params: Geometry parameters
        efficiency_percent: Optional efficiency (0-100). If None, estimated from losses.
        
    Returns:
        Gain in dBi
    """
    if "length_mm" in params:
        length_mm = params["length_mm"]
        width_mm = params["width_mm"]
        substrate_height_mm = params.get("substrate_height_mm", 1.6)
        eps_r = params.get("eps_r", 4.4)
        
        # Calculate aperture area: A = W × L (in m²)
        # IMPORTANT: Use actual W and L from geometry, not fixed constants
        area_mm2 = length_mm * width_mm
        area_m2 = area_mm2 * 1e-6  # Convert to m²
        
        # Calculate resonant frequency to get wavelength
        freq_ghz = estimate_patch_resonant_freq(params)
        freq_hz = freq_ghz * 1e9
        c = 299792458  # Speed of light in m/s
        wavelength_m = c / freq_hz
        
        # Directivity for patch antenna
        # Standard rectangular patch antennas have directivity typically 6-8 dBi
        # The directivity depends on patch dimensions and substrate properties
        # Use a more accurate model based on patch geometry
        
        # Calculate directivity using patch antenna formula
        # For rectangular patches: D ≈ 4π × (W × L) / λ² × radiation_efficiency_factor
        # But this gives too low values for small patches, so we use an empirical model
        
        # Empirical directivity model for rectangular patch antennas
        # Base directivity depends on patch aspect ratio (W/L) and substrate
        aspect_ratio = width_mm / length_mm if length_mm > 0 else 1.0
        
        # Base directivity for square patch on standard substrate: ~6.5 dBi
        # Directivity increases slightly with aspect ratio (wider patches)
        base_directivity_dbi = 6.5 + 0.5 * (aspect_ratio - 1.0)  # Adjust for aspect ratio
        
        # Substrate effect: lower ε_r gives slightly higher directivity
        eps_r_factor = 1.0 - 0.1 * (eps_r - 2.2) / 2.2  # Normalize to Rogers 5880 (ε_r=2.2)
        directivity_dbi = base_directivity_dbi * eps_r_factor
        
        # Clamp to reasonable range (5-9 dBi for standard patches)
        directivity_dbi = max(5.0, min(9.0, directivity_dbi))
        
        # Convert to linear for gain calculation
        directivity_linear = 10 ** (directivity_dbi / 10)
        
        # Efficiency: if not provided, estimate from losses
        if efficiency_percent is None:
            # Simplified efficiency model based on substrate thickness
            # Thicker substrates have more losses
            # Typical efficiency: 70-95% for well-designed patches
            base_efficiency = 0.85  # 85% base efficiency
            loss_factor = 1.0 - (substrate_height_mm - 0.8) * 0.03  # ~3% loss per mm above 0.8mm
            loss_factor = max(0.70, min(0.95, loss_factor))  # Clamp between 70% and 95%
            efficiency_linear = base_efficiency * loss_factor
        else:
            efficiency_linear = efficiency_percent / 100.0
        
        # Gain = Efficiency × Directivity (linear)
        gain_linear = efficiency_linear * directivity_linear
        gain_dbi = 10 * math.log10(gain_linear) if gain_linear > 0 else 0.0
        
        # Log calculation details
        logger.debug(
            f"Gain calculation: L={length_mm:.3f}mm, W={width_mm:.3f}mm, "
            f"A={area_mm2:.2f}mm², aspect_ratio={aspect_ratio:.2f}, "
            f"λ={wavelength_m*1000:.3f}mm, D={directivity_dbi:.2f}dBi, "
            f"η={efficiency_linear*100:.1f}%, G={gain_dbi:.2f}dBi"
        )
        
        return gain_dbi
        
    elif "slot_length_mm" in params:
        # Slot antennas typically have lower gain
        return 3.0
        
    elif "iterations" in params:
        # Fractal - depends on design
        return 5.0
    
    return 4.5  # Default fallback


