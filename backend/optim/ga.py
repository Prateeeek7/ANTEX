"""
Genetic Algorithm implementation for antenna optimization.
"""
import random
import logging
from typing import List, Dict, Any, Callable
from models.geometry import DesignType
from optim.space import sample_random_params, normalize_params, denormalize_params

logger = logging.getLogger(__name__)


class GAConfig:
    def __init__(
        self,
        population_size: int = 30,
        generations: int = 40,
        mutation_rate: float = 0.2,
        crossover_rate: float = 0.8,
        tournament_size: int = 3,
        elite_size: int = 2
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.elite_size = elite_size


def run_genetic_algorithm(
    fitness_func: Callable[[Dict[str, float]], float],
    design_type: DesignType,
    target_freq_ghz: float,
    target_bw_mhz: float,
    constraints: Dict[str, Any] = None,
    config: GAConfig = None
) -> Dict[str, Any]:
    """
    Run genetic algorithm optimization.
    
    Args:
        fitness_func: Function that takes params dict and returns fitness score
        design_type: Type of antenna design
        target_freq_ghz: Target frequency
        target_bw_mhz: Target bandwidth
        constraints: Parameter constraints
        config: GA configuration
        
    Returns:
        Dict with best_candidate, history, and population
    """
    if config is None:
        config = GAConfig()
    
    # Initialize population
    # CRITICAL: Use auto-design for first individual to get good starting point
    from optim.auto_design import estimate_initial_patch_dimensions
    population = []
    
    # First individual: use auto-design based on target frequency
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
            population.append({
                "params": auto_params,
                "fitness": fitness,
                "normalized": normalize_params(auto_params, design_type, constraints)
            })
            logger.info(f"Auto-designed initial patch: L={auto_params['length_mm']:.2f}mm, W={auto_params['width_mm']:.2f}mm")
        except Exception as e:
            logger.warning(f"Auto-design failed, using random: {e}")
            # Fall through to random sampling
    
    # Remaining individuals: random sampling
    for _ in range(len(population), config.population_size):
        params = sample_random_params(design_type, constraints)
        # CRITICAL: Validate max_size constraint
        if constraints and "max_size_mm" in constraints:
            max_size = constraints["max_size_mm"]
            if "length_mm" in params:
                params["length_mm"] = min(params["length_mm"], max_size)
            if "width_mm" in params:
                params["width_mm"] = min(params["width_mm"], max_size)
        
        fitness = fitness_func(params)
        population.append({
            "params": params,
            "fitness": fitness,
            "normalized": normalize_params(params, design_type, constraints)
        })
    
    # Sort by fitness (higher is better)
    population.sort(key=lambda x: x["fitness"], reverse=True)
    
    history = []
    best_fitness_ever = population[0]["fitness"]
    best_candidate_ever = population[0].copy()
    
    # Evolution loop
    for generation in range(config.generations):
        new_population = []
        
        # Elitism: keep best individuals
        for i in range(config.elite_size):
            new_population.append(population[i].copy())
        
        # Generate offspring
        while len(new_population) < config.population_size:
            # Selection
            parent1 = tournament_selection(population, config.tournament_size)
            parent2 = tournament_selection(population, config.tournament_size)
            
            # Crossover
            if random.random() < config.crossover_rate:
                child_norm = crossover(parent1["normalized"], parent2["normalized"])
            else:
                child_norm = parent1["normalized"].copy()
            
            # Mutation
            if random.random() < config.mutation_rate:
                child_norm = mutate(child_norm)
            
            # Denormalize and evaluate
            child_params = denormalize_params(child_norm, design_type, constraints)
            
            # CRITICAL: Validate max_size constraint and geometry bounds
            if constraints and "max_size_mm" in constraints:
                max_size = constraints["max_size_mm"]
                if "length_mm" in child_params:
                    child_params["length_mm"] = min(child_params["length_mm"], max_size)
                if "width_mm" in child_params:
                    child_params["width_mm"] = min(child_params["width_mm"], max_size)
            
            # Validate feed_offset doesn't exceed length/2
            if "feed_offset_mm" in child_params and "length_mm" in child_params:
                max_offset = abs(child_params["length_mm"] / 2)
                child_params["feed_offset_mm"] = max(-max_offset, min(max_offset, child_params["feed_offset_mm"]))
            
            # Log parameter change and frequency recalculation
            if generation % 5 == 0 or len(new_population) < 3:  # Log every 5th generation or first few
                logger.debug(
                    f"GA Gen {generation+1}, Individual {len(new_population)+1}: "
                    f"L={child_params.get('length_mm', 'N/A'):.2f}mm, W={child_params.get('width_mm', 'N/A'):.2f}mm, "
                    f"offset={child_params.get('feed_offset_mm', 0):.2f}mm"
                )
            
            child_fitness = fitness_func(child_params)
            
            new_population.append({
                "params": child_params,
                "fitness": child_fitness,
                "normalized": child_norm
            })
        
        # Update population
        population = new_population
        population.sort(key=lambda x: x["fitness"], reverse=True)
        
        # Track best
        if population[0]["fitness"] > best_fitness_ever:
            best_fitness_ever = population[0]["fitness"]
            best_candidate_ever = population[0].copy()
        
        # Record history with geometry information
        avg_fitness = sum(p["fitness"] for p in population) / len(population)
        best_params = population[0]["params"]
        history.append({
            "generation": generation + 1,
            "best_fitness": population[0]["fitness"],
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
                f"GA Gen {generation+1}: best_fitness={population[0]['fitness']:.2f}, "
                f"best_L={best_params.get('length_mm', 0):.2f}mm, "
                f"best_W={best_params.get('width_mm', 0):.2f}mm, "
                f"avg_fitness={avg_fitness:.2f}"
            )
    
    return {
        "best_candidate": {
            "params": best_candidate_ever["params"],
            "fitness": best_candidate_ever["fitness"]
        },
        "history": history,
        "population": [
            {"params": p["params"], "fitness": p["fitness"]}
            for p in population[:10]  # Return top 10
        ]
    }


def tournament_selection(population: List[Dict], tournament_size: int) -> Dict:
    """Tournament selection."""
    tournament = random.sample(population, min(tournament_size, len(population)))
    return max(tournament, key=lambda x: x["fitness"])


def crossover(parent1_norm: List[float], parent2_norm: List[float]) -> List[float]:
    """Uniform crossover."""
    child = []
    for i in range(len(parent1_norm)):
        if random.random() < 0.5:
            child.append(parent1_norm[i])
        else:
            child.append(parent2_norm[i])
    return child


def mutate(normalized: List[float], mutation_strength: float = 0.1) -> List[float]:
    """Gaussian mutation on normalized parameters."""
    mutated = []
    for val in normalized:
        if random.random() < 0.3:  # Only mutate some parameters
            new_val = val + random.gauss(0, mutation_strength)
            new_val = max(0.0, min(1.0, new_val))  # Clamp
            mutated.append(new_val)
        else:
            mutated.append(val)
    return mutated




