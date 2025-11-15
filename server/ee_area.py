import ee


def make_geometry_from_bbox(bbox_coords):
    """Convert closed [lon, lat] polygon list to EE geometry."""
    return ee.Geometry.Polygon(bbox_coords)

def count_landsat_images_by_year(bbox_coords, year):
    """
    Count the number of Landsat 8/9 images for a given year and bbox.
    
    Args:
        bbox_coords: closed polygon list of [lon, lat] points
        year: integer year (e.g., 2025)
    
    Returns:
        dict with keys: year, image_count, start_date, end_date
    """
    geometry = make_geometry_from_bbox(bbox_coords)
    
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    # Build Landsat 8/9 collection
    ls8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").filterBounds(geometry).filterDate(start_date, end_date)
    ls9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2").filterBounds(geometry).filterDate(start_date, end_date)
    
    # Merge and get size
    combined = ls8.merge(ls9)
    image_count = combined.size().getInfo()
    
    return {
        "year": year,
        "image_count": image_count,
        "start_date": start_date,
        "end_date": end_date
    }