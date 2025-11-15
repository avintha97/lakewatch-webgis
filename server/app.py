from flask import Flask, jsonify
import os
from dotenv import load_dotenv
import ee

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

@app.route("/api/v1/lakes/senanayaka/landsat-2025-count", methods=["GET"])
def senanayaka_landsat_2025_count():
    """
    Test route:
    - Uses a fixed bounding box for Senanayaka Samudraya (Sri Lanka, Asia)
    - Counts how many Landsat images (L8 + L9) intersect this area in 2025
    - Returns JSON for the frontend
    """

    try:
        # 1) Define the bounding box geometry (WGS84 / EPSG:4326)
        #    Your coordinates:
        #    0: [81.39865413309057, 7.099820828875569]
        #    1: [81.55658259988745, 7.099820828875569]
        #    2: [81.55658259988745, 7.281713154976799]
        #    3: [81.39865413309057, 7.281713154976799]
        #    4: [81.39865413309057, 7.099820828875569]
        bbox_coords = [
            [81.39865413309057, 7.099820828875569],
            [81.55658259988745, 7.099820828875569],
            [81.55658259988745, 7.281713154976799],
            [81.39865413309057, 7.281713154976799],
            [81.39865413309057, 7.099820828875569],
        ]

        geometry = ee.Geometry.Polygon([bbox_coords])

        # 2) Set date range for year 2025
        start_date = "2025-01-01"
        end_date = "2025-12-31"

        # 3) Choose Landsat collections (L8 + L9, Collection 2 Level-2)
        landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
            .filterBounds(geometry) \
            .filterDate(start_date, end_date)

        landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
            .filterBounds(geometry) \
            .filterDate(start_date, end_date)

        # 4) Count images in each collection and sum
        count_l8 = landsat8.size()
        count_l9 = landsat9.size()
        total_count = count_l8.add(count_l9)

        # Bring the number from EE to Python
        total_count_int = int(total_count.getInfo())

        # 5) Build response for frontend
        response = {
            "lake_name": "Senanayaka Samudraya",
            "country": "Sri Lanka",
            "continent": "Asia",
            "year": 2025,
            "bounding_box": {
                "type": "Polygon",
                "coordinates": [bbox_coords],
                "crs": "EPSG:4326"
            },
            "landsat_sources": [
                "LANDSAT/LC08/C02/T1_L2",
                "LANDSAT/LC09/C02/T1_L2"
            ],
            "image_count": {
                "total": total_count_int,
                "landsat8": int(count_l8.getInfo()),
                "landsat9": int(count_l9.getInfo())
            }
        }

        return jsonify(response), 200

    except Exception as e:
        # If something fails (EE error, auth, etc.)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)
