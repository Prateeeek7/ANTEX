from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from models.optimization import OptimizationAlgorithm, OptimizationStatus
from models.geometry import DesignType


class OptimizationConfig(BaseModel):
    project_id: int
    design_type: DesignType
    algorithm: OptimizationAlgorithm
    population_size: int = 30
    generations: int = 40
    constraints: Optional[dict[str, Any]] = None


class OptimizationHistory(BaseModel):
    generation: int
    best_fitness: float
    avg_fitness: float


class OptimizationResult(BaseModel):
    run_id: int
    best_candidate: dict[str, Any]
    history: list[OptimizationHistory]
    metrics: dict[str, Any]


class OptimizationRunResponse(BaseModel):
    id: int
    project_id: int
    algorithm: OptimizationAlgorithm
    population_size: int
    generations: int
    status: OptimizationStatus
    best_fitness: Optional[float] = None
    log: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DesignCandidateResponse(BaseModel):
    id: int
    optimization_run_id: Optional[int] = None
    geometry_params: dict[str, Any]
    fitness: float
    metrics: dict[str, Any]
    is_best: bool
    created_at: datetime
    
    class Config:
        from_attributes = True





