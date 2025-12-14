export default function DocsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Documentation</h1>

      <div className="space-y-8">
        <section className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">What is ANTEX?</h2>
          <p className="text-gray-700 mb-4">
            ANTEX is a web-based tool that uses evolutionary algorithms to optimize antenna designs.
            It helps engineers quickly find antenna geometries that meet specific frequency and bandwidth requirements.
          </p>
        </section>

        <section className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Optimization Algorithms</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-medium text-gray-800 mb-2">Genetic Algorithm (GA)</h3>
              <p className="text-gray-700">
                Genetic Algorithm mimics natural selection. It starts with a population of random antenna designs,
                evaluates their fitness, and evolves better designs through selection, crossover, and mutation operations.
                Over multiple generations, the algorithm converges toward optimal solutions.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-medium text-gray-800 mb-2">Particle Swarm Optimization (PSO)</h3>
              <p className="text-gray-700">
                PSO uses a swarm of particles (potential designs) that move through the parameter space.
                Each particle adjusts its position based on its own best position and the swarm's best position.
                This collaborative search often converges quickly to good solutions.
              </p>
            </div>
          </div>
        </section>

        <section className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Fitness Function</h2>
          <p className="text-gray-700 mb-4">
            The fitness function evaluates how well an antenna design meets your specifications. It considers:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li><strong>Frequency Error:</strong> How close the resonant frequency is to your target</li>
            <li><strong>Bandwidth Error:</strong> How close the bandwidth matches your requirement</li>
            <li><strong>Gain:</strong> Higher gain is preferred (within physical limits)</li>
          </ul>
          <p className="text-gray-700 mt-4">
            The optimization algorithms try to maximize fitness by minimizing errors and maximizing gain.
          </p>
        </section>

        <section className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Limitations</h2>
          <div className="space-y-3 text-gray-700">
            <p>
              <strong>Approximate Models:</strong> The current version uses simplified analytical models for EM simulation.
              These provide good estimates but are not as accurate as full-wave simulation tools like HFSS or CST.
            </p>
            <p>
              <strong>Design Validation:</strong> Optimized designs should be validated with professional EM simulation
              software before fabrication. The results here are a starting point for further refinement.
            </p>
            <p>
              <strong>Physical Constraints:</strong> The optimizer doesn't consider manufacturing tolerances, connector
              losses, or other practical constraints. These should be factored in during final design validation.
            </p>
          </div>
        </section>

        <section className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Getting Started</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>Create a new project with your target specifications</li>
            <li>Choose a design type (patch, slot, or fractal antenna)</li>
            <li>Select an optimization algorithm and set population size and generations</li>
            <li>Start the optimization and wait for results</li>
            <li>Review the best candidate's geometry and metrics</li>
            <li>Validate promising designs in professional EM simulation tools</li>
          </ol>
        </section>
      </div>
    </div>
  )
}


