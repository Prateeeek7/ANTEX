# AI Antenna Designer

A full-stack web application for optimizing antenna designs using evolutionary algorithms (Genetic Algorithm and Particle Swarm Optimization).

## Features

### Core Features
- **User Authentication**: JWT-based authentication system (currently disabled for development)
- **Project Management**: Create and manage antenna design projects with specifications
- **Optimization Algorithms**: 
  - Genetic Algorithm (GA)
  - Particle Swarm Optimization (PSO)
- **Design Types**: Support for patch, slot, and fractal antennas
- **Results Tracking**: Store and analyze optimization runs and design candidates

### Simulation Capabilities
- **Analytical Models**: Fast approximate EM models for quick fitness evaluation (~1ms)
- **Meep FDTD Integration** (⭐ NEW): Real 3D FDTD electromagnetic simulations with CST/HFSS-grade accuracy
  - Full 3D FDTD simulation using MIT's Meep
  - Real S11 curve extraction
  - Gain and radiation pattern calculation
  - STL/geometry export for fabrication
  - Hybrid mode: Fast optimization with analytical, accurate validation with Meep

### Visualization & Analysis
- **2D Geometry Visualization**: Real-time antenna geometry rendering
- **Convergence Plots**: Optimization history and fitness evolution
- **Interactive Dashboards**: Project overview, runs, candidates, and simulation data
- **S11 Curves**: Return loss vs frequency from real simulations

### Data Management
- **Project Tabs**: Overview, Runs, Candidates, Simulation data
- **File Upload**: Import HFSS/CST simulation results
- **Export Options**: STL files for 3D printing/fabrication
- **Best Design Tracking**: Automatically track and display best candidates

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL/SQLite** - Database (SQLite for dev, PostgreSQL for production)
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **NumPy, SciPy** - Numerical computations
- **DEAP** - Evolutionary algorithms
- **Meep** - MIT's open-source FDTD EM solver (optional, for real simulations)
- **bcrypt** - Password hashing
- **python-jose** - JWT token handling

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **Recharts** - Data visualization
- **Zustand** - State management

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd "Antenna Designer"
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start all services:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

5. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```bash
createdb antenna_designer
```

5. Create `.env` file:
```bash
cp ../.env.example .env
# Edit .env with your database URL
```

6. Run migrations:
```bash
alembic upgrade head
```

7. Start the server:
```bash
uvicorn main:app --reload
```

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

## Usage

1. **Register/Login**: Create an account or log in
2. **Create Project**: Define your antenna specifications (target frequency, bandwidth, max size, substrate)
3. **Start Optimization**: Choose design type, algorithm, and parameters
4. **View Results**: Analyze optimization history and best design candidates
5. **Export/Validate**: Use results as starting point for validation in professional EM tools

## Project Structure

```
.
├── backend/
│   ├── api/              # API routers
│   ├── core/             # Core utilities (config, security, logging)
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy models
│   ├── optim/            # Optimization algorithms (GA, PSO)
│   ├── schemas/          # Pydantic schemas
│   ├── sim/              # Simulation models and fitness computation
│   ├── alembic/          # Database migrations
│   └── main.py           # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── api/          # API client functions
│   │   ├── components/   # React components
│   │   ├── layouts/      # Layout components
│   │   ├── pages/        # Page components
│   │   ├── store/        # State management
│   │   └── types/        # TypeScript types
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Documentation

When the backend is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

### Code Quality

Backend:
- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions

Frontend:
- Follow ESLint rules
- Use TypeScript strictly
- Component-based architecture

## Meep FDTD Integration (CST/HFSS-Grade Simulations)

The system now supports **real 3D FDTD electromagnetic simulations** using Meep (MIT Electromagnetic Equation Propagation)!

### Quick Setup

1. **Install Meep:**
   ```bash
   # macOS - Recommended: Use conda (easiest method)
   # First install Miniconda or Anaconda if you don't have it:
   # Download from: https://docs.conda.io/en/latest/miniconda.html
   conda install -c conda-forge meep
   
   # Alternative: pip (requires compilation and system dependencies)
   # On macOS, you may need to install dependencies first:
   brew install hdf5 fftw gsl libmpfr gmp
   pip install meep
   
   # Note: Meep is NOT available via `brew install meep`
   ```

2. **Enable in `.env`:**
   ```env
   USE_MEEP=true
   MEEP_RESOLUTION=20
   ```

3. **Check status:**
   ```bash
   curl http://localhost:8000/api/v1/meep/status
   ```

### Features
- ✅ Real FDTD simulations (not approximations)
- ✅ Accurate S11 curves and return loss
- ✅ Gain and radiation patterns
- ✅ STL export for 3D printing
- ✅ Hybrid optimization strategy (fast + accurate)
- ✅ EM field visualization (E-field, H-field, current distribution)

## Limitations

- **Analytical Models**: Fast but approximate (±10-20% error)
- **Meep FDTD**: Accurate but slower (~30s-5min per simulation)
- **Physical Constraints**: Manufacturing tolerances not accounted for
- **Validation**: For production designs, still recommend validation with commercial tools

## Future Enhancements

- ✅ ~~Integration with Meep for full-wave simulation~~ (DONE!)
- Surrogate neural network models for faster fitness evaluation
- 3D geometry visualization
- Export to CAD formats (STEP, IGES)
- Background job processing for long optimizations
- Advanced optimization algorithms (NSGA-II, MOPSO)
- Multi-objective optimization
- Automated design rule checking

## License

[Your License Here]

## Contributing

[Contributing Guidelines]

## Support

[Support Information]


