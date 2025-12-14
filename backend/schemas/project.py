from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.project import ProjectStatus
from models.geometry import DesignType, GeneratedBy


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_frequency_ghz: float
    bandwidth_mhz: float
    max_size_mm: float
    substrate: str
    
    # New parameters for accurate design
    substrate_thickness_mm: float = 1.6
    feed_type: str = "microstrip"  # microstrip, coaxial, inset, probe
    polarization: str = "linear_vertical"  # linear_vertical, linear_horizontal, circular_rhcp, circular_lhcp
    target_gain_dbi: float = 5.0
    target_impedance_ohm: float = 50.0
    conductor_thickness_um: float = 35.0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_frequency_ghz: Optional[float] = None
    bandwidth_mhz: Optional[float] = None
    max_size_mm: Optional[float] = None
    substrate: Optional[str] = None
    substrate_thickness_mm: Optional[float] = None
    feed_type: Optional[str] = None
    polarization: Optional[str] = None
    target_gain_dbi: Optional[float] = None
    target_impedance_ohm: Optional[float] = None
    conductor_thickness_um: Optional[float] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int


