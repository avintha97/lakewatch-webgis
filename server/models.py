"""
SQLAlchemy models for LakeWatch WebGIS.
Stores water analysis data with PostGIS geometry support.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from geoalchemy2 import Geometry
from database import Base


class LakeAnalysis(Base):
    """
    Model for storing lake water area analysis results.
    
    Attributes:
        id: Unique identifier
        geometry: Polygon geometry of the analyzed area (PostGIS)
        date: Target analysis date (YYYY-MM-DD)
        threshold: VV/VH threshold used (in dB)
        water_area_km2: Calculated water area in square kilometers
        pixel_count: Number of water pixels detected
        submission_date: When the analysis was submitted
        satellite: Satellite source (e.g., "Sentinel-1")
        created_at: Database record creation timestamp
    """
    
    __tablename__ = "lake_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False, index=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    threshold = Column(Integer, nullable=False)  # dB value
    water_area_km2 = Column(Float, nullable=False)
    pixel_count = Column(Integer, nullable=False)
    submission_date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    satellite = Column(String(50), nullable=False, default="Sentinel-1")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "date": self.date,
            "threshold": self.threshold,
            "water_area_km2": self.water_area_km2,
            "pixel_count": self.pixel_count,
            "submission_date": self.submission_date,
            "satellite": self.satellite,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
