from flask import Flask, jsonify
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

from ee_area import count_landsat_images_by_year


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

@app.route("/api/v1/lakes/image-count/<int:year>", methods=["GET"])
def get_image_count_by_year(year):
    """
    Get image count for Senanayaka Samudraya for a given year.
    
    URL: GET /api/v1/lakes/image-count/2025
    """
    bbox_coords = [
        [81.39865413309057, 7.099820828875569],
        [81.55658259988745, 7.099820828875569],
        [81.55658259988745, 7.281713154976799],
        [81.39865413309057, 7.281713154976799],
        [81.39865413309057, 7.099820828875569],
    ]
    
    try:
        result = count_landsat_images_by_year(bbox_coords, year)
        
        return jsonify({
            "lake_name": "Senanayaka Samudraya",
            "year": result["year"],
            "image_count": result["image_count"],
            "start_date": result["start_date"],
            "end_date": result["end_date"]
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
