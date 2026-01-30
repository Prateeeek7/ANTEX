from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from core.config import settings

_db_url = settings.effective_db_url

# Create engine
connect_args = {}
if "sqlite" in _db_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    _db_url,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

