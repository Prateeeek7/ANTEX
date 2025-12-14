import pytest
from sim.fitness import compute_fitness


def test_fitness_exact_match():
    """Test fitness when parameters exactly match target."""
    params = {
        "length_mm": 30.0,
        "width_mm": 25.0,
        "substrate_height_mm": 1.6,
        "eps_r": 4.4,
        "feed_offset_mm": 0.0,
    }
    result = compute_fitness(params, target_frequency_ghz=2.4, target_bandwidth_mhz=100.0)
    
    assert "fitness" in result
    assert "metrics" in result
    assert "freq_error_ghz" in result["metrics"]
    assert "bandwidth_error_mhz" in result["metrics"]
    assert result["fitness"] > 0  # Should be positive


def test_fitness_frequency_error():
    """Test that frequency error affects fitness."""
    params1 = {
        "length_mm": 30.0,
        "width_mm": 25.0,
        "substrate_height_mm": 1.6,
        "eps_r": 4.4,
        "feed_offset_mm": 0.0,
    }
    params2 = {
        "length_mm": 40.0,  # Different size = different frequency
        "width_mm": 25.0,
        "substrate_height_mm": 1.6,
        "eps_r": 4.4,
        "feed_offset_mm": 0.0,
    }
    
    result1 = compute_fitness(params1, target_frequency_ghz=2.4, target_bandwidth_mhz=100.0)
    result2 = compute_fitness(params2, target_frequency_ghz=2.4, target_bandwidth_mhz=100.0)
    
    # Fitnesses should be different
    assert result1["fitness"] != result2["fitness"]
    # Errors should be different
    assert result1["metrics"]["freq_error_ghz"] != result2["metrics"]["freq_error_ghz"]





