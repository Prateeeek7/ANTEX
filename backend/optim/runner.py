"""
Optimization runner that orchestrates GA/PSO and persists results.
"""
from typing import Dict, Any
import logging
from sqlalchemy.orm import Session
from models.project import AntennaProject
from models.optimization import OptimizationRun, DesignCandidate, OptimizationAlgorithm, OptimizationStatus
from models.geometry import DesignType, GeneratedBy
from optim.ga import run_genetic_algorithm, GAConfig
from optim.pso import run_pso, PSOConfig
from sim.fitness import compute_fitness
from sim.material_properties import get_substrate_properties

logger = logging.getLogger(__name__)


def run_optimization(
    project: AntennaProject,
    design_type: DesignType,
    algorithm: OptimizationAlgorithm,
    population_size: int,
    generations: int,
    constraints: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Run optimization and persist results to database.
    
    Returns:
        Dict with optimization result data
    """
    # Prepare project parameters for fitness function
    project_params = {
        "substrate": project.substrate,
        "substrate_thickness_mm": project.substrate_thickness_mm,
        "feed_type": project.feed_type,
        "polarization": project.polarization,
        "target_gain_dbi": project.target_gain_dbi,
        "target_impedance_ohm": project.target_impedance_ohm,
        "conductor_thickness_um": project.conductor_thickness_um,
    }
    
    # CRITICAL: Add max_size_mm to constraints to ensure optimizer respects it
    if constraints is None:
        constraints = {}
    if "max_size_mm" not in constraints:
        constraints["max_size_mm"] = project.max_size_mm
    
    # CRITICAL: Log project parameters to verify they're being used correctly
    logger.info(
        f"[OPTIMIZATION START] Project {project.id}: "
        f"target_f={project.target_frequency_ghz:.6f}GHz, "
        f"target_BW={project.bandwidth_mhz:.2f}MHz, "
        f"substrate={project.substrate}, "
        f"ε_r_from_material={get_substrate_properties(project.substrate)['permittivity']:.3f}, "
        f"h={project.substrate_thickness_mm:.3f}mm, "
        f"max_size={project.max_size_mm:.1f}mm"
    )
    
    # Create fitness function
    def fitness_func(params: Dict[str, Any]) -> float:
        # CRITICAL: Verify target frequency is actually used (not cached or default)
        result = compute_fitness(
            params,
            project.target_frequency_ghz,  # Explicitly use project target
            project.bandwidth_mhz,  # Explicitly use project bandwidth
            project_params=project_params
        )
        return result["fitness"]
    
    # Create optimization run record
    opt_run = OptimizationRun(
        project_id=project.id,
        algorithm=algorithm,
        population_size=population_size,
        generations=generations,
        status=OptimizationStatus.running
    )
    db.add(opt_run)
    db.commit()
    db.refresh(opt_run)
    
    try:
        # Run optimization
        if algorithm == OptimizationAlgorithm.ga:
            config = GAConfig(
                population_size=population_size,
                generations=generations
            )
            result = run_genetic_algorithm(
                fitness_func,
                design_type,
                project.target_frequency_ghz,
                project.bandwidth_mhz,
                constraints,
                config
            )
            generated_by = GeneratedBy.ga
            logger.info(f"[GA COMPLETE] Run {opt_run.id}: Best fitness={result['best_candidate']['fitness']:.4f}")
        elif algorithm == OptimizationAlgorithm.pso:
            config = PSOConfig(
                swarm_size=population_size,
                generations=generations
            )
            result = run_pso(
                fitness_func,
                design_type,
                project.target_frequency_ghz,
                project.bandwidth_mhz,
                constraints,
                config
            )
            generated_by = GeneratedBy.pso
            logger.info(f"[PSO COMPLETE] Run {opt_run.id}: Best fitness={result['best_candidate']['fitness']:.4f}")
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Compute detailed metrics for best candidate
        best_params = result["best_candidate"]["params"]
        fitness_result = compute_fitness(
            best_params,
            project.target_frequency_ghz,
            project.bandwidth_mhz,
            project_params=project_params
        )
        
        # Update optimization run
        opt_run.status = OptimizationStatus.completed
        opt_run.best_fitness = result["best_candidate"]["fitness"]
        opt_run.log = {
            "history": result["history"],
            "population_size": population_size,
            "generations": generations
        }
        
        # Create design candidates
        # Helper function to check if two parameter sets are effectively duplicates
        # Uses tolerance for floating point comparison
        def are_params_duplicate(params1: Dict[str, Any], params2: Dict[str, Any], tolerance: float = 1e-6) -> bool:
            """Check if two parameter sets are duplicates within tolerance."""
            if set(params1.keys()) != set(params2.keys()):
                return False
            for key in params1.keys():
                val1 = params1[key]
                val2 = params2[key]
                # Handle different types
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    if abs(val1 - val2) > tolerance:
                        return False
                elif val1 != val2:
                    return False
            return True
        
        # Mark best candidate
        best_candidate = DesignCandidate(
            optimization_run_id=opt_run.id,
            geometry_params={**best_params, "shape_family": constraints.get("shape_family", "rectangular_patch")},
            fitness=result["best_candidate"]["fitness"],
            metrics=fitness_result["metrics"],
            is_best=True
        )
        db.add(best_candidate)
        
        # Track saved parameter sets to avoid duplicates
        saved_params_list = [best_params]
        candidates_saved = 1  # Best candidate already saved
        
        # Save all unique candidates from top 10 of final population
        for candidate in result["population"][:10]:  # Top 10
            # Check if this candidate is a duplicate of any already saved
            is_duplicate = False
            for saved_params in saved_params_list:
                if are_params_duplicate(candidate["params"], saved_params):
                    is_duplicate = True
                    break
            
            if is_duplicate:
                continue  # Skip duplicates
            
            # Compute detailed metrics for this candidate
            fitness_res = compute_fitness(
                candidate["params"],
                project.target_frequency_ghz,
                project.bandwidth_mhz,
                project_params=project_params
            )
            
            # Add shape_family to geometry_params if present in constraints
            candidate_params = {**candidate["params"], "shape_family": constraints.get("shape_family", "rectangular_patch")}
            
            candidate_db = DesignCandidate(
                optimization_run_id=opt_run.id,
                geometry_params=candidate_params,
                fitness=candidate["fitness"],
                metrics=fitness_res["metrics"],
                is_best=False
            )
            db.add(candidate_db)
            saved_params_list.append(candidate["params"])
            candidates_saved += 1
        
        logger.info(f"Saved {candidates_saved} unique candidates (1 best + {candidates_saved - 1} others) for run {opt_run.id}")
        
        # Create geometry param set for best design
        from models.geometry import GeometryParamSet
        geom_set = GeometryParamSet(
            project_id=project.id,
            design_type=design_type,
            parameters=best_params,
            generated_by=generated_by
        )
        db.add(geom_set)
        
        db.commit()
        
        return {
            "run_id": opt_run.id,
            "best_candidate": {
                "params": best_params,
                "fitness": result["best_candidate"]["fitness"],
                **fitness_result["metrics"]
            },
            "history": result["history"],
            "metrics": fitness_result["metrics"]
        }
        
    except Exception as e:
        # Mark run as failed with detailed error information
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        logger.error(f"Optimization failed for run {opt_run.id}: {error_msg}")
        logger.error(f"Traceback: {error_trace}")
        
        opt_run.status = OptimizationStatus.failed
        opt_run.log = {
            "error": error_msg,
            "error_type": type(e).__name__,
            "traceback": error_trace
        }
        db.commit()
        # Don't re-raise - let the background task handle it gracefully
        # raise

