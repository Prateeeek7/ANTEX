"""
Parameter space definitions for different antenna design types.
"""
from typing import Dict, List, Tuple, Any
import random
from models.geometry import DesignType


def get_param_space(design_type: DesignType, constraints: Dict[str, Any] = None) -> Dict[str, Tuple[float, float]]:
    """
    Get parameter bounds for a given design type.
    
    Returns:
        Dict mapping parameter names to (min, max) tuples
    """
    if constraints is None:
        constraints = {}
    
    # Check for shape_family in constraints (for specific patch shapes)
    shape_family = constraints.get("shape_family", "rectangular_patch")
    
    if design_type == DesignType.patch:
        # CRITICAL: Respect max_size_mm constraint from project
        max_size_mm = constraints.get("max_size_mm", 50.0)
        min_size_mm = constraints.get("min_size_mm", 10.0)
        
        # Star patch uses different parameters
        if shape_family == "star_patch":
            max_radius = max_size_mm / 2  # Radius constraint based on max_size
            return {
                "outer_radius_mm": (
                    constraints.get("min_outer_radius_mm", 10.0),
                    constraints.get("max_outer_radius_mm", min(max_radius, 150.0))
                ),
                "inner_radius_mm": (
                    constraints.get("min_inner_radius_mm", 5.0),
                    constraints.get("max_inner_radius_mm", min(max_radius * 0.7, 100.0))
                ),
                "num_points": (
                    constraints.get("min_num_points", 4),
                    constraints.get("max_num_points", 12)
                ),
                "substrate_height_mm": (
                    constraints.get("min_substrate_height_mm", 0.5),
                    constraints.get("max_substrate_height_mm", 3.0)
                ),
                "eps_r": (
                    constraints.get("min_eps_r", 2.2),
                    constraints.get("max_eps_r", 10.0)
                ),
                "feed_offset_mm": (
                    constraints.get("min_feed_offset_mm", -10.0),
                    constraints.get("max_feed_offset_mm", 10.0)
                ),
            }
        
        # Default rectangular patch parameters
        return {
            "length_mm": (
                constraints.get("min_length_mm", min_size_mm),
                constraints.get("max_length_mm", max_size_mm)
            ),
            "width_mm": (
                constraints.get("min_width_mm", min_size_mm),
                constraints.get("max_width_mm", max_size_mm)
            ),
            "substrate_height_mm": (
                constraints.get("min_substrate_height_mm", 0.5),
                constraints.get("max_substrate_height_mm", 3.0)
            ),
            "eps_r": (
                constraints.get("min_eps_r", 2.2),
                constraints.get("max_eps_r", 10.0)
            ),
            "feed_offset_mm": (
                constraints.get("min_feed_offset_mm", -10.0),
                constraints.get("max_feed_offset_mm", 10.0)
            ),
        }
    elif design_type == DesignType.slot:
        return {
            "length_mm": (
                constraints.get("min_length_mm", 20.0),
                constraints.get("max_length_mm", 60.0)
            ),
            "width_mm": (
                constraints.get("min_width_mm", 20.0),
                constraints.get("max_width_mm", 60.0)
            ),
            "slot_length_mm": (
                constraints.get("min_slot_length_mm", 5.0),
                constraints.get("max_slot_length_mm", 30.0)
            ),
            "slot_width_mm": (
                constraints.get("min_slot_width_mm", 1.0),
                constraints.get("max_slot_width_mm", 5.0)
            ),
            "substrate_height_mm": (
                constraints.get("min_substrate_height_mm", 0.5),
                constraints.get("max_substrate_height_mm", 3.0)
            ),
            "eps_r": (
                constraints.get("min_eps_r", 2.2),
                constraints.get("max_eps_r", 10.0)
            ),
        }
    elif design_type == DesignType.fractal:
        return {
            "iterations": (1, 4),  # Integer, but we'll treat as float and round
            "scale_factor": (0.3, 0.7),
            "base_length_mm": (
                constraints.get("min_length_mm", 15.0),
                constraints.get("max_length_mm", 40.0)
            ),
            "base_width_mm": (
                constraints.get("min_width_mm", 15.0),
                constraints.get("max_width_mm", 40.0)
            ),
            "substrate_height_mm": (
                constraints.get("min_substrate_height_mm", 0.5),
                constraints.get("max_substrate_height_mm", 3.0)
            ),
            "eps_r": (
                constraints.get("min_eps_r", 2.2),
                constraints.get("max_eps_r", 10.0)
            ),
        }
    else:
        # Default/custom: use patch-like parameters
        return get_param_space(DesignType.patch, constraints)


def sample_random_params(design_type: DesignType, constraints: Dict[str, Any] = None) -> Dict[str, float]:
    """Sample a random parameter set within bounds."""
    space = get_param_space(design_type, constraints)
    params = {}
    for param_name, (min_val, max_val) in space.items():
        if param_name == "iterations" or param_name == "num_points":
            params[param_name] = int(random.uniform(min_val, max_val + 1))
        else:
            params[param_name] = random.uniform(min_val, max_val)
    return params


def normalize_params(params: Dict[str, float], design_type: DesignType, constraints: Dict[str, Any] = None) -> List[float]:
    """Normalize parameters to [0, 1] range for optimization algorithms."""
    space = get_param_space(design_type, constraints)
    normalized = []
    for param_name in sorted(space.keys()):
        min_val, max_val = space[param_name]
        if max_val == min_val:
            normalized.append(0.0)
        else:
            normalized.append((params.get(param_name, min_val) - min_val) / (max_val - min_val))
    return normalized


def denormalize_params(normalized: List[float], design_type: DesignType, constraints: Dict[str, Any] = None) -> Dict[str, float]:
    """
    Convert normalized parameters back to actual values.
    
    CRITICAL: Validates that geometry respects max_size_mm constraint.
    Ensures length and width don't exceed max_size_mm.
    """
    space = get_param_space(design_type, constraints)
    param_names = sorted(space.keys())
    params = {}
    max_size_mm = constraints.get("max_size_mm") if constraints else None
    
    for i, param_name in enumerate(param_names):
        min_val, max_val = space[param_name]
        # Clamp to [0, 1]
        n = max(0.0, min(1.0, normalized[i]))
        value = min_val + n * (max_val - min_val)
        
        # Apply max_size constraint for length and width
        if max_size_mm and param_name in ["length_mm", "width_mm"]:
            value = min(value, max_size_mm)
        
        if param_name == "iterations" or param_name == "num_points":
            params[param_name] = int(round(value))
        else:
            params[param_name] = value
    
    # Add shape_family to params if it's in constraints (for rendering)
    if constraints and "shape_family" in constraints:
        params["shape_family"] = constraints["shape_family"]
    
    # CRITICAL: Ensure both length and width respect max_size_mm
    if max_size_mm:
        if "length_mm" in params:
            params["length_mm"] = min(params["length_mm"], max_size_mm)
        if "width_mm" in params:
            params["width_mm"] = min(params["width_mm"], max_size_mm)
    
    return params




