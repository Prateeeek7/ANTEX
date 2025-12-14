"""
API endpoints for Meep FDTD simulation integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.base import get_db
from models.user import User
from models.project import AntennaProject
from api.dependencies import get_current_user
from core.exceptions import ProjectNotFoundError
from core.config import settings
from sim.meep_simulator import simulate_patch_antenna, check_meep_available, export_stl
from sim.fdtd_solver import simulate_patch_antenna_fdtd
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SimulationRequest(BaseModel):
    project_id: int
    geometry_params: Dict[str, Any]
    target_frequency_ghz: float
    use_meep: Optional[bool] = None


class STLExportRequest(BaseModel):
    project_id: int
    candidate_id: Optional[int] = None
    geometry_params: Dict[str, Any]


@router.post("/simulate")
async def run_simulation(
    request: SimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run Meep FDTD simulation for antenna geometry.
    
    Returns real S11, gain, and other EM metrics.
    """
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == request.project_id).first()
    if not project:
        raise ProjectNotFoundError(request.project_id)
    
    # Extract geometry parameters
    params = request.geometry_params
    length_mm = params.get("length_mm", 30.0)
    width_mm = params.get("width_mm", 30.0)
    substrate_height_mm = params.get("substrate_height_mm", 1.6)
    eps_r = params.get("eps_r", 4.4)
    
    # Determine if Meep should be used
    use_meep = request.use_meep if request.use_meep is not None else settings.USE_MEEP
    
    if use_meep and check_meep_available():
        try:
            # Run Meep simulation
            result = simulate_patch_antenna(
                length_mm=length_mm,
                width_mm=width_mm,
                target_freq_ghz=request.target_frequency_ghz,
                substrate_height_mm=substrate_height_mm,
                eps_r=eps_r,
                resolution=settings.MEEP_RESOLUTION
            )
            
            if not result['success']:
                # Fallback to analytical models if Meep fails
                logger.warning(f"Meep simulation failed: {result.get('error', 'Unknown error')}. Falling back to analytical models.")
                use_meep = False
            else:
                return {
                    "success": True,
                    "simulation_method": "Meep_FDTD",
                    "metrics": result['metrics'],
                    "s11_data": result.get('s11_data'),
                    "field_data": result.get('field_data')
                }
                
        except Exception as e:
            # Fallback to analytical models on exception
            logger.warning(f"Meep simulation error: {e}. Falling back to analytical models.", exc_info=True)
            use_meep = False
    else:
        logger.info("Meep not used (either disabled or not available). Using analytical models.")
        use_meep = False

    # Use analytical models (either as fallback or if use_meep is False)
    from sim.fitness import compute_fitness
    result = compute_fitness(
        params=params,
        target_frequency_ghz=request.target_frequency_ghz,
        target_bandwidth_mhz=project.bandwidth_mhz,
        use_meep=False
    )
    
    # Format metrics to match frontend expectations
    metrics = result.get('metrics', {})
    formatted_metrics = {
        "resonant_frequency_ghz": metrics.get('estimated_freq_ghz', request.target_frequency_ghz),
        "return_loss_dB": metrics.get('return_loss_dB', -15.0),
        "bandwidth_mhz": metrics.get('estimated_bandwidth_mhz', project.bandwidth_mhz),
        "gain_dbi": metrics.get('gain_estimate_dBi', 5.0),
        # Include original fields for compatibility
        "frequency_ghz": metrics.get('estimated_freq_ghz', request.target_frequency_ghz),
        "estimated_freq_ghz": metrics.get('estimated_freq_ghz'),
        "estimated_bandwidth_mhz": metrics.get('estimated_bandwidth_mhz'),
        "gain_estimate_dBi": metrics.get('gain_estimate_dBi')
    }
    
    return {
        "success": True,
        "simulation_method": "analytical",
        "metrics": formatted_metrics
    }


@router.post("/export-stl")
async def export_stl_endpoint(
    request: STLExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export antenna geometry as STL file for 3D printing/fabrication.
    """
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == request.project_id).first()
    if not project:
        raise ProjectNotFoundError(request.project_id)
    
    # Extract geometry parameters
    params = request.geometry_params
    
    try:
        import tempfile
        stl_file = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        stl_path = stl_file.name
        stl_file.close()
        
        success = export_stl(params, stl_path)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export STL file"
            )
        
        # Read STL file content
        with open(stl_path, 'rb') as f:
            stl_content = f.read()
        
        # Cleanup
        import os
        os.unlink(stl_path)
        
        # Return as base64 encoded
        import base64
        return {
            "success": True,
            "stl_file_base64": base64.b64encode(stl_content).decode('utf-8'),
            "filename": f"antenna_{request.project_id}_{params.get('length_mm', 30)}mm.stl"
        }
        
    except Exception as e:
        logger.error(f"STL export error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"STL export failed: {str(e)}"
        )


@router.get("/fields/{project_id}")
async def get_field_visualization(
    project_id: int,
    candidate_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get EM field visualization data from the most recent Meep simulation.
    
    Returns E-field, H-field, and current distribution data for visualization.
    """
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Get best design or specific candidate, or use default geometry
    params = None
    
    if candidate_id:
        from models.optimization import DesignCandidate, OptimizationRun
        candidate = db.query(DesignCandidate).join(OptimizationRun).filter(
            DesignCandidate.id == candidate_id,
            DesignCandidate.optimization_run_id.isnot(None),
            OptimizationRun.project_id == project_id
        ).first()
        if candidate:
            params = candidate.geometry_params
    
    if not params:
        # Try to get best design for project
        from models.optimization import DesignCandidate, OptimizationRun
        best_candidate = db.query(DesignCandidate).join(OptimizationRun).filter(
            OptimizationRun.project_id == project_id,
            DesignCandidate.optimization_run_id.isnot(None),
            DesignCandidate.is_best == True
        ).order_by(DesignCandidate.fitness.desc()).first()
        
        if best_candidate:
            params = best_candidate.geometry_params
    
    # If still no params, use default geometry based on project specs
    if not params:
        # Calculate default patch dimensions based on target frequency
        # Using simplified formula: L ≈ c / (2 * f * sqrt(eps_r))
        c = 299792458  # Speed of light in m/s
        target_freq_hz = project.target_frequency_ghz * 1e9
        eps_r = 4.4  # Default FR4
        # Approximate length for half-wavelength patch
        length_m = c / (2 * target_freq_hz * (eps_r ** 0.5))
        length_mm = length_m * 1000
        
        # Use reasonable defaults
        params = {
            "length_mm": min(length_mm, project.max_size_mm if project.max_size_mm else 50.0),
            "width_mm": min(length_mm * 1.5, project.max_size_mm if project.max_size_mm else 50.0),
            "substrate_height_mm": 1.6,
            "eps_r": 4.4
        }
        logger.info(f"No design candidate found for project {project_id}. Using default geometry: {params}")
    
    # Run simulation to get field data
    try:
        length_mm = params.get("length_mm", 30.0)
        width_mm = params.get("width_mm", 30.0)
        substrate_height_mm = params.get("substrate_height_mm", 1.6)
        eps_r = params.get("eps_r", 4.4)
        
        # Always attempt to run Meep for field visualization if enabled, but fall back to mock if it fails
        use_meep = check_meep_available() and settings.USE_MEEP
        
        # Try FDTD solver first (pure Python, always available)
        try:
            logger.info("Running 3D FDTD simulation...")
            result = simulate_patch_antenna_fdtd(
                length_mm=length_mm,
                width_mm=width_mm,
                target_freq_ghz=project.target_frequency_ghz,
                substrate_height_mm=substrate_height_mm,
                eps_r=eps_r,
                resolution=settings.MEEP_RESOLUTION
            )
            
            if result.get('success') and result.get('field_data'):
                # Extract field lines
                from sim.meep_simulator import _extract_field_lines
                import numpy as np
                
                E_field = result['field_data']['E_field']
                if E_field.get('Ex') and E_field.get('Ey'):
                    Ex_arr = np.array(E_field['Ex'])
                    Ey_arr = np.array(E_field['Ey'])
                    Ez_arr = np.array(E_field.get('Ez', [[0.0] * len(Ex_arr[0])] * len(Ex_arr)))
                    x_pts = np.array(E_field['x'])
                    y_pts = np.array(E_field['y'])
                    
                    field_lines = _extract_field_lines(Ex_arr, Ey_arr, Ez_arr, x_pts, y_pts)
                    E_field['_field_lines'] = field_lines
                
                H_field = result['field_data']['H_field']
                if H_field.get('Hx') and H_field.get('Hy'):
                    Hx_arr = np.array(H_field['Hx'])
                    Hy_arr = np.array(H_field['Hy'])
                    Hz_arr = np.array(H_field.get('Hz', [[0.0] * len(Hx_arr[0])] * len(Hx_arr)))
                    x_pts = np.array(H_field['x'])
                    y_pts = np.array(H_field['y'])
                    
                    field_lines = _extract_field_lines(Hx_arr, Hy_arr, Hz_arr, x_pts, y_pts)
                    H_field['_field_lines'] = field_lines
                
                return {
                    "success": True,
                    "field_data": result['field_data'],
                    "geometry_params": params,
                    "metrics": result.get('metrics', {}),
                    "simulation_method": "FDTD_3D",
                    "simulation_info": result.get('simulation_info', {})
                }
            else:
                logger.warning("FDTD simulation failed, falling back to analytical models.")
        except Exception as fdtd_error:
            logger.warning(f"FDTD simulation error: {fdtd_error}. Using analytical field data.", exc_info=True)
        
        # Fallback: Try Meep if available and enabled
        if use_meep and check_meep_available():
            try:
                result = simulate_patch_antenna(
                    length_mm=length_mm,
                    width_mm=width_mm,
                    target_freq_ghz=project.target_frequency_ghz,
                    substrate_height_mm=substrate_height_mm,
                    eps_r=eps_r,
                    resolution=settings.MEEP_RESOLUTION
                )
                
                if result.get('success') and result.get('field_data'):
                    return {
                        "success": True,
                        "field_data": result['field_data'],
                        "geometry_params": params,
                        "metrics": result.get('metrics', {}),
                        "simulation_method": "Meep_FDTD"
                    }
            except Exception as meep_error:
                logger.warning(f"Meep simulation failed: {meep_error}.")
        
        # Fallback to analytical field data (physics-based, always available)
        from sim.meep_simulator import generate_analytical_field_data
        analytical_field_data = generate_analytical_field_data(length_mm, width_mm, substrate_height_mm, project.target_frequency_ghz, eps_r)
        
        # Calculate approximate metrics for display
        from sim.models import estimate_patch_resonant_freq, estimate_bandwidth, estimate_gain
        estimated_freq = estimate_patch_resonant_freq(params)
        estimated_bw = estimate_bandwidth(params)
        estimated_gain = estimate_gain(params)
        
        return {
            "success": True,
            "field_data": analytical_field_data,
            "geometry_params": params,
            "metrics": {
                "resonant_frequency_ghz": estimated_freq,
                "bandwidth_mhz": estimated_bw,
                "gain_dbi": estimated_gain,
                "return_loss_dB": -15.0
            },
            "simulation_method": "analytical",
            "note": "Physics-based analytical field data (TM10 mode). FDTD simulation unavailable."
        }
                
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else f"{type(e).__name__}"
        logger.error(f"Error getting field visualization: {error_msg}", exc_info=True)
        # Always return analytical data even on error
        from sim.meep_simulator import generate_analytical_field_data
        length_mm = params.get("length_mm", 30.0)
        width_mm = params.get("width_mm", 30.0)
        substrate_height_mm = params.get("substrate_height_mm", 1.6)
        eps_r = params.get("eps_r", 4.4)
        analytical_field_data = generate_analytical_field_data(length_mm, width_mm, substrate_height_mm, project.target_frequency_ghz, eps_r)
        return {
            "success": True,
            "field_data": analytical_field_data,
            "geometry_params": params,
            "metrics": {},
            "simulation_method": "analytical",
            "note": f"Physics-based analytical field data generated due to error: {error_msg}"
        }


@router.get("/status")
def get_meep_status():
    """
    Check if Meep is available and configured.
    """
    try:
        meep_available = check_meep_available()
        
        note = None
        if not meep_available:
            note = "Meep is not installed. Install with: pip install meep or brew install meep. Using analytical models with mock field visualization."
        
        return {
            "enabled": settings.USE_MEEP,
            "available": meep_available and settings.USE_MEEP,
            "resolution": settings.MEEP_RESOLUTION,
            "note": note
        }
    except Exception as e:
        logger.error(f"Error checking Meep status: {e}", exc_info=True)
        return {
            "enabled": settings.USE_MEEP,
            "available": False,
            "error": str(e)
        }

