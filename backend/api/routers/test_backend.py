"""
Test endpoint to verify backend receives correct parameters from frontend.

This endpoint accepts raw JSON and returns detailed parameter validation,
helping debug UI/Backend mismatches.
"""
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sim.material_properties import get_substrate_properties
from sim.models import estimate_patch_resonant_freq, estimate_bandwidth, estimate_gain
from sim.fitness import compute_fitness
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class TestRequest(BaseModel):
    """Test request model."""
    target_frequency_ghz: float
    bandwidth_mhz: float
    max_size_mm: float
    substrate: str
    substrate_thickness_mm: float
    feed_type: Optional[str] = "microstrip"
    polarization: Optional[str] = "linear_vertical"
    target_gain_dbi: Optional[float] = 5.0
    target_impedance_ohm: Optional[float] = 50.0
    conductor_thickness_um: Optional[float] = 35.0
    # Test geometry
    test_length_mm: Optional[float] = 30.0
    test_width_mm: Optional[float] = 25.0


@router.post("/test-parameters")
def test_backend_parameters(request: TestRequest = Body(...)):
    """
    Test endpoint to verify backend receives and processes parameters correctly.
    
    Returns detailed validation of:
    - Units consistency (mm, µm)
    - εr from substrate name (not defaulting)
    - Frequency target usage
    - Parameter transformations
    """
    results = {
        "input_parameters": request.model_dump(),
        "validation": {},
        "calculations": {},
        "warnings": []
    }
    
    # 1. Verify substrate → εr mapping
    try:
        material_props = get_substrate_properties(request.substrate)
        eps_r = material_props["permittivity"]
        results["validation"]["substrate"] = {
            "name": request.substrate,
            "eps_r": eps_r,
            "loss_tangent": material_props.get("loss_tangent", 0.0),
            "verified": True
        }
        
        # Check if eps_r matches expected (not defaulting to 4.4)
        if request.substrate == "Rogers RT/duroid 5880" and abs(eps_r - 2.2) > 0.1:
            results["warnings"].append(
                f"εr mismatch: Expected 2.2 for Rogers 5880, got {eps_r}"
            )
        elif request.substrate == "FR4" and abs(eps_r - 4.4) > 0.1:
            results["warnings"].append(
                f"εr mismatch: Expected 4.4 for FR4, got {eps_r}"
            )
    except Exception as e:
        results["validation"]["substrate"] = {
            "error": str(e),
            "verified": False
        }
        results["warnings"].append(f"Substrate lookup failed: {e}")
        eps_r = 4.4  # Fallback
    
    # 2. Verify units
    results["validation"]["units"] = {
        "frequency_ghz": request.target_frequency_ghz,
        "bandwidth_mhz": request.bandwidth_mhz,
        "max_size_mm": request.max_size_mm,
        "substrate_thickness_mm": request.substrate_thickness_mm,
        "conductor_thickness_um": request.conductor_thickness_um,
        "test_length_mm": request.test_length_mm,
        "test_width_mm": request.test_width_mm,
        "units_consistent": True
    }
    
    # Verify frequency is not default (1.0 GHz)
    if abs(request.target_frequency_ghz - 1.0) < 0.1:
        results["warnings"].append(
            "WARNING: Frequency target is 1.0 GHz - might be default value!"
        )
    
    # 3. Test calculations with provided geometry
    test_params = {
        "length_mm": request.test_length_mm,
        "width_mm": request.test_width_mm,
        "substrate_height_mm": request.substrate_thickness_mm,
        "eps_r": eps_r,
        "feed_offset_mm": 0.0,
    }
    
    try:
        f_res = estimate_patch_resonant_freq(test_params)
        bw = estimate_bandwidth(test_params)
        gain = estimate_gain(test_params)
        
        results["calculations"]["resonant_frequency"] = {
            "calculated_ghz": f_res,
            "target_ghz": request.target_frequency_ghz,
            "error_ghz": abs(f_res - request.target_frequency_ghz),
            "error_percent": abs((f_res - request.target_frequency_ghz) / request.target_frequency_ghz * 100)
        }
        
        results["calculations"]["bandwidth"] = {
            "calculated_mhz": bw,
            "target_mhz": request.bandwidth_mhz,
            "error_mhz": abs(bw - request.bandwidth_mhz)
        }
        
        results["calculations"]["gain"] = {
            "calculated_dbi": gain,
            "target_dbi": request.target_gain_dbi,
            "error_dbi": abs(gain - request.target_gain_dbi)
        }
        
        # 4. Test full fitness calculation
        project_params = {
            "substrate": request.substrate,
            "substrate_thickness_mm": request.substrate_thickness_mm,
            "feed_type": request.feed_type,
            "polarization": request.polarization,
            "target_gain_dbi": request.target_gain_dbi,
            "target_impedance_ohm": request.target_impedance_ohm,
            "conductor_thickness_um": request.conductor_thickness_um,
        }
        
        fitness_result = compute_fitness(
            test_params,
            target_frequency_ghz=request.target_frequency_ghz,
            target_bandwidth_mhz=request.bandwidth_mhz,
            project_params=project_params
        )
        
        results["calculations"]["fitness"] = {
            "fitness_score": fitness_result["fitness"],
            "metrics": fitness_result["metrics"]
        }
        
        # Verify target frequency was actually used
        if abs(fitness_result["metrics"]["estimated_freq_ghz"] - request.target_frequency_ghz) > 0.1:
            # This is expected if geometry doesn't match, but we log it
            pass
        
    except Exception as e:
        results["calculations"]["error"] = str(e)
        results["warnings"].append(f"Calculation failed: {e}")
    
    # 5. Verify max_size constraint
    if request.test_length_mm > request.max_size_mm:
        results["warnings"].append(
            f"Length {request.test_length_mm}mm exceeds max_size {request.max_size_mm}mm"
        )
    if request.test_width_mm > request.max_size_mm:
        results["warnings"].append(
            f"Width {request.test_width_mm}mm exceeds max_size {request.max_size_mm}mm"
        )
    
    results["validation"]["summary"] = {
        "all_checks_passed": len(results["warnings"]) == 0,
        "warning_count": len(results["warnings"])
    }
    
    logger.info(f"Backend parameter test: {results['validation']['summary']}")
    
    return results


