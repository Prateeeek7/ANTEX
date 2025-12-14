from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import logging
from db.base import get_db
from models.user import User
from models.project import AntennaProject
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from api.dependencies import get_current_user
from core.exceptions import ProjectNotFoundError, UnauthorizedProjectAccessError
from api.reports import generate_comprehensive_project_report
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new antenna project."""
    project = AntennaProject(
        user_id=current_user.id if current_user else 1,  # Use dev user if no auth
        **project_data.model_dump()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=ProjectListResponse)
def list_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects for the current user."""
    # In dev mode, show all projects if no auth
    projects = db.query(AntennaProject).offset(skip).limit(limit).all()
    total = db.query(AntennaProject).count()
    
    return ProjectListResponse(projects=projects, total=total)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project by ID."""
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Skip auth check in dev mode
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project."""
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project."""
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    db.delete(project)
    db.commit()
    return None


@router.get("/{project_id}/runs")
def get_project_runs(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all optimization runs for a project."""
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    from models.optimization import OptimizationRun
    runs = db.query(OptimizationRun).filter(
        OptimizationRun.project_id == project_id
    ).order_by(OptimizationRun.created_at.desc()).all()
    
    return runs


@router.get("/{project_id}/best-design")
def get_best_design(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the best design for a project."""
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    # Find best candidate across all optimization runs for this project
    from models.optimization import DesignCandidate, OptimizationRun
    
    best_candidate = db.query(DesignCandidate).join(OptimizationRun).filter(
        OptimizationRun.project_id == project_id,
        DesignCandidate.is_best == True
    ).order_by(DesignCandidate.fitness.desc()).first()
    
    if not best_candidate:
        return {"message": "No design candidates found for this project"}
    
    return {
        "candidate": {
            "id": best_candidate.id,
            "geometry_params": best_candidate.geometry_params,
            "fitness": best_candidate.fitness,
            "metrics": best_candidate.metrics,
        },
        "optimization_run_id": best_candidate.optimization_run_id
    }


@router.get("/{project_id}/comprehensive-report")
def generate_comprehensive_report(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive PDF report with ALL project findings:
    - Optimization runs
    - Design candidates
    - Simulation results
    - RF Analysis
    - Performance metrics
    """
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Get all optimization runs
    from models.optimization import OptimizationRun
    runs = db.query(OptimizationRun).filter(
        OptimizationRun.project_id == project_id
    ).order_by(OptimizationRun.created_at.desc()).all()
    
    optimization_runs_data = [{
        "id": run.id,
        "algorithm": run.algorithm.value if hasattr(run.algorithm, 'value') else str(run.algorithm),
        "status": run.status.value if hasattr(run.status, 'value') else str(run.status),
        "population_size": run.population_size,
        "generations": run.generations,
        "best_fitness": run.best_fitness,
        "created_at": run.created_at.isoformat() if run.created_at else None
    } for run in runs]
    
    # Get all design candidates
    from models.optimization import DesignCandidate
    candidates = db.query(DesignCandidate).join(OptimizationRun).filter(
        OptimizationRun.project_id == project_id
    ).all()
    
    design_candidates_data = [{
        "id": cand.id,
        "fitness": cand.fitness,
        "geometry_params": cand.geometry_params,
        "metrics": cand.metrics,
        "is_best": cand.is_best
    } for cand in candidates]
    
    # Get best design
    best_candidate = db.query(DesignCandidate).join(OptimizationRun).filter(
        OptimizationRun.project_id == project_id,
        DesignCandidate.is_best == True
    ).order_by(DesignCandidate.fitness.desc()).first()
    
    best_design_data = None
    if best_candidate:
        best_design_data = {
            "candidate": {
                "id": best_candidate.id,
                "fitness": best_candidate.fitness,
                "geometry_params": best_candidate.geometry_params,
                "metrics": best_candidate.metrics
            }
        }
    
    # Get simulation results and RF analysis from best candidate metrics
    simulation_results_data = None
    rf_analysis_data = None
    performance_metrics_data = None
    
    if best_candidate:
        metrics = best_candidate.metrics or {}
        
        # Extract simulation results from metrics
        if metrics:
            simulation_results_data = {
                "simulation_method": metrics.get("simulation_method", "analytical"),
                "metrics": {
                    "resonant_frequency_ghz": metrics.get("estimated_freq_ghz", project.target_frequency_ghz),
                    "frequency_ghz": metrics.get("estimated_freq_ghz", project.target_frequency_ghz),
                    "return_loss_dB": metrics.get("return_loss_dB", 0),
                    "s11_db": metrics.get("return_loss_dB", 0),
                    "bandwidth_mhz": metrics.get("estimated_bandwidth_mhz", metrics.get("bandwidth_mhz", project.bandwidth_mhz)),
                    "gain_dbi": metrics.get("gain_estimate_dBi", 0),
                    "gain_estimate_dBi": metrics.get("gain_estimate_dBi", 0),
                },
                "s11_data": metrics.get("s11_data")  # Include if available
            }
            
            # Extract RF analysis data from metrics
            impedance_data = metrics.get("estimated_impedance_ohm", {})
            if isinstance(impedance_data, dict):
                impedance_real = impedance_data.get("real", 50.0)
                impedance_imag = impedance_data.get("imag", 0.0)
            else:
                # Handle case where impedance might be a complex number or scalar
                impedance_real = float(impedance_data) if isinstance(impedance_data, (int, float)) else 50.0
                impedance_imag = 0.0
            
            vswr = metrics.get("vswr", 0)
            return_loss_db = metrics.get("return_loss_dB", 0)
            
            # Determine if matched (VSWR < 2.0 is generally considered matched)
            matched = vswr > 0 and vswr < 2.0
            
            # Try to get detailed RF analysis if available (with matching networks)
            rf_analysis_data = {
                "impedance_real": impedance_real,
                "impedance_imag": impedance_imag,
                "vswr": vswr,
                "return_loss_db": return_loss_db,
                "matched": matched,
                "target_impedance_ohm": project.target_impedance_ohm if hasattr(project, 'target_impedance_ohm') else 50.0
            }
            
            # Try to get AI recommendations from analysis API if available
            if not matched:
                try:
                    from api.routers.analysis import _generate_ai_matching_recommendations
                    z_antenna = complex(impedance_real, impedance_imag)
                    ai_matching_recs = _generate_ai_matching_recommendations(
                        z_antenna, vswr, return_loss_db, matched, [], rf_analysis_data["target_impedance_ohm"]
                    )
                    rf_analysis_data["ai_recommendations"] = ai_matching_recs
                except Exception as e:
                    logger.warning(f"Could not generate RF matching recommendations: {e}")
        
        # Compute performance metrics from best candidate
        performance_metrics_data = {
            "overall_score": best_candidate.fitness * 100,  # Scale fitness to 0-100
            "resonant_frequency_ghz": metrics.get("estimated_freq_ghz", project.target_frequency_ghz),
            "target_frequency_ghz": project.target_frequency_ghz,
            "frequency_error_percent": abs((metrics.get("estimated_freq_ghz", project.target_frequency_ghz) - project.target_frequency_ghz) / project.target_frequency_ghz * 100) if project.target_frequency_ghz > 0 else 0,
            "bandwidth_mhz": metrics.get("estimated_bandwidth_mhz", metrics.get("bandwidth_mhz", project.bandwidth_mhz)),
            "target_bandwidth_mhz": project.bandwidth_mhz,
            "gain_dbi": metrics.get("gain_estimate_dBi", 0),
            "return_loss_db": metrics.get("return_loss_dB", 0),
            "vswr": metrics.get("vswr", 0),
        }
    
    # Generate project data
    project_data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "target_frequency_ghz": project.target_frequency_ghz,
        "bandwidth_mhz": project.bandwidth_mhz,
        "max_size_mm": project.max_size_mm,
        "substrate": project.substrate,
        "status": project.status.value if hasattr(project.status, 'value') else str(project.status),
        "created_at": project.created_at.isoformat() if project.created_at else None
    }
    
    try:
        # Generate PDF
        pdf_bytes = generate_comprehensive_project_report(
            project_data=project_data,
            optimization_runs=optimization_runs_data,
            design_candidates=design_candidates_data,
            best_design=best_design_data,
            simulation_results=simulation_results_data,
            rf_analysis=rf_analysis_data,
            performance_metrics=performance_metrics_data
        )
        
        # Ensure pdf_bytes is actually bytes (not string or other type)
        if not isinstance(pdf_bytes, bytes):
            if isinstance(pdf_bytes, str):
                pdf_bytes = pdf_bytes.encode('utf-8')
            else:
                pdf_bytes = bytes(pdf_bytes)
        
        # Verify it's a valid PDF (check magic bytes)
        if len(pdf_bytes) < 4 or pdf_bytes[:4] != b'%PDF':
            logger.error(f"Invalid PDF generated: first 20 bytes: {pdf_bytes[:20]}")
            raise ValueError("Generated content is not a valid PDF")
        
        # Return PDF response with proper encoding
        filename = f"antenna_design_report_{project.name.replace(' ', '_')}_{project_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        logger.info(f"Sending PDF report: {len(pdf_bytes)} bytes, filename: {filename}")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF report: {str(e)}"
        )


