"""
Fitness computation for optimization.

Supports both analytical models and real Meep FDTD simulations.
"""
from typing import Dict, Any, Optional
from sim.models import estimate_patch_resonant_freq, estimate_bandwidth, estimate_gain
from sim.types import GeometryParams
from core.config import settings
import logging
import math
import numpy as np

logger = logging.getLogger(__name__)

# Try to import Meep simulator (optional)
try:
    from sim.meep_simulator import simulate_patch_antenna, check_meep_available
    MEEP_AVAILABLE = check_meep_available()
except ImportError:
    MEEP_AVAILABLE = False
    logger.warning("Meep simulator not available. Using analytical models only.")


def compute_fitness(
    params: Dict[str, Any],
    target_frequency_ghz: float,
    target_bandwidth_mhz: float,
    weights: Dict[str, float] = None,
    use_meep: Optional[bool] = None,
    project_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compute fitness score for a geometry parameter set.
    
    Args:
        params: Geometry parameters dict
        target_frequency_ghz: Target resonant frequency in GHz
        target_bandwidth_mhz: Target bandwidth in MHz
        weights: Optional weights for fitness components
        use_meep: Whether to use Meep FDTD (None = use config setting)
        project_params: Optional project parameters (substrate, thickness, etc.)
        
    Returns:
        Dict with fitness score and metrics
    """
    if weights is None:
        weights = {
            "freq_error": 0.6,
            "bandwidth_error": 0.3,
            "gain_bonus": 0.1
        }
    
    # Determine if we should use Meep
    should_use_meep = use_meep if use_meep is not None else settings.USE_MEEP
    
    # Extract project parameters if provided
    substrate = project_params.get("substrate", "FR4") if project_params else "FR4"
    substrate_thickness_mm = project_params.get("substrate_thickness_mm", 1.6) if project_params else 1.6
    target_gain_dbi = project_params.get("target_gain_dbi", 5.0) if project_params else 5.0
    target_impedance_ohm = project_params.get("target_impedance_ohm", 50.0) if project_params else 50.0
    conductor_thickness_um = project_params.get("conductor_thickness_um", 35.0) if project_params else 35.0
    
    # Get material properties
    from sim.material_properties import get_substrate_properties
    material_props = get_substrate_properties(substrate)
    eps_r = material_props["permittivity"]
    loss_tan = material_props["loss_tangent"]
    
    # Update params with project-specific values
    params_with_project = params.copy()
    params_with_project["eps_r"] = eps_r
    params_with_project["substrate_height_mm"] = substrate_thickness_mm
    
    # Use real FDTD simulation if enabled and available
    if should_use_meep and MEEP_AVAILABLE:
        try:
            return _compute_fitness_meep(
                params_with_project, 
                target_frequency_ghz, 
                target_bandwidth_mhz, 
                weights,
                substrate_thickness_mm,
                eps_r,
                loss_tan,
                conductor_thickness_um,
                target_gain_dbi,
                target_impedance_ohm
            )
        except Exception as e:
            logger.warning(f"Meep simulation failed, falling back to analytical: {e}")
            # Fall through to analytical model
    
    # Use analytical models (fast approximation)
    # IMPORTANT: Frequency is recalculated every time params change
    freq_ghz = estimate_patch_resonant_freq(params_with_project)
    bandwidth_mhz = estimate_bandwidth(params_with_project)
    
    # Calculate efficiency first (needed for gain calculation)
    # Efficiency accounts for conductor and dielectric losses
    frequency_hz = target_frequency_ghz * 1e9
    trace_length_mm = params_with_project.get("length_mm", 30.0) * 0.5  # Approximate feed length
    trace_width_mm = params_with_project.get("feed_width_mm", 2.0)  # Default feed width for loss calculation
    
    from sim.material_properties import calculate_conductor_loss, calculate_dielectric_loss
    conductor_loss_db = calculate_conductor_loss(
        frequency_hz, trace_width_mm, trace_length_mm, conductor_thickness_um
    )
    dielectric_loss_db = calculate_dielectric_loss(
        frequency_hz, loss_tan, eps_r, substrate_thickness_mm, trace_length_mm
    )
    total_loss_db = conductor_loss_db + dielectric_loss_db
    
    # Calculate efficiency (accounting for losses)
    # Efficiency = 10^(-total_loss_db/10)
    efficiency_linear = 10 ** (-total_loss_db / 10) if total_loss_db > 0 else 1.0
    efficiency_percent = efficiency_linear * 100
    
    # Gain = Efficiency × Directivity (calculated using W × L aperture)
    gain_dbi = estimate_gain(params_with_project, efficiency_percent=efficiency_percent)
    
    # Compute errors
    freq_error_ghz = abs(freq_ghz - target_frequency_ghz)
    bandwidth_error_mhz = abs(bandwidth_mhz - target_bandwidth_mhz)
    
    # Normalize errors (relative to targets)
    freq_error_normalized = freq_error_ghz / target_frequency_ghz if target_frequency_ghz > 0 else 1.0
    bandwidth_error_normalized = bandwidth_error_mhz / target_bandwidth_mhz if target_bandwidth_mhz > 0 else 1.0
    
    # CRITICAL: Add large penalty for frequency error > 10%
    # This prevents optimizer from sacrificing frequency for gain
    freq_error_penalty = 0.0
    if freq_error_normalized > 0.10:  # > 10% error
        # Exponential penalty: error^2 scaled by severity
        freq_error_penalty = (freq_error_normalized - 0.10) ** 2 * 500  # Large penalty
        logger.warning(
            f"Large frequency error detected: {freq_error_normalized*100:.1f}% "
            f"(f_res={freq_ghz:.3f}GHz vs target={target_frequency_ghz:.3f}GHz). "
            f"Applying penalty: {freq_error_penalty:.2f}"
        )
    
    # Calculate impedance and return loss using project parameters
    # IMPORTANT: Use frequency-dependent impedance model
    from sim.material_properties import get_effective_permittivity, calculate_conductor_loss, calculate_dielectric_loss
    from sim.s_parameters import estimate_antenna_impedance, impedance_to_s11, s11_to_vswr, s11_to_return_loss_db
    
    # Estimate input impedance using frequency-dependent model
    # This uses the actual operating frequency (target_frequency_ghz) vs resonant frequency (freq_ghz)
    estimated_impedance = estimate_antenna_impedance(params_with_project, target_frequency_ghz)
    
    # Calculate S11 (reflection coefficient) from impedance
    # S11 = (Z - Z0) / (Z + Z0)
    s11 = impedance_to_s11(estimated_impedance)
    
    # Calculate VSWR from S11 magnitude (not heuristics!)
    # VSWR = (1 + |S11|) / (1 - |S11|)
    vswr = s11_to_vswr(s11)
    
    # Calculate Return Loss from S11 magnitude
    # RL = -20 * log10(|S11|)
    return_loss_dB = s11_to_return_loss_db(s11)
    
    # Calculate impedance mismatch error
    impedance_error = abs(estimated_impedance.real - target_impedance_ohm) / target_impedance_ohm
    
    # DETAILED DEBUG OUTPUT: Print all key metrics for each optimizer step
    # This helps verify calculations are correct and parameters are being used properly
    logger.info(
        f"[OPTIMIZER STEP] "
        f"L={params_with_project.get('length_mm', 'N/A'):.3f}mm, "
        f"W={params_with_project.get('width_mm', 'N/A'):.3f}mm, "
        f"h={substrate_thickness_mm:.3f}mm, ε_r={eps_r:.3f}, "
        f"f_res={freq_ghz:.6f}GHz (target={target_frequency_ghz:.6f}GHz), "
        f"f_error={freq_error_ghz:.6f}GHz ({freq_error_normalized*100:.2f}%), "
        f"BW={bandwidth_mhz:.2f}MHz, "
        f"RL={return_loss_dB:.2f}dB, VSWR={vswr:.3f}, "
        f"Gain={gain_dbi:.2f}dBi (η={efficiency_percent:.1f}%), "
        f"Z={estimated_impedance.real:.2f}+j{estimated_impedance.imag:.2f}Ω"
    )
    
    # Calculate ε_eff and ΔL for detailed logging (recalculate for consistency)
    eps_eff_calc = None
    delta_L_calc = None
    if "length_mm" in params_with_project:
        length_mm = params_with_project.get("length_mm")
        width_mm = params_with_project.get("width_mm")
        h = substrate_thickness_mm
        W = width_mm
        if W > 0:
            ratio_h_W = h / W
            eps_eff_calc = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * ratio_h_W) ** (-0.5)
            ratio_W_h = W / h
            delta_L_calc = 0.412 * h * (eps_eff_calc + 0.3) * (ratio_W_h + 0.264) / ((eps_eff_calc - 0.258) * (ratio_W_h + 0.8))
    
    # Calculate directivity for logging
    directivity_dbi = None
    if "length_mm" in params_with_project and freq_ghz > 0:
        length_mm = params_with_project.get("length_mm")
        width_mm = params_with_project.get("width_mm")
        wavelength_m = 299792458 / (freq_ghz * 1e9)
        area_m2 = (length_mm * width_mm * 1e-6) * 0.8  # Aperture efficiency
        directivity_linear = 4 * math.pi * area_m2 / (wavelength_m ** 2)
        directivity_dbi = 10 * math.log10(directivity_linear) if directivity_linear > 0 else 0
    
    if eps_eff_calc is not None and delta_L_calc is not None:
        logger.debug(
            f"[DETAILED METRICS] "
            f"ε_eff={eps_eff_calc:.4f}, ΔL={delta_L_calc:.4f}mm, "
            f"L_eff={params_with_project.get('length_mm', 0) + 2*delta_L_calc:.4f}mm, "
            f"Efficiency×Directivity: η={efficiency_linear:.4f}, "
            f"Directivity={directivity_dbi:.2f}dBi" + (f", Gain={gain_dbi:.2f}dBi" if directivity_dbi else "")
        )
    
    # Gain penalty for not meeting target
    gain_error = max(0, target_gain_dbi - gain_dbi) / target_gain_dbi if target_gain_dbi > 0 else 0
    
    # Fitness: lower is better (we want to minimize error)
    # We use negative because we want to maximize fitness, so we minimize the weighted error sum
    # CRITICAL: Frequency error penalty is added separately to strongly penalize frequency violations
    fitness = -(
        weights["freq_error"] * freq_error_normalized * 100 +
        weights["bandwidth_error"] * bandwidth_error_normalized * 100 +
        weights.get("impedance_error", 0.15) * impedance_error * 100 +
        weights.get("gain_error", 0.1) * gain_error * 100 -
        weights["gain_bonus"] * gain_dbi * 10  # Bonus for higher gain
    ) - freq_error_penalty  # Subtract penalty for large frequency errors
    
    # Normalize fitness to positive range (optional, depends on optimizer preference)
    # Many optimizers expect positive fitness, so we can shift:
    fitness = fitness + 100  # Shift to make it positive
    
    return {
        "fitness": fitness,
        "metrics": {
            "freq_error_ghz": freq_error_ghz,
            "bandwidth_error_mhz": bandwidth_error_mhz,
            "gain_estimate_dBi": gain_dbi,
            "return_loss_dB": return_loss_dB,
            "estimated_freq_ghz": freq_ghz,
            "estimated_bandwidth_mhz": bandwidth_mhz,
            "estimated_impedance_ohm": {
                "real": float(estimated_impedance.real),
                "imag": float(estimated_impedance.imag)
            },
            "vswr": vswr,
            "conductor_loss_db": conductor_loss_db,
            "dielectric_loss_db": dielectric_loss_db,
            "total_loss_db": total_loss_db,
            "efficiency_percent": efficiency_percent,
            "impedance_error": impedance_error,
            "gain_error": gain_error,
            "simulation_method": "analytical"
        }
    }


def _compute_fitness_meep(
    params: Dict[str, Any],
    target_frequency_ghz: float,
    target_bandwidth_mhz: float,
    weights: Dict[str, float],
    substrate_thickness_mm: float = 1.6,
    eps_r: float = 4.4,
    loss_tan: float = 0.02,
    conductor_thickness_um: float = 35.0,
    target_gain_dbi: float = 5.0,
    target_impedance_ohm: float = 50.0
) -> Dict[str, Any]:
    """
    Compute fitness using real Meep FDTD simulation.
    
    This provides CST/HFSS-grade accuracy but is much slower than analytical models.
    """
    # Extract geometry parameters
    length_mm = params.get("length_mm", 30.0)
    width_mm = params.get("width_mm", 30.0)
    
    # Use project parameters for substrate
    substrate_height_mm = substrate_thickness_mm
    
    # Run Meep simulation with project parameters
    sim_result = simulate_patch_antenna(
        length_mm=length_mm,
        width_mm=width_mm,
        target_freq_ghz=target_frequency_ghz,
        substrate_height_mm=substrate_height_mm,
        eps_r=eps_r,
        loss_tan=loss_tan,
        resolution=settings.MEEP_RESOLUTION
    )
    
    if not sim_result['success']:
        raise RuntimeError(f"Meep simulation failed: {sim_result.get('error', 'Unknown error')}")
    
    metrics = sim_result['metrics']
    
    # Extract real simulation results
    freq_ghz = metrics.get('resonant_frequency_ghz', target_frequency_ghz)
    bandwidth_mhz = metrics.get('bandwidth_mhz', target_bandwidth_mhz)
    gain_dbi = metrics.get('gain_dbi', 5.0)
    return_loss_dB = metrics.get('return_loss_dB', -10.0)
    freq_error_ghz = metrics.get('frequency_error_ghz', 0.0)
    
    # Compute errors
    bandwidth_error_mhz = abs(bandwidth_mhz - target_bandwidth_mhz)
    
    # Normalize errors
    freq_error_normalized = freq_error_ghz / target_frequency_ghz if target_frequency_ghz > 0 else 1.0
    bandwidth_error_normalized = bandwidth_error_mhz / target_bandwidth_mhz if target_bandwidth_mhz > 0 else 1.0
    
    # Calculate impedance metrics from simulation
    # Handle both complex and dict formats for impedance
    impedance_data = metrics.get('impedance_ohm', target_impedance_ohm)
    if isinstance(impedance_data, dict):
        estimated_impedance_real = impedance_data.get('real', target_impedance_ohm)
        estimated_impedance_imag = impedance_data.get('imag', 0.0)
        # Keep reference for dict conversion
        estimated_impedance_for_dict = impedance_data
    elif hasattr(impedance_data, 'real'):
        estimated_impedance_real = impedance_data.real
        estimated_impedance_imag = impedance_data.imag
        # Keep reference for dict conversion
        estimated_impedance_for_dict = impedance_data
    else:
        estimated_impedance_real = float(impedance_data)
        estimated_impedance_imag = 0.0
        # For scalar, create a simple dict
        estimated_impedance_for_dict = {"real": estimated_impedance_real, "imag": 0.0}
    
    impedance_error = abs(estimated_impedance_real - target_impedance_ohm) / target_impedance_ohm
    vswr = metrics.get('vswr', 2.0)
    
    # Gain error
    gain_error = max(0, target_gain_dbi - gain_dbi) / target_gain_dbi if target_gain_dbi > 0 else 0
    
    # Fitness calculation (same as analytical, but with real data)
    fitness = -(
        weights["freq_error"] * freq_error_normalized * 100 +
        weights["bandwidth_error"] * bandwidth_error_normalized * 100 +
        weights.get("impedance_error", 0.15) * impedance_error * 100 +
        weights.get("gain_error", 0.1) * gain_error * 100 -
        weights["gain_bonus"] * gain_dbi * 10
    )
    fitness = fitness + 100  # Shift to positive
    
    # Convert impedance to JSON-serializable dict format
    if isinstance(estimated_impedance_for_dict, dict):
        impedance_dict = estimated_impedance_for_dict
    elif hasattr(estimated_impedance_for_dict, 'real'):
        impedance_dict = {
            "real": float(estimated_impedance_for_dict.real),
            "imag": float(estimated_impedance_for_dict.imag)
        }
    else:
        impedance_dict = {
            "real": float(estimated_impedance_for_dict),
            "imag": 0.0
        }
    
    return {
        "fitness": fitness,
        "metrics": {
            "freq_error_ghz": freq_error_ghz,
            "bandwidth_error_mhz": bandwidth_error_mhz,
            "gain_estimate_dBi": gain_dbi,
            "return_loss_dB": return_loss_dB,
            "estimated_freq_ghz": freq_ghz,
            "estimated_bandwidth_mhz": bandwidth_mhz,
            "estimated_impedance_ohm": impedance_dict,
            "vswr": vswr,
            "impedance_error": impedance_error,
            "gain_error": gain_error,
            "simulation_method": "Meep_FDTD",
            "s11_data": sim_result.get('s11_data')
        }
    }


