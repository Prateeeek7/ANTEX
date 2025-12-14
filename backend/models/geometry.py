from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.base import Base


class DesignType(str, enum.Enum):
    patch = "patch"
    slot = "slot"
    fractal = "fractal"
    custom = "custom"


class GeneratedBy(str, enum.Enum):
    user = "user"
    ga = "ga"
    pso = "pso"
    nn = "nn"
    external = "external"


class GeometryParamSet(Base):
    __tablename__ = "geometry_param_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("antenna_projects.id"), nullable=False)
    design_type = Column(SQLEnum(DesignType), nullable=False)
    parameters = Column(JSON, nullable=False)  # JSONB in PostgreSQL
    generated_by = Column(SQLEnum(GeneratedBy), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("AntennaProject", back_populates="geometry_params")





