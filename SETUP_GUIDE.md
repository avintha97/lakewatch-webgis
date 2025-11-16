# LakeWatch WebGIS Installation & Setup Guide

## Project Structure

```
LakeWatch-webgis/
├── server/                          # Flask backend
│   ├── app.py                       # Main Flask app with API endpoints
│   ├── ee_area.py                   # Earth Engine helpers for water calculation
│   ├── models.py                    # SQLAlchemy ORM models (NEW)
│   ├── database.py                  # Database initialization (NEW)
│   └── __pycache__/
├── client/                          # React frontend
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js                   # Updated with new routes
│       ├── pages/
│       │   ├── Home.jsx
│       │   └── MapPage.jsx          # Interactive map with drawing (NEW)
│       ├── components/
│       │   └── LakeAreaCalculator.jsx   # Updated with navigation button
│       └── styles/
│           ├── Home.css
│           ├── LakeAreaCalculator.css   # Updated with nav styles
│           └── MapPage.css          # Map styling (NEW)
├── requirements.txt                 # Updated with database packages
├── .env                             # Environment configuration (NEEDS DATABASE_URL)
└── DATABASE_SETUP.md               # PostgreSQL setup guide (NEW)
```

## New Features

### 1. Interactive Map Interface (`MapPage.jsx`)
- **Leaflet Map** with OpenStreetMap tiles centered on Sri Lanka
- **Polygon Drawing Tools**: Draw, edit, and delete analysis areas
- **Real-time Analysis**: Integrated water calculation from Sentinel-1
- **Modal Form**: Configure analysis parameters (date, threshold, notes)
- **Results Panel**: View analysis results with record ID
- **Analysis History**: View previously saved analyses with timestamps
- **Responsive Design**: Works on desktop and mobile devices

### 2. PostgreSQL Database Integration
- **Automatic Schema Creation**: Tables created on first run
- **PostGIS Support**: Stores geometries as spatial data
- **ORM Models**: SQLAlchemy for type-safe database operations
- **RESTful API**: Endpoints for saving and retrieving analyses

### 3. New API Endpoints

#### Save Analysis
```
POST /api/v1/analysis/save
Content-Type: application/json

{
  "geometry": {"type": "Polygon", "coordinates": [[[lon, lat], ...]]},
  "date": "2025-01-27",
  "threshold": -17,
  "water_area_km2": 45.1234,
  "pixel_count": 451234,
  "submission_date": "2025-01-27",
  "satellite": "Sentinel-1",
  "notes": "Optional notes"
}

Response:
{
  "id": 1,
  "status": "saved",
  "message": "Analysis saved successfully"
}
```

#### Get All Analyses
```
GET /api/v1/analysis/list?limit=100&offset=0

Response:
{
  "count": 5,
  "returned": 5,
  "limit": 100,
  "offset": 0,
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
    }
  ]
}
```

#### Get Single Analysis
```
GET /api/v1/analysis/{id}

Response:
{
  "status": "ok",
  "analysis": {...}
}
```

## Installation Instructions

### Step 1: Backend Setup

```powershell
# Navigate to project root
cd d:\Data\Projects\Web-gis\LakeWatch-webgis

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install updated dependencies
pip install -r requirements.txt

# Note: New packages added:
# - flask-cors (4.0.0)
# - sqlalchemy (2.0.23)
# - psycopg2-binary (2.9.9)
# - geoalchemy2 (0.14.1)
# - shapely (2.0.2)
```

### Step 2: PostgreSQL Setup

See `DATABASE_SETUP.md` for detailed instructions. Quick version:

```powershell
# 1. Install PostgreSQL with PostGIS (if not already installed)
# Download: https://www.postgresql.org/download/windows/

# 2. Create database and enable PostGIS
# Use pgAdmin or command line (see DATABASE_SETUP.md)

# 3. Add DATABASE_URL to .env
# Example: postgresql+psycopg2://postgres:password@localhost:5432/lakewatch
```

### Step 3: Update .env File

```
EE_PROJECT=your-earth-engine-project
HIVOLUME_URL=https://example.com
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/lakewatch
```

### Step 4: Frontend Setup

```powershell
# Navigate to client directory
cd client

# Install React dependencies (including new map packages)
npm install

# New packages installed:
# - leaflet (1.9.x)
# - react-leaflet (4.x)
# - leaflet-draw (1.0.x)
# - react-leaflet-draw (0.20.x)

# The packages should already be in package.json from npm install
```

### Step 5: Start the Application

**Terminal 1 - Backend:**
```powershell
cd d:\Data\Projects\Web-gis\LakeWatch-webgis
.\venv\Scripts\Activate.ps1
python server\app.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```powershell
cd d:\Data\Projects\Web-gis\LakeWatch-webgis\client
npm start
# Client runs on http://localhost:3000
```

**Terminal 3 - Optional: Database monitor**
```powershell
# Monitor database in pgAdmin
# http://localhost:5050
```

## Usage Guide

### Using the Interactive Map

1. **Navigate to Map**
   - Click "🗺️ Go to Interactive Map" button on calculator page
   - Or directly visit `/map` route

2. **Draw Polygon**
   - Click the drawing tools on the top-left of the map
   - Draw a rectangle or polygon around your analysis area
   - Click to add points, press Enter or right-click to finish

3. **Configure Analysis**
   - Modal form appears after drawing
   - Set target date (±5 days for satellite search)
   - Adjust VV/VH threshold if needed (default: -17 dB)
   - Add optional notes
   - Click "🔍 Analyze & Save"

4. **View Results**
   - Floating panel shows water area in km²
   - Record ID indicates database storage
   - Timestamp shows submission time
   - Click "✨ New Analysis" to analyze another area

5. **View History**
   - Click "📋 Analysis History" button
   - View all previously saved analyses
   - Shows date, area, satellite, and notes

6. **Clear Data**
   - Click "🗑️ Clear All" to reset map and results
   - Clears drawing but keeps database records

### Using the Calculator (Original)

The original calculator still works:
- Navigate to `/calculator`
- Manually enter coordinates or modify default values
- Click "📊 Calculate Water Area"
- Results shown in table format
- Results are **not automatically saved** to database

## Environment Variables

Create `.env` file in project root with:

```
# Earth Engine Configuration
EE_PROJECT=ee-your-project-id

# External URL (optional)
HIVOLUME_URL=https://example.com

# PostgreSQL Database
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/lakewatch
```

## API Documentation

### Health Check
```
GET /api/v1/health
→ {"status": "ok", "message": "Flask server is running"}
```

### Environment Check
```
GET /api/v1/env-check
→ {"EE_PROJECT": "...", "HIVOLUME_URL": "..."}
```

### Water Area Calculation (Existing)
```
POST /api/v1/lakes/area
→ {"water_area_km2": 45.1234, "pixel_count": 451234, ...}
```

### Save Analysis (New)
```
POST /api/v1/analysis/save
→ {"id": 1, "status": "saved"}
```

### List Analyses (New)
```
GET /api/v1/analysis/list
→ {"count": 5, "analyses": [...]}
```

### Get Single Analysis (New)
```
GET /api/v1/analysis/{id}
→ {"status": "ok", "analysis": {...}}
```

## Troubleshooting

### React Dependencies Not Installed

```powershell
cd client
npm install leaflet react-leaflet leaflet-draw react-leaflet-draw axios
```

### Map Not Displaying

1. Check browser console for errors (F12)
2. Verify Flask backend is running on port 5000
3. Check CORS is enabled in `app.py`
4. Clear browser cache and reload

### Database Connection Errors

1. Verify PostgreSQL service is running
2. Check DATABASE_URL format in .env
3. Ensure database and `lakewatch` table exist
4. Test connection: `python -c "from database import init_database; init_database()"`

### Earth Engine Errors

```powershell
# Re-authenticate Earth Engine
python -c "import ee; ee.Authenticate(); ee.Initialize(project='YOUR_PROJECT')"
```

### Port Already in Use

```powershell
# Flask (5000)
lsof -i :5000
# Kill process: taskkill /PID <pid> /F

# React (3000)
lsof -i :3000
# Kill process: taskkill /PID <pid> /F
```

## Performance Optimization

- **Map Rendering**: Leaflet is lightweight; handles large areas efficiently
- **Database Queries**: PostGIS indexes improve spatial queries
- **API Calls**: Results are cached in component state
- **Batch Operations**: Use limit/offset for large result sets

## Testing

```powershell
# Test backend endpoints
curl http://localhost:5000/api/v1/health

# Test database
python -c "
from database import init_database, get_session
from models import LakeAnalysis

init_database()
session = get_session()
print(f'Records in database: {session.query(LakeAnalysis).count()}')
session.close()
"

# Test React build
cd client
npm run build
```

## File Changes Summary

### Created Files
- ✅ `server/database.py` - Database initialization and helpers
- ✅ `server/models.py` - SQLAlchemy ORM models
- ✅ `client/src/pages/MapPage.jsx` - Interactive map component
- ✅ `client/src/styles/MapPage.css` - Map styling
- ✅ `DATABASE_SETUP.md` - PostgreSQL setup guide

### Modified Files
- ✅ `client/src/App.js` - Added MapPage route
- ✅ `client/src/components/LakeAreaCalculator.jsx` - Added navigation button
- ✅ `client/src/styles/LakeAreaCalculator.css` - Added navigation styles
- ✅ `server/app.py` - Added CORS, database initialization, new endpoints
- ✅ `requirements.txt` - Added database and map packages

## Next Steps

1. **Backup**: Backup any existing data before deployment
2. **Test**: Run through the usage guide with test data
3. **Deploy**: Set up production database and environment
4. **Monitor**: Check Flask logs and database performance

## Support & Documentation

- **Earth Engine**: https://developers.google.com/earth-engine
- **Leaflet**: https://leafletjs.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **PostGIS**: https://postgis.net/documentation/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

---

**Last Updated**: November 16, 2025  
**Version**: 2.0 (with PostgreSQL and Interactive Map)
