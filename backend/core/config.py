from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DB_URL: str = "sqlite:///./antenna_designer.db"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # App
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "ANTEX"
    VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Meep FDTD Integration
    USE_MEEP: bool = True  # Set to True to enable real FDTD simulations (requires Meep installation)
    MEEP_RESOLUTION: int = 20  # Simulation resolution (pixels per unit length, higher = more accurate but slower)
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

