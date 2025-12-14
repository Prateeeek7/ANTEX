"""
Test optimization run to identify failures.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models.user
import models.project
import models.optimization
import models.geometry

from db.base import SessionLocal
from models.project import AntennaProject
from models.optimization import OptimizationRun, OptimizationStatus, OptimizationAlgorithm
from models.geometry import DesignType
from optim.runner import run_optimization
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_optimization_run():
    """Test a simple optimization run to identify errors."""
    db = SessionLocal()
    try:
        # Get or create a test project
        project = db.query(AntennaProject).filter(
            AntennaProject.target_frequency_ghz == 2.4
        ).first()
        
        if not project:
            logger.error("No test project found. Please create a project first.")
            return
        
        logger.info(f"Testing optimization for project: {project.name}")
        logger.info(f"  Target frequency: {project.target_frequency_ghz} GHz")
        logger.info(f"  Substrate: {project.substrate}")
        logger.info(f"  Substrate thickness: {project.substrate_thickness_mm} mm")
        
        # Test with minimal parameters (fast test)
        try:
            result = run_optimization(
                project=project,
                design_type=DesignType.patch,
                algorithm=OptimizationAlgorithm.ga,
                population_size=5,  # Small for quick test
                generations=3,  # Small for quick test
                constraints={"max_size_mm": project.max_size_mm},
                db=db
            )
            
            logger.info("✓ Optimization completed successfully!")
            logger.info(f"  Best fitness: {result.get('best_candidate', {}).get('fitness', 'N/A')}")
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"✗ Optimization failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Traceback:\\n{traceback.format_exc()}")
            return False
            
    finally:
        db.close()

if __name__ == "__main__":
    success = test_optimization_run()
    sys.exit(0 if success else 1)


