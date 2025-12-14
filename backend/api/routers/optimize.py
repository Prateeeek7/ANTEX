from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from db.base import get_db
from models.user import User
from models.project import AntennaProject
from models.optimization import OptimizationRun, OptimizationAlgorithm, OptimizationStatus, DesignCandidate
from schemas.optimization import OptimizationConfig, OptimizationResult, OptimizationRunResponse, DesignCandidateResponse
from api.dependencies import get_current_user
from core.exceptions import ProjectNotFoundError, UnauthorizedProjectAccessError, OptimizationRunNotFoundError
from optim.runner import run_optimization
from models.geometry import DesignType
from db.base import SessionLocal
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def run_optimization_background(
    run_id: int,
    project_id: int,
    design_type: DesignType,
    algorithm: OptimizationAlgorithm,
    population_size: int,
    generations: int,
    constraints: dict
):
    """
    Run optimization in background thread.
    
    CRITICAL: This function MUST handle all exceptions and update the run status.
    If an exception is not caught, the run will remain stuck in "running" status.
    """
    db = SessionLocal()
    opt_run = None
    try:
        # Get optimization run record first
        opt_run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
        if not opt_run:
            logger.error(f"Optimization run {run_id} not found in database")
            return
        
        # Get project
        project = db.query(AntennaProject).filter(AntennaProject.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found for run {run_id}")
            opt_run.status = OptimizationStatus.failed
            opt_run.log = {"error": f"Project {project_id} not found"}
            db.commit()
            return
        
        logger.info(f"Starting background optimization run {run_id} for project {project_id}")
        
        # Run optimization - this will update the run status internally
        run_optimization(
            project=project,
            design_type=design_type,
            algorithm=algorithm,
            population_size=population_size,
            generations=generations,
            constraints=constraints or {},
            db=db
        )
        
        logger.info(f"Completed optimization run {run_id}")
        
    except KeyboardInterrupt:
        # Don't mark as failed for keyboard interrupts
        logger.warning(f"Optimization run {run_id} interrupted by user")
        if opt_run:
            opt_run.status = OptimizationStatus.failed
            opt_run.log = {"error": "Optimization interrupted by user"}
            db.commit()
        raise  # Re-raise to let FastAPI handle it
    
    except Exception as e:
        # CRITICAL: Catch ALL exceptions to prevent runs from getting stuck
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        error_type = type(e).__name__
        
        logger.error(f"Optimization run {run_id} failed: {error_msg}", exc_info=True)
        logger.error(f"Error type: {error_type}")
        logger.error(f"Full traceback:\n{error_trace}")
        
        # Update run status - use a new session if current one is invalid
        try:
            if opt_run:
                opt_run.status = OptimizationStatus.failed
                opt_run.log = {
                    "error": error_msg,
                    "error_type": error_type,
                    "traceback": error_trace
                }
                db.commit()
            else:
                # If opt_run is None, create new session
                db2 = SessionLocal()
                try:
                    opt_run2 = db2.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
                    if opt_run2:
                        opt_run2.status = OptimizationStatus.failed
                        opt_run2.log = {
                            "error": error_msg,
                            "error_type": error_type,
                            "traceback": error_trace
                        }
                        db2.commit()
                finally:
                    db2.close()
        except Exception as db_error:
            logger.error(f"Failed to update optimization run status in database: {db_error}")
    
    finally:
        # Always close the database session
        try:
            db.close()
        except Exception:
            pass  # Ignore errors when closing


@router.post("/start", response_model=OptimizationRunResponse)
def start_optimization(
    config: OptimizationConfig,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start an optimization run (runs asynchronously in background)."""
    # Validate project
    project = db.query(AntennaProject).filter(AntennaProject.id == config.project_id).first()
    if not project:
        raise ProjectNotFoundError(config.project_id)
    
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    # Create optimization run record with "pending" status
    opt_run = OptimizationRun(
        project_id=config.project_id,
        algorithm=config.algorithm,
        population_size=config.population_size,
        generations=config.generations,
        status=OptimizationStatus.running
    )
    db.add(opt_run)
    db.commit()
    db.refresh(opt_run)
    
    # Start optimization in background
    background_tasks.add_task(
        run_optimization_background,
        run_id=opt_run.id,
        project_id=config.project_id,
        design_type=config.design_type,
        algorithm=config.algorithm,
        population_size=config.population_size,
        generations=config.generations,
        constraints=config.constraints or {}
    )
    
    return opt_run


@router.get("/run/{run_id}", response_model=OptimizationRunResponse)
def get_optimization_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get optimization run details."""
    opt_run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    if not opt_run:
        raise OptimizationRunNotFoundError(run_id)
    
    # Verify user owns the project
    project = db.query(AntennaProject).filter(AntennaProject.id == opt_run.project_id).first()
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    return opt_run


@router.get("/run/{run_id}/candidates", response_model=list[DesignCandidateResponse])
def get_run_candidates(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all candidates from an optimization run."""
    opt_run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    if not opt_run:
        raise OptimizationRunNotFoundError(run_id)
    
    # Verify user owns the project
    project = db.query(AntennaProject).filter(AntennaProject.id == opt_run.project_id).first()
    # Auth disabled - skip user check
    # if project.user_id != current_user.id:
    #     raise UnauthorizedProjectAccessError()
    
    candidates = db.query(DesignCandidate).filter(
        DesignCandidate.optimization_run_id == run_id
    ).order_by(DesignCandidate.fitness.desc()).all()
    
    return candidates


