from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logging import setup_logging
from db.base import Base, engine
import json
import os

# Import models to register them with SQLAlchemy
import models.user
import models.project
import models.geometry
import models.optimization

# Import routers
import api.routers.auth as auth_router
import api.routers.projects as projects_router
import api.routers.optimize as optimize_router
import api.routers.sim as sim_router
import api.routers.meep as meep_router
import api.routers.analysis as analysis_router
import api.routers.performance as performance_router
import api.routers.geometry as geometry_router
import api.routers.test_backend as test_backend_router

# Setup logging
setup_logging(debug=settings.DEBUG)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# #region agent log - Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    log_path = "/Users/pratikkumar/Desktop/Antenna Designer/.cursor/debug.log"
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_data = {
            "location": "main.py:middleware",
            "message": "HTTP_REQUEST",
            "data": {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "headers": dict(request.headers)
            },
            "timestamp": int(__import__("time").time() * 1000),
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "A"
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    
    response = await call_next(request)
    
    try:
        log_data = {
            "location": "main.py:middleware",
            "message": "HTTP_RESPONSE",
            "data": {
                "status_code": response.status_code,
                "path": request.url.path
            },
            "timestamp": int(__import__("time").time() * 1000),
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "A"
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    
    return response
# #endregion

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(projects_router.router, prefix=f"{settings.API_V1_PREFIX}/projects", tags=["projects"])
app.include_router(optimize_router.router, prefix=f"{settings.API_V1_PREFIX}/optimize", tags=["optimize"])
app.include_router(sim_router.router, prefix=f"{settings.API_V1_PREFIX}/sim", tags=["sim"])
app.include_router(meep_router.router, prefix=f"{settings.API_V1_PREFIX}/meep", tags=["meep"])
app.include_router(analysis_router.router, prefix=f"{settings.API_V1_PREFIX}/analysis", tags=["analysis"])
app.include_router(performance_router.router, prefix=f"{settings.API_V1_PREFIX}/performance", tags=["performance"])
app.include_router(geometry_router.router, prefix=f"{settings.API_V1_PREFIX}/geometry", tags=["geometry"])
app.include_router(test_backend_router.router, prefix=f"{settings.API_V1_PREFIX}/test", tags=["test"])


@app.get("/")
def root():
    return {"message": "ANTEX API", "version": settings.VERSION}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

