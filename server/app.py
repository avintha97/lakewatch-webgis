from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime


# Workaround for Windows: blessings module uses fcntl (Unix-only)
# Monkey-patch fcntl before importing ee
import sys
if sys.platform == 'win32':
    import types
    fcntl_mock = types.ModuleType('fcntl')
    fcntl_mock.ioctl = lambda *args, **kwargs: None  # dummy ioctl function
    sys.modules['fcntl'] = fcntl_mock

import ee

# from ee_area import count_landsat_images_by_year
from ee_area import calculate_water_area_sentinel1
from database import init_database, get_session
from models import LakeAnalysis


# -------------------------------------------------
# 1) Load .env from project root
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
print(ENV_PATH)
load_dotenv(ENV_PATH)

EE_PROJECT = os.getenv("EE_PROJECT")
HIVOLUME_URL = os.getenv("HIVOLUME_URL")

print("EE_PROJECT from env:", EE_PROJECT)
print("HIVOLUME_URL from env:", HIVOLUME_URL)

# -------------------------------------------------
# 2) Initialize Earth Engine
#    (we already ran ee.Authenticate() once manually)
# -------------------------------------------------
try:
    if EE_PROJECT:
        # Equivalent to: ee.Initialize(project='ee-aviresearch')
        ee.Initialize(project=EE_PROJECT)
    else:
        # Fallback: use default credentials without explicit project
        ee.Initialize()
    print("Earth Engine initialized OK")
except Exception as e:
    print("Earth Engine init error:", e)

# -------------------------------------------------
# 3) Initialize Flask app and database
# -------------------------------------------------
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
try:
    init_database()
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization error: {e}")
    print("Database features may not be available")


@app.route("/api/v1/env-check", methods=["GET"])
def env_check():
    """
    Check that environment variables are loaded correctly.
    """
    return jsonify({
        "EE_PROJECT": EE_PROJECT,
        "HIVOLUME_URL": HIVOLUME_URL
    }), 200


@app.route("/api/v1/health", methods=["GET"])
def health_check():
    """
    Simple health check for Flask.
    """
    return jsonify({"status": "ok", "message": "Flask server is running"}), 200

@app.route("/api/v1/lakes/area", methods=["POST"])
def get_lakes_area():
    """
    POST /api/v1/lakes/area
    
    Calculate water area using Sentinel-1 SAR for a given geometry and date.
    
    Request body JSON:
    {
        "bbox": [[lon, lat], [lon, lat], [lon, lat], [lon, lat], [lon, lat]],
        "date": "2025-01-27",
        "vv_vh_threshold": -17
    }
    
    Response:
    {
        "target_date": "2025-01-27",
        "start_date": "2025-01-22",
        "end_date": "2025-02-01",
        "water_area_km2": 45.1234,
        "pixel_count": 451234,
        "vv_vh_threshold_db": -17,
        "satellite": "Sentinel-1"
    }
    """
    try:
        data = request.get_json()
        bbox = data.get("bbox")
        date = data.get("date")
        vv_vh_threshold = data.get("vv_vh_threshold", -17)
        
        if not bbox or not date:
            return jsonify({
                "status": "error",
                "message": "Missing 'bbox' or 'date' in request body"
            }), 400
        
        result = calculate_water_area_sentinel1(bbox, date, vv_vh_threshold)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/v1/analysis/save", methods=["POST"])
def save_analysis():
    """
    POST /api/v1/analysis/save
    
    Save water area analysis to PostgreSQL database with PostGIS geometry.
    
    Request body JSON:
    {
        "geometry": {"type": "Polygon", "coordinates": [[[lon, lat], ...]]},
        "date": "2025-01-27",
        "threshold": -17,
        "water_area_km2": 45.1234,
        "pixel_count": 451234,
        "submission_date": "2025-01-27",
        "satellite": "Sentinel-1",
        "notes": "Optional notes about this analysis"
    }
    
    Response:
    {
        "id": 1,
        "status": "saved",
        "message": "Analysis saved successfully"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["geometry", "date", "threshold", "water_area_km2", "pixel_count", "submission_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Extract data
        geometry = data.get("geometry")
        date = data.get("date")
        threshold = data.get("threshold")
        water_area_km2 = data.get("water_area_km2")
        pixel_count = data.get("pixel_count")
        submission_date = data.get("submission_date")
        satellite = data.get("satellite", "Sentinel-1")
        notes = data.get("notes")
        
        # Create session and new record
        session = get_session()
        
        try:
            # Create geometry from GeoJSON (converts to WKT for PostGIS)
            from shapely.geometry import shape as shapely_shape
            from geoalchemy2.elements import WKTElement
            
            shapely_geom = shapely_shape(geometry)
            wkt_geom = WKTElement(shapely_geom.wkt, srid=4326)
            
            # Create new analysis record
            new_analysis = LakeAnalysis(
                geometry=wkt_geom,
                date=date,
                threshold=threshold,
                water_area_km2=water_area_km2,
                pixel_count=pixel_count,
                submission_date=submission_date,
                satellite=satellite,
                notes=notes
            )
            
            session.add(new_analysis)
            session.commit()
            record_id = new_analysis.id
            session.close()
            
            return jsonify({
                "id": record_id,
                "status": "saved",
                "message": "Analysis saved successfully"
            }), 201
        
        except Exception as db_err:
            session.rollback()
            session.close()
            # Print full error to console for debugging
            import traceback
            print(f"Database Save Error: {str(db_err)}")
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": f"Database error: {str(db_err)}"
            }), 500
    
    except Exception as e:
        # Print full error to console for debugging
        import traceback
        print(f"Save Analysis Error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/v1/analysis/list", methods=["GET"])
def list_analyses():
    """
    GET /api/v1/analysis/list
    
    Retrieve all saved analyses from the database.
    
    Query parameters:
    - limit: Maximum number of results (default: 100)
    - offset: Number of results to skip (default: 0)
    
    Response:
    {
        "count": 5,
        "analyses": [
            {
                "id": 1,
                "date": "2025-01-27",
                "water_area_km2": 45.1234,
                "pixel_count": 451234,
                "submission_date": "2025-01-27",
                "satellite": "Sentinel-1",
                "notes": "...",
                "created_at": "2025-01-27T10:30:00"
            },
            ...
        ]
    }
    """
    try:
        limit = request.args.get("limit", default=100, type=int)
        offset = request.args.get("offset", default=0, type=int)
        
        # Validate parameters
        limit = min(limit, 500)  # Max 500 results
        offset = max(offset, 0)
        
        session = get_session()
        
        try:
            # Query analyses ordered by most recent first
            analyses = session.query(LakeAnalysis)\
                .order_by(LakeAnalysis.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            total_count = session.query(LakeAnalysis).count()
            
            session.close()
            
            return jsonify({
                "count": total_count,
                "returned": len(analyses),
                "limit": limit,
                "offset": offset,
                "analyses": [a.to_dict() for a in analyses]
            }), 200
        
        except Exception as db_err:
            session.close()
            return jsonify({
                "status": "error",
                "message": f"Database error: {str(db_err)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/v1/analysis/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    """
    GET /api/v1/analysis/{id}
    
    Retrieve a specific analysis by ID.
    """
    try:
        session = get_session()
        
        try:
            analysis = session.query(LakeAnalysis).filter(LakeAnalysis.id == analysis_id).first()
            session.close()
            
            if not analysis:
                return jsonify({
                    "status": "error",
                    "message": f"Analysis with ID {analysis_id} not found"
                }), 404
            
            return jsonify({
                "status": "ok",
                "analysis": analysis.to_dict()
            }), 200
        
        except Exception as db_err:
            session.close()
            return jsonify({
                "status": "error",
                "message": f"Database error: {str(db_err)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
