"""
3D Radiation Pattern Analysis for Antenna Design.

Provides:
- Far-field radiation pattern calculation
- 3D polar plots (gain patterns)
- Directivity and efficiency calculations
- Beamwidth analysis
"""
import numpy as np
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_radiation_pattern(
    geometry_params: Dict[str, Any],
    frequency_ghz: float,
    theta_points: int = 180,
    phi_points: int = 360
) -> Dict[str, Any]:
    """
    Calculate 3D radiation pattern for patch antenna.
    
    Uses analytical models based on antenna theory:
    - Patch antennas: TM10 mode radiation pattern
    - Approximate far-field calculation
    
    Args:
        geometry_params: Geometry parameters
        frequency_ghz: Operating frequency in GHz
        theta_points: Number of elevation angles (0-180°)
        phi_points: Number of azimuth angles (0-360°)
        
    Returns:
        Dictionary with radiation pattern data
    """
    if "length_mm" in geometry_params:
        # Patch antenna radiation pattern
        return _calculate_patch_radiation_pattern(
            geometry_params, frequency_ghz, theta_points, phi_points
        )
    else:
        # Default: isotropic pattern
        return _calculate_isotropic_pattern(theta_points, phi_points)


def _calculate_patch_radiation_pattern(
    params: Dict[str, Any],
    freq_ghz: float,
    theta_points: int,
    phi_points: int
) -> Dict[str, Any]:
    """
    Calculate patch antenna radiation pattern (TM10 mode).
    
    Pattern formula:
    E(θ,φ) = E0 * cos(π*L*sin(θ)*cos(φ)/λ) * sinc(W*sin(θ)*sin(φ)/λ)
    """
    length_mm = params.get("length_mm", 30.0)
    width_mm = params.get("width_mm", 30.0)
    eps_r = params.get("eps_r", 4.4)
    
    # Convert to meters
    length = length_mm * 1e-3
    width = width_mm * 1e-3
    
    # Wavelength
    c = 299792458.0
    freq_hz = freq_ghz * 1e9
    wavelength = c / freq_hz
    wavelength_eff = wavelength / np.sqrt(eps_r)  # Effective wavelength in substrate
    
    # Angular grid
    theta = np.linspace(0, np.pi, theta_points)  # Elevation: 0 to 180°
    phi = np.linspace(0, 2 * np.pi, phi_points)  # Azimuth: 0 to 360°
    
    THETA, PHI = np.meshgrid(theta, phi)
    
    # Radiation pattern calculation
    # E-plane (φ=0): E(θ) = cos(π*L*sin(θ)/λ)
    # H-plane (φ=90°): E(θ) = sinc(W*sin(θ)/λ)
    
    # General pattern (simplified)
    k = 2 * np.pi / wavelength
    
    # E-field pattern
    E_theta = np.cos(np.pi * length * np.sin(THETA) * np.cos(PHI) / wavelength)
    E_phi = np.sinc(width * np.sin(THETA) * np.sin(PHI) / wavelength)
    
    # Combined pattern (normalized)
    E_pattern = E_theta * E_phi
    
    # Apply cos(θ) factor for patch antenna (stronger in broadside)
    E_pattern = E_pattern * np.cos(THETA)
    
    # Normalize
    E_pattern = np.abs(E_pattern)
    E_max = np.max(E_pattern)
    if E_max > 0:
        E_pattern = E_pattern / E_max
    
    # Calculate gain (dBi)
    # Directivity: D = 4π / (∫∫|E|² dΩ)
    d_omega = np.sin(THETA)  # Solid angle element
    power_pattern = E_pattern ** 2
    total_power = np.trapz(np.trapz(power_pattern * d_omega, theta, axis=1), phi, axis=0)
    
    if total_power > 0:
        directivity = 4 * np.pi / total_power
        gain_dbi = 10 * np.log10(directivity)
    else:
        gain_dbi = 0.0
    
    # Calculate beamwidth
    # Find -3dB points in E-plane (φ=0) and H-plane (φ=90°)
    e_plane_cut = E_pattern[:, 0]  # φ=0
    h_plane_cut = E_pattern[:, phi_points // 4]  # φ=90°
    
    # Find half-power beamwidth
    e_plane_hpbw = _calculate_beamwidth(theta, e_plane_cut)
    h_plane_hpbw = _calculate_beamwidth(theta, h_plane_cut)
    
    # Convert to gain in dBi (add efficiency factor)
    efficiency = 0.9  # Typical patch antenna efficiency
    gain_dbi = gain_dbi + 10 * np.log10(efficiency)
    
    return {
        "theta": theta.tolist(),
        "phi": phi.tolist(),
        "gain_pattern": E_pattern.tolist(),
        "gain_dbi": float(gain_dbi),
        "directivity_dbi": float(10 * np.log10(directivity)) if total_power > 0 else 0.0,
        "efficiency": float(efficiency),
        "beamwidth_e_plane_deg": float(e_plane_hpbw),
        "beamwidth_h_plane_deg": float(h_plane_hpbw),
        "max_gain_theta_deg": float(np.degrees(theta[np.argmax(e_plane_cut)])),
        "max_gain_phi_deg": 0.0,  # Typically broadside for patch
        "frequency_ghz": freq_ghz
    }


def _calculate_isotropic_pattern(theta_points: int, phi_points: int) -> Dict[str, Any]:
    """Calculate isotropic radiation pattern (reference)."""
    theta = np.linspace(0, np.pi, theta_points)
    phi = np.linspace(0, 2 * np.pi, phi_points)
    THETA, PHI = np.meshgrid(theta, phi)
    
    # Uniform pattern
    E_pattern = np.ones_like(THETA)
    
    return {
        "theta": theta.tolist(),
        "phi": phi.tolist(),
        "gain_pattern": E_pattern.tolist(),
        "gain_dbi": 0.0,  # Isotropic = 0 dBi
        "directivity_dbi": 0.0,
        "efficiency": 1.0,
        "beamwidth_e_plane_deg": 360.0,
        "beamwidth_h_plane_deg": 360.0,
        "max_gain_theta_deg": 90.0,
        "max_gain_phi_deg": 0.0,
        "frequency_ghz": 2.4
    }


def _calculate_beamwidth(theta: np.ndarray, pattern: np.ndarray) -> float:
    """Calculate half-power beamwidth (HPBW) in degrees."""
    # Find maximum
    max_idx = np.argmax(pattern)
    max_value = pattern[max_idx]
    
    # Find -3dB points (half power)
    half_power = max_value / np.sqrt(2)
    
    # Find points where pattern crosses half-power level
    above_half = pattern >= half_power
    if not np.any(above_half):
        return 180.0  # No beamwidth defined
    
    # Find first and last points above half-power
    indices = np.where(above_half)[0]
    if len(indices) < 2:
        return 180.0
    
    first_idx = indices[0]
    last_idx = indices[-1]
    
    # Ensure indices are within bounds
    first_idx = min(first_idx, len(theta) - 1)
    last_idx = min(last_idx, len(theta) - 1)
    
    # Convert to degrees
    theta_first = np.degrees(theta[first_idx])
    theta_last = np.degrees(theta[last_idx])
    
    beamwidth = abs(theta_last - theta_first)
    return min(beamwidth, 180.0)


def calculate_far_field_from_near_field(
    near_field_data: Dict[str, Any],
    frequency_ghz: float
) -> Dict[str, Any]:
    """
    Transform near-field data to far-field radiation pattern.
    
    Uses near-field to far-field transformation (NFFFT) algorithm.
    This is a simplified version - full implementation would use
    vector potential integration.
    
    Args:
        near_field_data: Near-field E and H field data
        frequency_ghz: Frequency in GHz
        
    Returns:
        Far-field radiation pattern
    """
    # Simplified transformation
    # In practice, this requires integration over a closed surface
    # using the equivalence principle
    
    logger.info("Near-field to far-field transformation (simplified)")
    
    # For now, use analytical pattern as approximation
    # Full NFFFT would require:
    # 1. Surface integration of equivalent currents
    # 2. Vector potential calculation
    # 3. Far-field limit approximation
    
    return {
        "method": "analytical_approximation",
        "note": "Full NFFFT requires surface integration - using analytical pattern",
        "pattern": _calculate_isotropic_pattern(180, 360)
    }

