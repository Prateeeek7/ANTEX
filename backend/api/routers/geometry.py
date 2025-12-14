"""
Geometry API endpoints for multi-shape antenna design system.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.base import get_db
from models.user import User
from api.dependencies import get_current_user
from sim.geometry_framework import (
    list_shape_families,
    get_shape_family,
    auto_design_geometry,
    validate_geometry_params,
    AntennaShapeFamily,
)
from sim.geometry_renderer import GeometryRenderer
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class GeometryRenderRequest(BaseModel):
    """Request for geometry rendering."""
    shape_family: str
    parameters: Dict[str, float]
    include_annotations: bool = True
    include_substrate: bool = True


class AutoDesignRequest(BaseModel):
    """Request for auto-design."""
    shape_family: str
    target_frequency_ghz: float
    substrate: Optional[str] = None  # Substrate name (e.g., "FR4", "Rogers RT/duroid 5880")
    substrate_eps_r: Optional[float] = None  # Will be looked up if substrate name provided
    substrate_height_mm: float = 1.6


@router.get("/shape-families")
async def get_shape_families(
    current_user: User = Depends(get_current_user)
):
    """Get list of all available antenna shape families."""
    families = list_shape_families()
    return {"shape_families": families}


@router.get("/shape-families/{family_name}")
async def get_shape_family_details(
    family_name: str,
    substrate: Optional[str] = Query(None, description="Substrate name to override eps_r default"),
    substrate_thickness_mm: Optional[float] = Query(None, description="Substrate thickness to override default"),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed definition of a shape family.
    
    CRITICAL: If substrate is provided, eps_r default_value is looked up from material properties.
    If substrate_thickness_mm is provided, substrate_height_mm default_value is overridden.
    """
    family_def = get_shape_family(family_name)
    if not family_def:
        raise HTTPException(status_code=404, detail=f"Shape family '{family_name}' not found")
    
    # Get eps_r from substrate if provided
    eps_r_default = None
    if substrate:
        from sim.material_properties import get_substrate_properties
        try:
            material_props = get_substrate_properties(substrate)
            eps_r_default = material_props["permittivity"]
            logger.info(f"Shape family details: Using {substrate} with ε_r={eps_r_default:.3f}")
        except Exception as e:
            logger.warning(f"Failed to get properties for {substrate}: {e}, using framework default")
    
    # Build parameters list with overridden defaults if needed
    parameters = []
    for p in family_def.parameters:
        default_value = p.default_value
        
        # Override eps_r default if substrate provided
        if p.name == "eps_r" and eps_r_default is not None:
            default_value = eps_r_default
        
        # Override substrate_height_mm default if provided
        if p.name == "substrate_height_mm" and substrate_thickness_mm is not None:
            default_value = substrate_thickness_mm
        
        parameters.append({
            "name": p.name,
            "min_value": p.min_value,
            "max_value": p.max_value,
            "default_value": default_value,
            "unit": p.unit,
            "description": p.description,
        })
    
    return {
        "family": family_def.family.value,
        "display_name": family_def.display_name,
        "description": family_def.description,
        "parameters": parameters,
        "auto_design_enabled": family_def.auto_design_enabled,
    }


@router.post("/auto-design")
async def auto_design(
    request: AutoDesignRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Auto-design geometry based on target frequency.
    
    CRITICAL: Uses substrate name to look up correct eps_r.
    If substrate name is provided, eps_r is looked up from material properties.
    Otherwise, uses provided eps_r or defaults to 4.4 (FR4).
    """
    try:
        family = AntennaShapeFamily(request.shape_family)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid shape family: {request.shape_family}")
    
    # Get eps_r from substrate name if provided
    eps_r = request.substrate_eps_r
    if request.substrate and not eps_r:
        from sim.material_properties import get_substrate_properties
        try:
            material_props = get_substrate_properties(request.substrate)
            eps_r = material_props["permittivity"]
            logger.info(f"Auto-design: Using {request.substrate} with ε_r={eps_r:.3f}")
        except Exception as e:
            logger.warning(f"Failed to get properties for {request.substrate}: {e}, using default")
            eps_r = 4.4  # Default to FR4
    elif not eps_r:
        eps_r = 4.4  # Default to FR4
    
    params = auto_design_geometry(
        family,
        request.target_frequency_ghz,
        eps_r,
        request.substrate_height_mm
    )
    
    return {
        "shape_family": request.shape_family,
        "target_frequency_ghz": request.target_frequency_ghz,
        "parameters": params,
    }


@router.post("/render")
async def render_geometry(
    request: GeometryRenderRequest,
    format: str = Query("json", regex="^(json|svg)$"),
    current_user: User = Depends(get_current_user)
):
    """Render geometry to specified format."""
    # Validate parameters
    is_valid, errors = validate_geometry_params(request.shape_family, request.parameters)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {errors}")
    
    # Render geometry
    renderer = GeometryRenderer()
    geometry = renderer.render_geometry(
        request.shape_family,
        request.parameters,
        request.include_annotations,
        request.include_substrate
    )
    
    if format == "svg":
        svg_content = renderer.to_svg(geometry)
        return {
            "format": "svg",
            "content": svg_content,
            "geometry": geometry,  # Also include JSON for frontend use
        }
    else:
        return {
            "format": "json",
            "geometry": geometry,
        }


@router.post("/validate")
async def validate_parameters(
    shape_family: str,
    parameters: Dict[str, float],
    current_user: User = Depends(get_current_user)
):
    """Validate geometry parameters."""
    is_valid, errors = validate_geometry_params(shape_family, parameters)
    return {
        "valid": is_valid,
        "errors": errors,
    }



