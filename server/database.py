"""
Database initialization and connection helpers for LakeWatch WebGIS.
Uses SQLAlchemy with PostgreSQL and PostGIS for geometry storage.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

# Create base class for models
Base = declarative_base()

# Initialize engine (will be set after app context)
engine = None
SessionLocal = None


def init_database():
    """Initialize database connection and create tables."""
    global engine, SessionLocal
    
    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL not set in .env file. "
            "Example: postgresql+psycopg2://user:password@localhost:5432/lakewatch"
        )
    
    # Create engine with NullPool to avoid connection pooling issues in some environments
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        poolclass=NullPool
    )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized and tables created.")


def get_session():
    """Get a new database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return SessionLocal()


def close_database():
    """Close database connection."""
    global engine
    if engine:
        engine.dispose()
        print("Database connection closed.")
