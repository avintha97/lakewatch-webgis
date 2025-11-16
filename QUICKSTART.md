# Quick Reference - LakeWatch WebGIS Setup

## 5-Minute Quick Start

### 1. Install Backend Dependencies
```powershell
cd d:\Data\Projects\Web-gis\LakeWatch-webgis
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Setup PostgreSQL
- **Option A (Easy)**: Use Docker
  ```powershell
  # If you have Docker installed
  docker run --name lakewatch-postgres \
    -e POSTGRES_PASSWORD=postgres \
    -p 5432:5432 \
    postgis/postgis:latest
  ```

- **Option B (Manual)**: See `DATABASE_SETUP.md`

### 3. Configure .env
```
EE_PROJECT=your-ee-project
HIVOLUME_URL=https://example.com
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/lakewatch
```

### 4. Install Frontend Dependencies
```powershell
cd client
npm install
```

### 5. Run Application

**Terminal 1:**
```powershell
cd d:\Data\Projects\Web-gis\LakeWatch-webgis
.\venv\Scripts\Activate.ps1
python server\app.py
```

**Terminal 2:**
```powershell
cd d:\Data\Projects\Web-gis\LakeWatch-webgis\client
npm start
```

Visit: http://localhost:3000

---

## Key Files

| File | Purpose |
|------|---------|
| `server/app.py` | Flask backend with API endpoints |
| `server/database.py` | PostgreSQL connection & init |
| `server/models.py` | SQLAlchemy ORM models |
| `client/src/pages/MapPage.jsx` | Interactive Leaflet map |
| `.env` | Configuration (NEEDS DATABASE_URL) |
| `DATABASE_SETUP.md` | PostgreSQL detailed setup |
| `SETUP_GUIDE.md` | Complete installation guide |

---

## API Endpoints

### Analysis API (NEW)
- `POST /api/v1/analysis/save` - Save analysis to database
- `GET /api/v1/analysis/list` - Get all analyses
- `GET /api/v1/analysis/{id}` - Get specific analysis

### Water Calculation (EXISTING)
- `POST /api/v1/lakes/area` - Calculate water area from bbox

### Health Checks
- `GET /api/v1/health` - Server status
- `GET /api/v1/env-check` - Environment variables

---

## NPM Packages Added

```
leaflet                 # Map rendering
react-leaflet          # React wrapper for Leaflet
leaflet-draw          # Drawing tools
react-leaflet-draw    # React wrapper for drawing
axios                 # HTTP client (already in client)
```

---

## Python Packages Added

```
flask-cors            # CORS support
sqlalchemy            # ORM
psycopg2-binary       # PostgreSQL driver
geoalchemy2           # PostGIS support
shapely               # Geometry handling
```

---

## Troubleshooting

### Map not loading
```powershell
# Check backend is running
curl http://localhost:5000/api/v1/health
```

### Database connection error
```powershell
# Test PostgreSQL connection
psql -U postgres -h localhost -d lakewatch
```

### Module not found errors
```powershell
# Reinstall all packages
pip install -r requirements.txt --force-reinstall
cd client && npm install
```

---

## File Tree

```
LakeWatch-webgis/
├── server/
│   ├── app.py                    [UPDATED] ✓ New endpoints + CORS
│   ├── database.py               [NEW] ✓ Database helpers
│   ├── models.py                 [NEW] ✓ ORM models
│   └── ee_area.py                [UNCHANGED] ✓
├── client/src/
│   ├── App.js                    [UPDATED] ✓ New route
│   ├── pages/
│   │   ├── Home.jsx              [UNCHANGED] ✓
│   │   └── MapPage.jsx           [NEW] ✓ Interactive map
│   ├── components/
│   │   └── LakeAreaCalculator.jsx [UPDATED] ✓ Nav button
│   └── styles/
│       ├── MapPage.css           [NEW] ✓ Map styling
│       └── LakeAreaCalculator.css [UPDATED] ✓ Nav styling
├── requirements.txt              [UPDATED] ✓ New packages
├── .env                          [NEEDS UPDATE] ⚠ Add DATABASE_URL
├── DATABASE_SETUP.md            [NEW] ✓ PostgreSQL guide
└── SETUP_GUIDE.md               [NEW] ✓ Full setup guide
```

---

## Next: Create Database

See `DATABASE_SETUP.md` for:
1. PostgreSQL installation
2. PostGIS setup
3. Database creation
4. Connection testing

---

## Support

- **Stuck?** Check `SETUP_GUIDE.md` troubleshooting section
- **Questions?** See API documentation in `SETUP_GUIDE.md`
- **Issues?** Review logs in browser console (F12) and Flask terminal
