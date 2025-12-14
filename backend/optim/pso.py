"""
Particle Swarm Optimization implementation for antenna optimization.
"""
import random
import logging
from typing import List, Dict, Any, Callable
from models.geometry import DesignType
from optim.space import sample_random_params, normalize_params, denormalize_params

logger = logging.getLogger(__name__)


class PSOConfig:
    def __init__(
        self,
        swarm_size: int = 30,
        generations: int = 40,
        w: float = 0.7,  # Inertia weight
        c1: float = 1.5,  # Cognitive coefficient
        c2: float = 1.5,  # Social coefficient
        v_max: float = 0.2  # Maximum velocity
    ):
        self.swarm_size = swarm_size
        self.generations = generations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.v_max = v_max


class Particle:
    def __init__(self, position_norm: List[float], fitness: float):
        self.position_norm = position_norm
        self.velocity = [0.0] * len(position_norm)
        self.fitness = fitness
        self.best_position_norm = position_norm.copy()
        self.best_fitness = fitness


def run_pso(
    fitness_func: Callable[[Dict[str, float]], float],
    design_type: DesignType,
    target_freq_ghz: float,
    target_bw_mhz: float,
    constraints: Dict[str, Any] = None,
    config: PSOConfig = None
) -> Dict[str, Any]:
    """
    Run Particle Swarm Optimization.
    
    Args:
        fitness_func: Function that takes params dict and returns fitness score
        design_type: Type of antenna design
        target_freq_ghz: Target frequency
        target_bw_mhz: Target bandwidth
        constraints: Parameter constraints
        config: PSO configuration
        
    Returns:
        Dict with best_candidate, history, and population
    """
    if config is None:
        config = PSOConfig()
    
    # Initialize swarm
    # CRITICAL: Use auto-design for first particle to get good starting point
    from optim.auto_design import estimate_initial_patch_dimensions
    swarm = []
    global_best_fitness = float('-inf')
    global_best_position_norm = None
    
    # First particle: use auto-design based on target frequency
    if design_type == DesignType.patch:
        try:
            auto_params = estimate_initial_patch_dimensions(
                target_freq_ghz,
                constraints.get("substrate", "FR4") if constraints else "FR4",
                constraints.get("substrate_thickness_mm", 1.6) if constraints else 1.6,
                constraints.get("max_size_mm") if constraints else None
            )
            # Ensure auto_params respect all constraints
            if constraints:
                max_size = constraints.get("max_size_mm")
                if max_size:
                    auto_params["length_mm"] = min(auto_params["length_mm"], max_size)
                    auto_params["width_mm"] = min(auto_params["width_mm"], max_size)
            
            fitness = fitness_func(auto_params)
            position_norm = normalize_params(auto_params, design_type, constraints)
            particle = Particle(position_norm, fitness)
            swarm.append(particle)
            
            if fitness > global_best_fitness:
                global_best_fitness = fitness
                global_best_position_norm = position_norm.copy()
            
            logger.info(f"Auto-designed initial patch: L={auto_params['length_mm']:.2f}mm, W={auto_params['width_mm']:.2f}mm")
        except Exception as e:
            logger.warning(f"Auto-design failed, using random: {e}")
            # Fall through to random sampling
    
    # Remaining particles: random sampling
    for _ in range(len(swarm), config.swarm_size):
        params = sample_random_params(design_type, constraints)
        # CRITICAL: Validate max_size constraint
        if constraints and "max_size_mm" in constraints:
            max_size = constraints["max_size_mm"]
            if "length_mm" in params:
                params["length_mm"] = min(params["length_mm"], max_size)
            if "width_mm" in params:
                params["width_mm"] = min(params["width_mm"], max_size)
        
        fitness = fitness_func(params)
        position_norm = normalize_params(params, design_type, constraints)
        
        particle = Particle(position_norm, fitness)
        swarm.append(particle)
        
        if fitness > global_best_fitness:
            global_best_fitness = fitness
            global_best_position_norm = position_norm.copy()
    
    history = []
    
    # Main PSO loop
    for generation in range(config.generations):
        for particle in swarm:
            # Update velocity
            for i in range(len(particle.position_norm)):
                r1 = random.random()
                r2 = random.random()
                
                cognitive = config.c1 * r1 * (particle.best_position_norm[i] - particle.position_norm[i])
                social = config.c2 * r2 * (global_best_position_norm[i] - particle.position_norm[i])
                
                particle.velocity[i] = (
                    config.w * particle.velocity[i] + cognitive + social
                )
                # Limit velocity
                particle.velocity[i] = max(-config.v_max, min(config.v_max, particle.velocity[i]))
            
            # Update position
            for i in range(len(particle.position_norm)):
                particle.position_norm[i] += particle.velocity[i]
                # Clamp to [0, 1]
                particle.position_norm[i] = max(0.0, min(1.0, particle.position_norm[i]))
            
            # Evaluate new position
            params = denormalize_params(particle.position_norm, design_type, constraints)
            
            # CRITICAL: Validate max_size constraint and geometry bounds
            if constraints and "max_size_mm" in constraints:
                max_size = constraints["max_size_mm"]
                if "length_mm" in params:
                    params["length_mm"] = min(params["length_mm"], max_size)
                if "width_mm" in params:
                    params["width_mm"] = min(params["width_mm"], max_size)
            
            # Validate feed_offset doesn't exceed length/2
            if "feed_offset_mm" in params and "length_mm" in params:
                max_offset = abs(params["length_mm"] / 2)
                params["feed_offset_mm"] = max(-max_offset, min(max_offset, params["feed_offset_mm"]))
            
            # Log parameter change and frequency recalculation (sample logging to avoid spam)
            if generation % 5 == 0 and particle == swarm[0]:  # Log every 5th generation for first particle
                logger.debug(
                    f"PSO Gen {generation+1}, Particle 1: "
                    f"L={params.get('length_mm', 'N/A'):.2f}mm, W={params.get('width_mm', 'N/A'):.2f}mm, "
                    f"offset={params.get('feed_offset_mm', 0):.2f}mm"
                )
            
            particle.fitness = fitness_func(params)
            
            # Update personal best
            if particle.fitness > particle.best_fitness:
                particle.best_fitness = particle.fitness
                particle.best_position_norm = particle.position_norm.copy()
            
            # Update global best
            if particle.fitness > global_best_fitness:
                global_best_fitness = particle.fitness
                global_best_position_norm = particle.position_norm.copy()
        
        # Record history with geometry information
        avg_fitness = sum(p.fitness for p in swarm) / len(swarm)
        best_params = denormalize_params(global_best_position_norm, design_type, constraints)
        history.append({
            "generation": generation + 1,
            "best_fitness": global_best_fitness,
            "avg_fitness": avg_fitness,
            "best_geometry": {
                "length_mm": best_params.get("length_mm", 0),
                "width_mm": best_params.get("width_mm", 0),
                "feed_offset_mm": best_params.get("feed_offset_mm", 0),
            }
        })
        
        # Log geometry history every 5 generations
        if (generation + 1) % 5 == 0:
            logger.info(
                f"PSO Gen {generation+1}: best_fitness={global_best_fitness:.2f}, "
                f"best_L={best_params.get('length_mm', 0):.2f}mm, "
                f"best_W={best_params.get('width_mm', 0):.2f}mm, "
                f"avg_fitness={avg_fitness:.2f}"
            )
    
    # Prepare result
    best_params = denormalize_params(global_best_position_norm, design_type, constraints)
    
    return {
        "best_candidate": {
            "params": best_params,
            "fitness": global_best_fitness
        },
        "history": history,
        "population": [
            {
                "params": denormalize_params(p.position_norm, design_type, constraints),
                "fitness": p.fitness
            }
            for p in sorted(swarm, key=lambda x: x.fitness, reverse=True)[:10]
        ]
    }




