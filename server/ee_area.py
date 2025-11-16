import ee
from datetime import datetime, timedelta


def make_geometry_from_bbox(bbox_coords):
    """Convert closed [lon, lat] polygon list to EE geometry."""
    return ee.Geometry.Polygon(bbox_coords)


def calculate_water_area_sentinel1(bbox_coords, target_date_str, vv_vh_threshold=-17):
    """
    Calculate water area using Sentinel-1 SAR (VV/VH ratio).
    Filters images for ±5 days around target_date and uses latest image.
    
    Args:
        bbox_coords: closed polygon list of [lon, lat] points
        target_date_str: date string in format "YYYY-MM-DD" (e.g., "2025-01-27")
        vv_vh_threshold: VV-VH threshold in dB for water detection (default -17)
    
    Returns:
        dict with water_area_km2, pixel_count, dates, and metadata
    """
    geometry = make_geometry_from_bbox(bbox_coords)
    
    # Parse target date and calculate ±5 day range
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    start_date = (target_date - timedelta(days=5)).strftime("%Y-%m-%d")
    end_date = (target_date + timedelta(days=5)).strftime("%Y-%m-%d")
    
    # Build Sentinel-1 GRD collection (IW mode, VV+VH)
    s1 = (ee.ImageCollection("COPERNICUS/S1_GRD")
          .filterBounds(geometry)
          .filterDate(start_date, end_date)
          .filter(ee.Filter.eq('instrumentMode', 'IW')))
    
    # Get latest image
    latest_image = s1.sort("system:time_start", False).first()
    
    # Extract VV and VH bands (in dB)
    vv = latest_image.select('VV')
    #vh = latest_image.select('VH')
    
    # Calculate VV - VH ratio for water detection
    #ratio = vv.subtract(vh)
    
    # Filter for water pixels (ratio <= threshold, e.g., -17 dB means low backscatter = water)
    water_pixels = vv.lte(vv_vh_threshold)
    
    # Calculate area: scale=10 means 10m pixels; each pixel = 100 m² = 0.0001 km²
    pixel_area = ee.Image.pixelArea()
    water_area_m2 = water_pixels.multiply(pixel_area).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e10
    )
    
    water_area_m2_value = water_area_m2.get('VV').getInfo()
    water_area_km2 = water_area_m2_value / 1e6 if water_area_m2_value else 0
    
    # Count water pixels
    pixel_count_result = water_pixels.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e10
    )
    pixel_count_value = pixel_count_result.get('VV').getInfo()
    
    return {
        "target_date": target_date_str,
        "start_date": start_date,
        "end_date": end_date,
        "water_area_km2": round(water_area_km2, 4),
        "pixel_count": int(pixel_count_value) if pixel_count_value else 0,
        "vv_vh_threshold_db": vv_vh_threshold,
        "satellite": "Sentinel-1"
    }