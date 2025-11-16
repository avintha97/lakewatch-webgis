# PostgreSQL Setup Guide for LakeWatch WebGIS

## Quick Start

This guide helps you set up PostgreSQL and PostGIS for the LakeWatch WebGIS project.

## Prerequisites

- PostgreSQL 12+ (download from https://www.postgresql.org/download/)
- PostGIS extension (included with PostgreSQL on Windows via EnterpriseDB installer)

## Installation Steps

### 1. Install PostgreSQL (Windows)

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer and follow the wizard
3. **Important:** Remember the password you set for the `postgres` user
4. Accept default port: `5432`
5. During installation, make sure to install **PostGIS** as an extension

### 2. Create Database and Enable PostGIS

After PostgreSQL is installed, open **pgAdmin** (included with PostgreSQL):

#### Option A: Using pgAdmin GUI
1. Open pgAdmin from Windows Start menu
2. Expand **Servers** > **PostgreSQL 15** (or your version)
3. Right-click on **Databases** → **Create** → **Database**
4. Name: `lakewatch`
5. Owner: `postgres`
6. Click **Save**

7. Right-click on the new `lakewatch` database → **Query Tool**
8. Paste the SQL below and execute:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

#### Option B: Using Command Line

Open **Command Prompt** or **PowerShell** and run:

```powershell
# Connect to PostgreSQL (you'll be prompted for password)
psql -U postgres -h localhost

# In the psql prompt:
CREATE DATABASE lakewatch;
\c lakewatch
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
\q
```

### 3. Configure LakeWatch .env File

In the project root directory (`d:\Data\Projects\Web-gis\LakeWatch-webgis\.env`), add:

```
EE_PROJECT=your-ee-project-id
HIVOLUME_URL=https://example.com
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/lakewatch
```

**Replace `your_password`** with the password you set during PostgreSQL installation.

### 4. Verify Connection

From the LakeWatch project root, test the connection:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements (if not already done)
pip install -r requirements.txt

# Test the connection
python -c "from database import init_database; init_database(); print('✓ Database connected!')"
```

## Database Schema

The application automatically creates the `lake_analysis` table with the following structure:

```sql
CREATE TABLE lake_analysis (
    id SERIAL PRIMARY KEY,
    geometry geometry(Polygon, 4326) NOT NULL,
    date VARCHAR(10) NOT NULL,
    threshold INTEGER NOT NULL,
    water_area_km2 FLOAT NOT NULL,
    pixel_count INTEGER NOT NULL,
    submission_date VARCHAR(10) NOT NULL,
    satellite VARCHAR(50) NOT NULL DEFAULT 'Sentinel-1',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_lake_analysis_date ON lake_analysis(date);
CREATE INDEX idx_lake_analysis_created_at ON lake_analysis(created_at);
CREATE INDEX idx_lake_analysis_geometry ON lake_analysis USING GIST(geometry);
```

## Troubleshooting

### "Connection refused" Error
- Make sure PostgreSQL service is running
- Check if the service is running: `Services` → Search → `PostgreSQL 15 Server`
- Restart the service if needed

### "Database lakewatch does not exist" Error
- Create the database following steps in section 2

### "EXTENSION postgis does not exist" Error
- PostGIS was not installed during PostgreSQL setup
- Solution: Reinstall PostgreSQL and check the PostGIS option during installation

### "psycopg2 error" in Python
- Make sure all requirements are installed: `pip install -r requirements.txt`
- Verify DATABASE_URL format in `.env`

## Testing the Setup

Once everything is installed, test with a sample query:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Test in Python
python -c "
from database import init_database, get_session
from models import LakeAnalysis

# Initialize and create tables
init_database()

# Get a session and query
session = get_session()
count = session.query(LakeAnalysis).count()
session.close()

print(f'✓ Database ready! Current record count: {count}')
"
```

## Next Steps

1. Start the Flask backend server:
```powershell
python server\app.py
```

2. In another terminal, start the React client:
```powershell
cd client
npm start
```

3. Open http://localhost:3000 and navigate to the interactive map

## Useful PostgreSQL Commands

```powershell
# Connect to database
psql -U postgres -h localhost -d lakewatch

# List all tables
\dt

# View table structure
\d lake_analysis

# Query sample data
SELECT id, date, water_area_km2 FROM lake_analysis LIMIT 5;

# Delete all data
DELETE FROM lake_analysis;

# Drop database (careful!)
DROP DATABASE lakewatch;
```

## Performance Tips

- For large numbers of analyses, consider archiving old records
- Use the `limit` and `offset` parameters in the API to paginate results
- PostGIS indexes improve spatial queries significantly

## Support

For issues with:
- **PostgreSQL**: https://www.postgresql.org/support/
- **PostGIS**: https://postgis.net/
- **LakeWatch**: Check project README.md
