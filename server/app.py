from flask import Flask, jsonify,request
import os
from dotenv import load_dotenv


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
# 3) Flask app and test endpoints
# -------------------------------------------------
app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(debug=True)
