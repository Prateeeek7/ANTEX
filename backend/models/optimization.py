from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.base import Base


class OptimizationAlgorithm(str, enum.Enum):
    ga = "ga"
    pso = "pso"
    hybrid = "hybrid"


class OptimizationStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("antenna_projects.id"), nullable=False)
    algorithm = Column(SQLEnum(OptimizationAlgorithm), nullable=False)
    population_size = Column(Integer, nullable=False)
    generations = Column(Integer, nullable=False)
    status = Column(SQLEnum(OptimizationStatus), default=OptimizationStatus.pending, nullable=False)
    best_fitness = Column(Float, nullable=True)
    log = Column(JSON, nullable=True)  # Store history and metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("AntennaProject", back_populates="optimization_runs")
    candidates = relationship("DesignCandidate", back_populates="optimization_run", cascade="all, delete-orphan")


class DesignCandidate(Base):
    __tablename__ = "design_candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    optimization_run_id = Column(Integer, ForeignKey("optimization_runs.id"), nullable=True)
    geometry_params = Column(JSON, nullable=False)
    fitness = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=False)  # return_loss_dB, bandwidth_mhz, gain_dBi, etc.
    is_best = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    optimization_run = relationship("OptimizationRun", back_populates="candidates")





