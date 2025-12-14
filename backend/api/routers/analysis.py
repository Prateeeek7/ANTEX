"""
Advanced RF analysis endpoints for industry-level antenna design.

Provides:
- Smith Chart analysis
- S-parameter analysis
- Impedance matching
- Material library access
- Parameter sweeps
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.base import get_db
from models.user import User
from models.project import AntennaProject
from api.dependencies import get_current_user
from core.exceptions import ProjectNotFoundError
from sim.s_parameters import (
    impedance_to_s11, s11_to_impedance, s11_to_vswr, s11_to_return_loss_db,
    calculate_matching_network_l, estimate_antenna_impedance,
    create_touchstone_file
)
from sim.materials import (
    MATERIAL_LIBRARY, get_material, list_materials,
    get_effective_permittivity, estimate_substrate_loss
)
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter()


class ImpedanceAnalysisRequest(BaseModel):
    """Request for impedance analysis."""
    project_id: int
    frequency_ghz: float
    impedance_real: Optional[float] = None
    impedance_imag: Optional[float] = None
    use_geometry: bool = True  # Use geometry to estimate impedance


class ImpedanceAnalysisResponse(BaseModel):
    """Response for impedance analysis."""
    impedance_real: float
    impedance_imag: float
    s11_real: float
    s11_imag: float
    vswr: float
    return_loss_db: float
    matched: bool
    matching_networks: List[Dict[str, Any]]
    ai_recommendations: Optional[Dict[str, str]] = None
    
    model_config = {"arbitrary_types_allowed": True}


def _generate_ai_matching_recommendations(
    z_antenna: complex,
    vswr: float,
    return_loss_db: float,
    matched: bool,
    solutions: List[Dict[str, Any]],
    z0: float = 50.0
) -> Dict[str, str]:
    """
    Generate AI-powered recommendations for impedance matching.
    
    Analyzes the impedance mismatch and provides intelligent recommendations
    based on industry best practices.
    """
    recommendations = {}
    
    if matched:
        recommendations["overall"] = "✅ Excellent! Your antenna is well-matched. VSWR < 2.0 indicates good impedance matching. No matching network required."
        return recommendations
    
    # Analyze mismatch severity
    r_load = z_antenna.real
    x_load = z_antenna.imag
    
    if vswr > 5.0:
        severity = "critical"
        recommendations["overall"] = f"⚠️ Critical mismatch detected (VSWR = {vswr:.2f}). Strongly recommend matching network to improve performance."
    elif vswr > 3.0:
        severity = "high"
        recommendations["overall"] = f"⚠️ Significant mismatch (VSWR = {vswr:.2f}). Matching network recommended for optimal performance."
    else:
        severity = "moderate"
        recommendations["overall"] = f"ℹ️ Moderate mismatch (VSWR = {vswr:.2f}). Matching network can improve performance."
    
    # Specific recommendations based on impedance
    if r_load < z0 * 0.5:
        recommendations["resistance"] = f"Low resistance ({r_load:.1f}Ω). Consider series inductor to increase resistance, or use transformer matching."
    elif r_load > z0 * 2.0:
        recommendations["resistance"] = f"High resistance ({r_load:.1f}Ω). Consider shunt capacitor or transformer matching."
    else:
        recommendations["resistance"] = f"Resistance ({r_load:.1f}Ω) is reasonable. Focus on reactance compensation."
    
    if abs(x_load) > 30:
        if x_load > 0:
            recommendations["reactance"] = f"Strong inductive reactance (+j{x_load:.1f}Ω). Add series capacitor or shunt inductor to cancel."
        else:
            recommendations["reactance"] = f"Strong capacitive reactance (j{x_load:.1f}Ω). Add series inductor or shunt capacitor to cancel."
    elif abs(x_load) > 10:
        recommendations["reactance"] = f"Moderate reactance (j{x_load:.1f}Ω). Small matching component recommended."
    else:
        recommendations["reactance"] = f"Low reactance (j{x_load:.1f}Ω). Good reactive match."
    
    # Recommendations for each solution
    for i, solution in enumerate(solutions[:3]):  # Top 3 solutions
        sol_type = solution.get('type', '')
        desc = solution.get('description', '')
        
        if 'L-C' in sol_type or 'C-L' in sol_type:
            recommendations[f"solution_{i}"] = f"✅ Recommended: {desc}. This L-section network is ideal for moderate mismatches. Low component count, easy to implement."
        elif 'L-L' in sol_type:
            recommendations[f"solution_{i}"] = f"ℹ️ Alternative: {desc}. All-inductor network, good for high-frequency applications but may have higher Q."
        elif 'C-C' in sol_type:
            recommendations[f"solution_{i}"] = f"ℹ️ Alternative: {desc}. All-capacitor network, compact but may have limited tuning range."
        else:
            recommendations[f"solution_{i}"] = f"Option {i+1}: {desc}"
    
    # Best practice recommendation
    if solutions:
        best = solutions[0]
        recommendations["best_practice"] = f"🎯 Best Practice: Use {best.get('type', 'L-section')} matching network. " \
                                         f"Component values: {best.get('description', 'N/A')}. " \
                                         f"Expected improvement: VSWR < 2.0, Return Loss > 10 dB."
    
    return recommendations


class MaterialListResponse(BaseModel):
    """Response for material list."""
    materials: Dict[str, Dict[str, Any]]


class ParameterSweepRequest(BaseModel):
    """Request for parameter sweep."""
    project_id: int
    parameter_name: str
    start_value: float
    end_value: float
    num_points: int
    frequency_ghz: float


@router.post("/impedance", response_model=ImpedanceAnalysisResponse)
async def analyze_impedance(
    request: ImpedanceAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze antenna impedance and provide matching network solutions.
    
    Industry-standard impedance analysis with Smith chart data and
    matching network recommendations.
    """
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == request.project_id).first()
    if not project:
        raise ProjectNotFoundError(request.project_id)
    
    # Get best design geometry
    from models.optimization import DesignCandidate, OptimizationRun
    from sqlalchemy import desc
    
    # Find best candidate for this project
    best_candidate = db.query(DesignCandidate).join(
        OptimizationRun
    ).filter(
        OptimizationRun.project_id == request.project_id
    ).order_by(desc(DesignCandidate.fitness)).first()
    
    if request.use_geometry and best_candidate:
        # Get geometry params - could be stored in candidate or as relationship
        if hasattr(best_candidate, 'geometry_params'):
            geometry_params = best_candidate.geometry_params
        elif hasattr(best_candidate, 'geometry_param_set') and best_candidate.geometry_param_set:
            # If stored as relationship
            import json
            geometry_params = best_candidate.geometry_param_set.params
            if isinstance(geometry_params, str):
                geometry_params = json.loads(geometry_params)
        else:
            geometry_params = {}
        
        if geometry_params:
            z_antenna = estimate_antenna_impedance(geometry_params, request.frequency_ghz)
        else:
            # Fallback to default impedance
            z_antenna = complex(50.0, 10.0)
    elif request.impedance_real is not None and request.impedance_imag is not None:
        z_antenna = complex(request.impedance_real, request.impedance_imag)
    else:
        raise HTTPException(status_code=400, detail="Either provide impedance or use geometry with best design")
    
    # Use project's target impedance (default to 50 ohm if not set)
    target_impedance = project.target_impedance_ohm if hasattr(project, 'target_impedance_ohm') else 50.0
    
    # Calculate S-parameters using project's target impedance
    s11 = impedance_to_s11(z_antenna, z0=target_impedance)
    vswr = s11_to_vswr(s11)
    return_loss_db = s11_to_return_loss_db(s11)
    
    # Check if matched (VSWR < 2.0, or return loss < -10 dB)
    matched = vswr < 2.0 or return_loss_db > 10.0
    
    # Calculate matching networks using project's target impedance
    matching_networks = calculate_matching_network_l(
        z_antenna,
        request.frequency_ghz,
        z0=target_impedance
    )
    
    # Generate AI recommendations for matching
    ai_recommendations = _generate_ai_matching_recommendations(
        z_antenna, vswr, return_loss_db, matched, matching_networks.get('solutions', []), target_impedance
    )
    
    # Add recommendations to matching networks
    enhanced_networks = []
    for i, network in enumerate(matching_networks.get('solutions', [])):
        enhanced_networks.append({
            **network,
            "ai_recommendation": ai_recommendations.get(f"solution_{i}", ""),
            "priority": i + 1
        })
    
    return ImpedanceAnalysisResponse(
        impedance_real=float(z_antenna.real),
        impedance_imag=float(z_antenna.imag),
        s11_real=float(s11.real),
        s11_imag=float(s11.imag),
        vswr=vswr,
        return_loss_db=return_loss_db,
        matched=matched,
        matching_networks=enhanced_networks,
        ai_recommendations=ai_recommendations
    )


@router.get("/materials", response_model=MaterialListResponse)
async def get_material_library(
    category: Optional[str] = Query(None, description="Filter: 'substrate', 'conductor', or None for all"),
    current_user: User = Depends(get_current_user)
):
    """
    Get industry-standard material library.
    
    Returns comprehensive material database with dielectric properties,
    loss tangents, and application notes.
    """
    materials = list_materials(category)
    
    # Convert to dict format for JSON serialization
    materials_dict = {}
    for name, props in materials.items():
        materials_dict[name] = {
            "name": props.name,
            "eps_r": props.eps_r,
            "loss_tan": props.loss_tan,
            "conductivity_s_m": props.conductivity_s_m,
            "thickness_mm": props.thickness_mm,
            "cost_tier": props.cost_tier,
            "application": props.application
        }
    
    return MaterialListResponse(materials=materials_dict)


@router.get("/materials/{material_name}")
async def get_material_properties(
    material_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get properties for a specific material."""
    material = get_material(material_name)
    if not material:
        raise HTTPException(status_code=404, detail=f"Material '{material_name}' not found")
    
    return {
        "name": material.name,
        "eps_r": material.eps_r,
        "loss_tan": material.loss_tan,
        "conductivity_s_m": material.conductivity_s_m,
        "thickness_mm": material.thickness_mm,
        "cost_tier": material.cost_tier,
        "application": material.application
    }


@router.post("/sweep")
async def parameter_sweep(
    request: ParameterSweepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform parameter sweep analysis.
    
    Varies a design parameter and analyzes performance across the range.
    Essential for sensitivity analysis and design optimization.
    """
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == request.project_id).first()
    if not project:
        raise ProjectNotFoundError(request.project_id)
    
    # Get best design
    from models.optimization import DesignCandidate, OptimizationRun
    from sqlalchemy import desc
    
    best_candidate = db.query(DesignCandidate).join(
        OptimizationRun
    ).filter(
        OptimizationRun.project_id == request.project_id
    ).order_by(desc(DesignCandidate.fitness)).first()
    
    if not best_candidate:
        raise HTTPException(status_code=400, detail="No design candidate available for sweep")
    
    # Extract geometry params
    if hasattr(best_candidate, 'geometry_params'):
        geometry_params = best_candidate.geometry_params
    elif hasattr(best_candidate, 'geometry_param_set') and best_candidate.geometry_param_set:
        import json
        geometry_params = best_candidate.geometry_param_set.params
        if isinstance(geometry_params, str):
            geometry_params = json.loads(geometry_params)
    else:
        geometry_params = {}
    
    geometry_params = dict(geometry_params) if geometry_params else {}
    
    # Generate parameter values
    param_values = np.linspace(request.start_value, request.end_value, request.num_points)
    
    # Perform sweep
    results = []
    for sweep_idx, param_value in enumerate(param_values):
        # Update parameter
        geometry_params[request.parameter_name] = param_value
        
        # IMPORTANT: Ensure we have project parameters for accurate calculation
        # Add substrate thickness and material properties if not present
        if 'substrate_height_mm' not in geometry_params:
            geometry_params['substrate_height_mm'] = project.substrate_thickness_mm
        if 'eps_r' not in geometry_params:
            from sim.material_properties import get_substrate_properties
            material_props = get_substrate_properties(project.substrate)
            geometry_params['eps_r'] = material_props["permittivity"]
        
        # Calculate resonant frequency FIRST (needed for impedance calculation)
        # IMPORTANT: Frequency is recalculated for each sweep point
        from sim.models import estimate_patch_resonant_freq, estimate_bandwidth, estimate_gain
        freq_res = estimate_patch_resonant_freq(geometry_params)
        bandwidth = estimate_bandwidth(geometry_params)
        gain = estimate_gain(geometry_params)
        
        # Estimate impedance using operating frequency vs resonant frequency
        # IMPORTANT: Impedance is frequency-dependent and will vary as geometry changes
        z = estimate_antenna_impedance(geometry_params, request.frequency_ghz)
        
        # Compute S11 (reflection coefficient) from impedance
        # S11 = (Z - Z0) / (Z + Z0)
        s11 = impedance_to_s11(z)
        
        # Compute VSWR from S11 magnitude (not heuristics!)
        # VSWR = (1 + |S11|) / (1 - |S11|)
        vswr = s11_to_vswr(s11)
        
        # Compute Return Loss from S11 magnitude
        # RL = -20 * log10(|S11|)
        return_loss_db = s11_to_return_loss_db(s11)
        
        # DETAILED SWEEP LOGGING: Print all values to confirm non-flat variation
        logger.info(
            f"[SWEEP STEP {sweep_idx+1}/{len(param_values)}] "
            f"{request.parameter_name}={param_value:.6f}, "
            f"L={geometry_params.get('length_mm', 'N/A'):.3f}mm, "
            f"W={geometry_params.get('width_mm', 'N/A'):.3f}mm, "
            f"f_res={freq_res:.6f}GHz, f_oper={request.frequency_ghz:.6f}GHz, "
            f"freq_offset={((request.frequency_ghz - freq_res) / freq_res * 100):.2f}%, "
            f"Z={z.real:.2f}+j{z.imag:.2f}Ω, "
            f"|S11|={abs(s11):.4f}, RL={return_loss_db:.2f}dB, VSWR={vswr:.3f}, "
            f"BW={bandwidth:.2f}MHz, Gain={gain:.2f}dBi"
        )
        
        # Calculate and log ε_eff and ΔL for length sweeps
        if request.parameter_name == "length_mm":
            from sim.models import estimate_patch_resonant_freq
            # Recalculate to get intermediate values
            length_mm = geometry_params.get('length_mm')
            width_mm = geometry_params.get('width_mm')
            h = geometry_params.get('substrate_height_mm', 1.6)
            eps_r = geometry_params.get('eps_r', 4.4)
            if width_mm and length_mm:
                ratio_h_W = h / width_mm
                eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * ratio_h_W) ** (-0.5)
                ratio_W_h = width_mm / h
                delta_L = 0.412 * h * (eps_eff + 0.3) * (ratio_W_h + 0.264) / ((eps_eff - 0.258) * (ratio_W_h + 0.8))
                logger.debug(
                    f"[SWEEP DETAILS] ε_eff={eps_eff:.4f}, ΔL={delta_L:.4f}mm, "
                    f"L_eff={length_mm + 2*delta_L:.4f}mm"
                )
        
        results.append({
            "parameter_value": float(param_value),
            "impedance_real": float(z.real),
            "impedance_imag": float(z.imag),
            "s11_magnitude": float(abs(s11)),
            "s11_phase_deg": float(np.angle(s11) * 180 / np.pi),
            "vswr": float(vswr),  # Computed from S11, not heuristics
            "return_loss_db": float(return_loss_db),  # Computed from S11, frequency-dependent
            "resonant_frequency_ghz": freq_res,
            "frequency_offset_percent": float((request.frequency_ghz - freq_res) / freq_res * 100),
            "bandwidth_mhz": bandwidth,
            "gain_dbi": gain
        })
    
    return {
        "parameter_name": request.parameter_name,
        "frequency_ghz": request.frequency_ghz,
        "sweep_range": [request.start_value, request.end_value],
        "results": results
    }


@router.post("/export-touchstone/{project_id}")
async def export_touchstone(
    project_id: int,
    frequency_start_ghz: float = Query(..., description="Start frequency in GHz"),
    frequency_end_ghz: float = Query(..., description="End frequency in GHz"),
    num_points: int = Query(100, description="Number of frequency points"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export S-parameters as Touchstone file.
    
    Industry-standard format compatible with ADS, HFSS, CST, etc.
    """
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Generate frequency sweep
    frequencies = np.linspace(frequency_start_ghz, frequency_end_ghz, num_points)
    
    # Get best design
    from models.optimization import DesignCandidate, OptimizationRun
    from sqlalchemy import desc
    
    best_candidate = db.query(DesignCandidate).join(
        OptimizationRun
    ).filter(
        OptimizationRun.project_id == project_id
    ).order_by(desc(DesignCandidate.fitness)).first()
    
    if not best_candidate:
        raise HTTPException(status_code=400, detail="No design candidate available")
    
    # Extract geometry params
    if hasattr(best_candidate, 'geometry_params'):
        geometry_params = best_candidate.geometry_params
    elif hasattr(best_candidate, 'geometry_param_set') and best_candidate.geometry_param_set:
        import json
        geometry_params = best_candidate.geometry_param_set.params
        if isinstance(geometry_params, str):
            geometry_params = json.loads(geometry_params)
    else:
        geometry_params = {}
    
    geometry_params = dict(geometry_params) if geometry_params else {}
    
    # Calculate S11 for each frequency
    s11_data = []
    for freq in frequencies:
        z = estimate_antenna_impedance(geometry_params, freq)
        s11 = impedance_to_s11(z)
        s11_data.append(s11)
    
    # Create Touchstone file
    import tempfile
    import os
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.s1p')
    temp_path = temp_file.name
    temp_file.close()
    
    create_touchstone_file(frequencies.tolist(), s11_data, temp_path)
    
    # Read file content
    with open(temp_path, 'r') as f:
        content = f.read()
    
    # Cleanup
    os.unlink(temp_path)
    
    return {
        "filename": f"antenna_project_{project_id}.s1p",
        "content": content,
        "format": "Touchstone S1P",
        "frequency_range_ghz": [frequency_start_ghz, frequency_end_ghz]
    }

