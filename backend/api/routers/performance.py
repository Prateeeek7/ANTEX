"""
Comprehensive Performance Metrics Dashboard.

Provides industry-standard performance metrics for antenna designs:
- Efficiency analysis
- Bandwidth analysis
- Gain and directivity
- Impedance matching metrics
- Radiation efficiency
- Total efficiency
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.base import get_db
from models.user import User
from models.project import AntennaProject
from models.optimization import DesignCandidate
from api.dependencies import get_current_user
from core.exceptions import ProjectNotFoundError
from sim.models import estimate_patch_resonant_freq, estimate_bandwidth, estimate_gain
from sim.s_parameters import estimate_antenna_impedance, impedance_to_s11, s11_to_vswr, s11_to_return_loss_db
from sim.radiation import calculate_radiation_pattern
from api.reports import generate_design_report
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy import desc
import logging
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter()


class PerformanceMetricsResponse(BaseModel):
    """Comprehensive performance metrics."""
    # Frequency metrics
    resonant_frequency_ghz: float
    target_frequency_ghz: float
    frequency_error_ghz: float
    frequency_error_percent: float
    
    # Bandwidth metrics
    bandwidth_mhz: float
    target_bandwidth_mhz: float
    bandwidth_ratio: float
    fractional_bandwidth_percent: float
    
    # Gain metrics
    gain_dbi: float
    directivity_dbi: float
    efficiency_percent: float
    radiation_efficiency_percent: float
    
    # Impedance metrics (stored as separate real/imag parts, not complex)
    impedance_real: float
    impedance_imag: float
    vswr: float
    return_loss_db: float
    matched: bool
    
    # Radiation metrics
    beamwidth_e_plane_deg: float
    beamwidth_h_plane_deg: float
    front_to_back_ratio_db: float
    
    # Overall score
    overall_score: float
    score_breakdown: Dict[str, float]
    
    model_config = {"arbitrary_types_allowed": True}


@router.get("/metrics/{project_id}", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    project_id: int,
    frequency_ghz: Optional[float] = Query(None, description="Analysis frequency (default: project target)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive performance metrics for a project's best design.
    
    Returns industry-standard metrics including:
    - Frequency accuracy
    - Bandwidth performance
    - Gain and efficiency
    - Impedance matching
    - Radiation characteristics
    - Overall performance score
    """
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Get best design candidate (join through OptimizationRun to get project_id)
    from models.optimization import OptimizationRun
    best_candidate = db.query(DesignCandidate).join(
        OptimizationRun
    ).filter(
        OptimizationRun.project_id == project_id
    ).order_by(desc(DesignCandidate.fitness)).first()
    
    if not best_candidate:
        raise HTTPException(status_code=404, detail="No design candidate available")
    
    # Get geometry parameters
    geometry_params = best_candidate.geometry_params if hasattr(best_candidate, 'geometry_params') else {}
    if not geometry_params:
        # Try to get from relationship
        if hasattr(best_candidate, 'geometry_param_set') and best_candidate.geometry_param_set:
            import json
            geometry_params = best_candidate.geometry_param_set.params
            if isinstance(geometry_params, str):
                geometry_params = json.loads(geometry_params)
    
    if not geometry_params:
        raise HTTPException(status_code=400, detail="No geometry parameters available")
    
    # Analysis frequency
    analysis_freq = frequency_ghz if frequency_ghz is not None else project.target_frequency_ghz
    
    # Calculate metrics
    # Frequency metrics
    resonant_freq = estimate_patch_resonant_freq(geometry_params)
    freq_error = abs(resonant_freq - project.target_frequency_ghz)
    freq_error_percent = (freq_error / project.target_frequency_ghz) * 100 if project.target_frequency_ghz > 0 else 0
    
    # Bandwidth metrics
    bandwidth = estimate_bandwidth(geometry_params)
    bandwidth_ratio = bandwidth / project.bandwidth_mhz if project.bandwidth_mhz > 0 else 0
    fractional_bw = (bandwidth / (resonant_freq * 1000)) * 100 if resonant_freq > 0 else 0
    
    # Gain metrics
    gain = estimate_gain(geometry_params)
    
    # Calculate radiation pattern for directivity
    try:
        radiation_data = calculate_radiation_pattern(geometry_params, analysis_freq)
        directivity = radiation_data.get('directivity_dbi', gain)
        efficiency = radiation_data.get('efficiency', 0.9)
        beamwidth_e = radiation_data.get('beamwidth_e_plane_deg', 90.0)
        beamwidth_h = radiation_data.get('beamwidth_h_plane_deg', 90.0)
    except Exception as e:
        logger.warning(f"Failed to calculate radiation pattern: {e}")
        # Use defaults if calculation fails
        radiation_data = {}
        directivity = gain + 2  # Assume some directivity
        efficiency = 0.9
        beamwidth_e = 90.0
        beamwidth_h = 90.0
    
    radiation_efficiency = efficiency * 0.95  # Assume 95% radiation efficiency
    
    # Impedance metrics
    z_antenna = estimate_antenna_impedance(geometry_params, analysis_freq)
    s11 = impedance_to_s11(z_antenna)
    vswr = s11_to_vswr(s11)
    return_loss = s11_to_return_loss_db(s11)
    matched = vswr < 2.0
    
    # Radiation metrics (already extracted above with error handling)
    
    # Front-to-back ratio (simplified: ratio of max to 180° gain)
    pattern = radiation_data.get('gain_pattern', [])
    if pattern and len(pattern) > 0:
        max_gain = np.max([np.max(row) for row in pattern])
        back_gain = pattern[len(pattern) // 2][len(pattern[0]) // 2] if len(pattern) > len(pattern[0]) // 2 else 0.01
        ftb_ratio = 20 * np.log10(max_gain / max(back_gain, 0.001)) if back_gain > 0 else 30.0
    else:
        ftb_ratio = 20.0  # Default
    
    # Calculate overall score (0-100)
    # Weighted combination of all metrics
    freq_score = max(0, 100 - freq_error_percent * 10)  # 10 points per 1% error
    bw_score = min(100, bandwidth_ratio * 100)  # 100% if meets target
    gain_score = min(100, (gain / 10.0) * 100)  # Normalize to 10 dBi max
    match_score = 100 if matched else max(0, 100 - (vswr - 2.0) * 20)  # Penalty for high VSWR
    efficiency_score = efficiency * 100
    
    # Weighted overall score
    overall_score = (
        0.25 * freq_score +
        0.20 * bw_score +
        0.20 * gain_score +
        0.20 * match_score +
        0.15 * efficiency_score
    )
    
    score_breakdown = {
        "frequency_accuracy": freq_score,
        "bandwidth_performance": bw_score,
        "gain_performance": gain_score,
        "impedance_matching": match_score,
        "efficiency": efficiency_score
    }
    
    return PerformanceMetricsResponse(
        resonant_frequency_ghz=resonant_freq,
        target_frequency_ghz=project.target_frequency_ghz,
        frequency_error_ghz=freq_error,
        frequency_error_percent=freq_error_percent,
        bandwidth_mhz=bandwidth,
        target_bandwidth_mhz=project.bandwidth_mhz,
        bandwidth_ratio=bandwidth_ratio,
        fractional_bandwidth_percent=fractional_bw,
        gain_dbi=gain,
        directivity_dbi=directivity,
        efficiency_percent=efficiency * 100,
        radiation_efficiency_percent=radiation_efficiency * 100,
        impedance_real=float(z_antenna.real),
        impedance_imag=float(z_antenna.imag),
        vswr=vswr,
        return_loss_db=return_loss,
        matched=matched,
        beamwidth_e_plane_deg=beamwidth_e,
        beamwidth_h_plane_deg=beamwidth_h,
        front_to_back_ratio_db=ftb_ratio,
        overall_score=overall_score,
        score_breakdown=score_breakdown
    )


@router.get("/radiation-pattern/{project_id}")
async def get_radiation_pattern(
    project_id: int,
    frequency_ghz: Optional[float] = Query(None),
    theta_points: int = Query(180, ge=10, le=360),
    phi_points: int = Query(360, ge=10, le=720),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get 3D radiation pattern data for visualization."""
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Get best design (join through OptimizationRun to get project_id)
    from models.optimization import OptimizationRun
    best_candidate = db.query(DesignCandidate).join(
        OptimizationRun
    ).filter(
        OptimizationRun.project_id == project_id
    ).order_by(desc(DesignCandidate.fitness)).first()
    
    if not best_candidate:
        raise HTTPException(status_code=404, detail="No design candidate available")
    
    # Get geometry
    geometry_params = best_candidate.geometry_params if hasattr(best_candidate, 'geometry_params') else {}
    if not geometry_params and hasattr(best_candidate, 'geometry_param_set') and best_candidate.geometry_param_set:
        import json
        geometry_params = best_candidate.geometry_param_set.params
        if isinstance(geometry_params, str):
            geometry_params = json.loads(geometry_params)
    
    if not geometry_params:
        raise HTTPException(status_code=400, detail="No geometry parameters available")
    
    # Analysis frequency
    analysis_freq = frequency_ghz if frequency_ghz is not None else project.target_frequency_ghz
    
    # Calculate radiation pattern
    pattern_data = calculate_radiation_pattern(geometry_params, analysis_freq, theta_points, phi_points)
    
    return pattern_data


@router.get("/export-pdf/{project_id}")
async def export_pdf_report(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export comprehensive PDF design report."""
    from fastapi.responses import Response
    
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Get best design (join through OptimizationRun to get project_id)
    from models.optimization import OptimizationRun
    best_candidate = db.query(DesignCandidate).join(
        OptimizationRun
    ).filter(
        OptimizationRun.project_id == project_id
    ).order_by(desc(DesignCandidate.fitness)).first()
    
    if not best_candidate:
        raise HTTPException(status_code=404, detail="No design candidate available")
    
    # Get geometry
    geometry_params = best_candidate.geometry_params if hasattr(best_candidate, 'geometry_params') else {}
    if not geometry_params and hasattr(best_candidate, 'geometry_param_set') and best_candidate.geometry_param_set:
        import json
        geometry_params = best_candidate.geometry_param_set.params
        if isinstance(geometry_params, str):
            geometry_params = json.loads(geometry_params)
    
    # Get metrics
    metrics_response = await get_performance_metrics(project_id, None, current_user, db)
    metrics_dict = metrics_response.dict()
    
    # Get radiation pattern
    radiation_data = None
    try:
        radiation_response = await get_radiation_pattern(project_id, None, 180, 360, current_user, db)
        radiation_data = radiation_response
    except:
        pass
    
    # Prepare data
    project_data = {
        'name': project.name,
        'target_frequency_ghz': project.target_frequency_ghz,
        'bandwidth_mhz': project.bandwidth_mhz,
        'substrate': project.substrate,
        'max_size_mm': project.max_size_mm
    }
    
    design_data = {
        'candidate': {
            'geometry_params': geometry_params,
            'fitness': best_candidate.fitness,
            'metrics': best_candidate.metrics if hasattr(best_candidate, 'metrics') else {}
        }
    }
    
    # Generate PDF
    try:
        pdf_bytes = generate_design_report(project_data, design_data, metrics_dict, radiation_data)
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF report: {str(e)}"
        )
    
    # Return PDF
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=antenna_design_report_{project_id}.pdf"
        }
    )

