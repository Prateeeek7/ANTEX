from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.base import Base


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    running = "running"
    completed = "completed"
    failed = "failed"


class AntennaProject(Base):
    __tablename__ = "antenna_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_frequency_ghz = Column(Float, nullable=False)
    bandwidth_mhz = Column(Float, nullable=False)
    max_size_mm = Column(Float, nullable=False)
    substrate = Column(String, nullable=False)
    
    # New parameters for accurate design
    substrate_thickness_mm = Column(Float, default=1.6, nullable=False)  # Default FR4 thickness
    feed_type = Column(String, default="microstrip", nullable=False)  # microstrip, coaxial, inset, probe
    polarization = Column(String, default="linear_vertical", nullable=False)  # linear_vertical, linear_horizontal, circular_rhcp, circular_lhcp
    target_gain_dbi = Column(Float, default=5.0, nullable=False)  # Target gain in dBi
    target_impedance_ohm = Column(Float, default=50.0, nullable=False)  # Target impedance (usually 50 ohm)
    conductor_thickness_um = Column(Float, default=35.0, nullable=False)  # Copper thickness in micrometers (1 oz = 35um)
    
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.draft, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    geometry_params = relationship("GeometryParamSet", back_populates="project", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="project", cascade="all, delete-orphan")


