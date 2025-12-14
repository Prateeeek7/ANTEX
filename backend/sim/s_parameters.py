"""
S-Parameter analysis for RF antenna design.

Provides tools for:
- S-parameter computation from impedance
- Smith chart transformations
- Impedance matching
- Touchstone file export/import
"""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import skrf as rf
    SKRF_AVAILABLE = True
except ImportError:
    SKRF_AVAILABLE = False
    logger.warning("scikit-rf not available. S-parameter features will be limited.")


# Characteristic impedance (typically 50 ohms for RF systems)
Z0 = 50.0  # Reference impedance in ohms


def impedance_to_s11(z: complex, z0: float = Z0) -> complex:
    """
    Convert impedance to S11 (reflection coefficient).
    
    S11 = (Z - Z0) / (Z + Z0)
    
    Args:
        z: Complex impedance (R + jX)
        z0: Reference impedance (default 50 ohms)
        
    Returns:
        Complex S11 parameter
    """
    return (z - z0) / (z + z0)


def s11_to_impedance(s11: complex, z0: float = Z0) -> complex:
    """
    Convert S11 to impedance.
    
    Z = Z0 * (1 + S11) / (1 - S11)
    
    Args:
        s11: Complex S11 parameter
        z0: Reference impedance (default 50 ohms)
        
    Returns:
        Complex impedance (R + jX)
    """
    if abs(s11) >= 1.0:
        return complex(float('inf'), 0)  # Open circuit
    
    return z0 * (1 + s11) / (1 - s11)


def s11_to_vswr(s11: complex) -> float:
    """
    Calculate VSWR (Voltage Standing Wave Ratio) from S11.
    
    VSWR = (1 + |S11|) / (1 - |S11|)
    
    Args:
        s11: Complex S11 parameter
        
    Returns:
        VSWR (always >= 1.0)
    """
    mag_s11 = abs(s11)
    if mag_s11 >= 1.0:
        return float('inf')
    return (1 + mag_s11) / (1 - mag_s11)


def s11_to_return_loss_db(s11: complex) -> float:
    """
    Calculate return loss in dB from S11.
    
    This function returns S11 magnitude in dB (negative value), which is commonly
    referred to as "return loss" in many RF engineering contexts.
    
    Return Loss (dB) = 20 * log10(|S11|)
    
    For a good match:
    - |S11| < 0.316 (VSWR < 2.0) → Return Loss < -10 dB
    - |S11| < 0.1 (VSWR < 1.22) → Return Loss < -20 dB
    
    Args:
        s11: Complex S11 parameter
        
    Returns:
        Return loss in dB (negative value, representing S11 magnitude in dB)
    """
    mag_s11 = abs(s11)
    if mag_s11 <= 0:
        return float('-inf')
    # Return S11 magnitude in dB (negative value)
    # Better match = more negative (closer to -infinity)
    # Poor match = less negative (closer to 0)
    return 20 * np.log10(mag_s11)


def smith_to_rectangular(gamma: complex) -> Tuple[float, float]:
    """
    Convert Smith chart coordinates (reflection coefficient) to rectangular coordinates.
    
    Args:
        gamma: Complex reflection coefficient
        
    Returns:
        (x, y) coordinates on Smith chart
    """
    real = gamma.real
    imag = gamma.imag
    return (real, imag)


def rectangular_to_smith(x: float, y: float) -> complex:
    """
    Convert rectangular coordinates to Smith chart (reflection coefficient).
    
    Args:
        x, y: Rectangular coordinates
        
    Returns:
        Complex reflection coefficient
    """
    return complex(x, y)


def calculate_matching_network_l(
    z_load: complex,
    frequency_ghz: float,
    z0: float = Z0
) -> Dict[str, Any]:
    """
    Calculate L-section matching network for impedance matching.
    
    Returns both possible configurations (series L-shunt C and series C-shunt L).
    
    Args:
        z_load: Load impedance (R + jX)
        frequency_ghz: Frequency in GHz
        z0: Source impedance (default 50 ohms)
        
    Returns:
        Dictionary with matching network parameters
    """
    freq_hz = frequency_ghz * 1e9
    omega = 2 * np.pi * freq_hz
    
    r_load = z_load.real
    x_load = z_load.imag
    
    solutions = []
    
    # Case 1: Series inductor, shunt capacitor (when R_load < Z0)
    if r_load < z0:
        q = np.sqrt(z0 / r_load - 1)
        x_series = x_load + q * r_load
        x_shunt = -z0 / q
        
        if x_series > 0:  # Inductor
            l_series_nh = x_series / omega * 1e9
            c_shunt_pf = -1 / (x_shunt * omega) * 1e12
            
            solutions.append({
                "type": "L-C",
                "series_inductor_nh": l_series_nh,
                "shunt_capacitor_pf": c_shunt_pf,
                "description": f"Series {l_series_nh:.2f} nH inductor, Shunt {c_shunt_pf:.2f} pF capacitor"
            })
    
    # Case 2: Series capacitor, shunt inductor (when R_load < Z0)
    if r_load < z0:
        q = np.sqrt(z0 / r_load - 1)
        x_series = x_load - q * r_load
        x_shunt = z0 / q
        
        if x_series < 0:  # Capacitor
            c_series_pf = -1 / (x_series * omega) * 1e12
            l_shunt_nh = x_shunt / omega * 1e9
            
            solutions.append({
                "type": "C-L",
                "series_capacitor_pf": c_series_pf,
                "shunt_inductor_nh": l_shunt_nh,
                "description": f"Series {c_series_pf:.2f} pF capacitor, Shunt {l_shunt_nh:.2f} nH inductor"
            })
    
    # Case 3: Series inductor, shunt inductor (when R_load > Z0)
    if r_load > z0:
        q = np.sqrt(r_load / z0 - 1)
        x_series = x_load - q * z0
        x_shunt = q * z0
        
        if x_series > 0:  # Inductor
            l_series_nh = x_series / omega * 1e9
            l_shunt_nh = x_shunt / omega * 1e9
            
            solutions.append({
                "type": "L-L",
                "series_inductor_nh": l_series_nh,
                "shunt_inductor_nh": l_shunt_nh,
                "description": f"Series {l_series_nh:.2f} nH inductor, Shunt {l_shunt_nh:.2f} nH inductor"
            })
    
    # Case 4: Series capacitor, shunt capacitor (when R_load > Z0)
    if r_load > z0:
        q = np.sqrt(r_load / z0 - 1)
        x_series = x_load + q * z0
        x_shunt = -q * z0
        
        if x_series < 0:  # Capacitor
            c_series_pf = -1 / (x_series * omega) * 1e12
            c_shunt_pf = -1 / (x_shunt * omega) * 1e12
            
            solutions.append({
                "type": "C-C",
                "series_capacitor_pf": c_series_pf,
                "shunt_capacitor_pf": c_shunt_pf,
                "description": f"Series {c_series_pf:.2f} pF capacitor, Shunt {c_shunt_pf:.2f} pF capacitor"
            })
    
    return {
        "load_impedance_ohm": complex(z_load),
        "frequency_ghz": frequency_ghz,
        "solutions": solutions,
        "best_solution": solutions[0] if solutions else None
    }


def estimate_antenna_impedance(
    geometry_params: Dict[str, Any],
    frequency_ghz: float
) -> complex:
    """
    Estimate antenna input impedance from geometry and frequency.
    
    IMPORTANT: This model is frequency-dependent and accounts for:
    - Feed position (affects base impedance)
    - Frequency offset from resonance (affects reactance and resistance)
    
    The impedance varies with frequency:
    - At resonance (f = f_res): R is minimum, X ≈ 0
    - Below resonance: capacitive (negative X)
    - Above resonance: inductive (positive X)
    - Resistance increases as frequency moves away from resonance
    
    Args:
        geometry_params: Geometry parameters (must include length_mm, width_mm, etc.)
        frequency_ghz: Operating frequency in GHz (used to compute frequency offset)
        
    Returns:
        Complex impedance estimate (R + jX)
    """
    if "length_mm" in geometry_params:
        # Patch antenna model
        length_mm = geometry_params["length_mm"]
        width_mm = geometry_params.get("width_mm", length_mm)
        feed_offset_mm = geometry_params.get("feed_offset_mm", 0.0)
        eps_r = geometry_params.get("eps_r", 4.4)
        substrate_height_mm = geometry_params.get("substrate_height_mm", 1.6)
        
        # Calculate resonant frequency for this geometry
        from sim.models import estimate_patch_resonant_freq
        freq_res_ghz = estimate_patch_resonant_freq(geometry_params)
        
        # Frequency offset from resonance (normalized)
        freq_offset = (frequency_ghz - freq_res_ghz) / freq_res_ghz if freq_res_ghz > 0 else 0.0
        
        # Base impedance depends on feed position
        # At edge (offset=0): high impedance ~200 ohms
        # At center (offset=L/2): low impedance ~50 ohms
        # Feed offset is measured from the edge
        center_offset_ratio = abs(feed_offset_mm) / (length_mm / 2) if length_mm > 0 else 0
        center_offset_ratio = min(1.0, center_offset_ratio)
        
        # Base resistance at resonance (depends on feed position)
        # FIXED: Formula was inverted - at edge (offset=0) should be high, at center should be low
        # When center_offset_ratio = 0 (at edge): r_base = 200Ω (high)
        # When center_offset_ratio = 1 (at center): r_base = 50Ω (low)
        # Use a smoother transition for better matching
        r_base = 200 - 150 * (center_offset_ratio ** 1.5)  # Non-linear for better matching
        
        # Resistance increases away from resonance (Q-factor effect)
        # Higher Q = sharper resonance = faster resistance increase
        # Typical patch Q ~ 10-50, use Q ~ 20 for more realistic model (less sensitive)
        Q = 20.0
        # Reduce frequency offset sensitivity - patches are more tolerant
        r_in = r_base * (1 + Q * abs(freq_offset) * 0.5)  # Reduced sensitivity
        
        # Reactance: frequency-dependent
        # At resonance: X ≈ 0
        # Below resonance (f < f_res): capacitive (X < 0)
        # Above resonance (f > f_res): inductive (X > 0)
        # Reactance magnitude increases with frequency offset
        # Use simple LC resonator model: X ≈ 2*Q*R_base*(f - f_res)/f_res
        x_in = 2 * Q * r_base * freq_offset
        
        # Add feed position effect (small correction)
        x_feed_correction = 10.0 * (1 - 2 * center_offset_ratio)
        x_in = x_in + x_feed_correction * 0.1  # Small contribution
        
        logger.debug(
            f"Impedance calculation: f_oper={frequency_ghz:.6f}GHz, f_res={freq_res_ghz:.6f}GHz, "
            f"freq_offset={freq_offset:.6f}, R={r_in:.2f}Ω, X={x_in:.2f}Ω"
        )
        
        return complex(r_in, x_in)
    
    # Default: 50 ohms (matched)
    return complex(50.0, 0.0)


def create_touchstone_file(
    frequencies: List[float],
    s11_data: List[complex],
    filename: str,
    z0: float = Z0
) -> str:
    """
    Create Touchstone file (S1P format) from S-parameter data.
    
    Args:
        frequencies: List of frequencies in GHz
        s11_data: List of complex S11 values
        filename: Output filename
        z0: Reference impedance
        
    Returns:
        Path to created file
    """
    if not SKRF_AVAILABLE:
        # Fallback: create simple text format
        with open(filename, 'w') as f:
            f.write(f"! Touchstone file generated by ANTEX\n")
            f.write(f"! Frequency unit: GHz, S-parameter: RI (Real/Imaginary)\n")
            f.write(f"# GHZ S RI R {z0}\n")
            
            for freq, s11 in zip(frequencies, s11_data):
                f.write(f"{freq:.6f} {s11.real:.6e} {s11.imag:.6e}\n")
        
        return filename
    
    # Use scikit-rf for proper Touchstone format
    freq_hz = np.array(frequencies) * 1e9
    s11_array = np.array(s11_data)
    
    # Create Network object
    ntwk = rf.Network(frequency=freq_hz, s=s11_array, z0=z0)
    ntwk.write_touchstone(filename)
    
    return filename

