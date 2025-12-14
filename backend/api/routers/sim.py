from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.base import get_db
from models.user import User
from models.project import AntennaProject
from models.optimization import DesignCandidate
from models.geometry import GeometryParamSet, GeneratedBy
from schemas.optimization import DesignCandidateResponse
from api.dependencies import get_current_user
from core.exceptions import ProjectNotFoundError, UnauthorizedProjectAccessError
from sim.importers import parse_hfss_result, parse_cst_result
import tempfile
import os

router = APIRouter()


@router.post("/upload/{project_id}")
async def upload_simulation_result(
    project_id: int,
    file: UploadFile = File(...),
    simulation_tool: str = "hfss",  # "hfss" or "cst"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse HFSS/CST simulation results."""
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Parse simulation results
        if simulation_tool.lower() == "hfss":
            parsed_data = parse_hfss_result(tmp_path)
        elif simulation_tool.lower() == "cst":
            parsed_data = parse_cst_result(tmp_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="simulation_tool must be 'hfss' or 'cst'"
            )
        
        # Create design candidate from external simulation
        # Note: We don't have geometry params from the file, so we create a minimal candidate
        # In a real implementation, you'd extract geometry from the simulation file
        candidate = DesignCandidate(
            optimization_run_id=None,  # External simulation, not from optimization
            geometry_params={},  # Would need to extract from file
            fitness=0.0,  # Would compute from metrics
            metrics={
                "frequency_ghz": parsed_data.get("frequency_ghz", 0),
                "return_loss_dB": parsed_data.get("return_loss_dB", 0),
                "gain_dBi": parsed_data.get("gain_dBi", 0),
                "bandwidth_mhz": parsed_data.get("bandwidth_mhz", 0),
                "source": parsed_data.get("source", simulation_tool)
            },
            is_best=False
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return {
            "message": "Simulation result uploaded and parsed",
            "candidate_id": candidate.id,
            "metrics": candidate.metrics
        }
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/candidates/{project_id}", response_model=List[DesignCandidateResponse])
def get_simulation_candidates(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all simulation-based candidates for a project."""
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(project_id)
    
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    # Get all candidates from optimization runs for this project
    from models.optimization import OptimizationRun
    
    candidates = db.query(DesignCandidate).join(OptimizationRun).filter(
        OptimizationRun.project_id == project_id
    ).order_by(DesignCandidate.fitness.desc()).all()
    
    return candidates


