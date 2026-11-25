# geo_server.py
import json
import math
from fastmcp import FastMCP
from shapely.geometry import Point, Polygon
from shapely import wkt as shapely_wkt

# Create the MCP server instance
mcp = FastMCP("Geo Tools Server")

@mcp.tool
def buffer_point(latitude: float, longitude: float, distance_km: float) -> str:
    """Create a circular buffer polygon around a geographic point.
    
    Args:
        latitude: Latitude of the center point in decimal degrees.
        longitude: Longitude of the center point in decimal degrees.
        distance_km: Radius of the buffer in kilometers.
    
    Returns:
        A JSON string containing the buffer geometry in WKT format and its approximate area in square kilometers.
    """
    try:
        # Create point (Shapely uses x=lon, y=lat)
        point = Point(longitude, latitude)
        
        # Approximate degrees per km at the given latitude
        deg_per_km = 1.0 / (111.32 * abs(math.cos(math.radians(latitude))))
        buffer_poly = point.buffer(distance_km * deg_per_km)
        
        return json.dumps({
            "buffer_wkt": buffer_poly.wkt,
            "area_sq_km": round(buffer_poly.area * (111.32 ** 2) * abs(math.cos(math.radians(latitude))), 2)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool
def distance_between_points(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Calculate the geodesic distance between two geographic points using the Haversine formula.
    
    Args:
        lat1: Latitude of the first point.
        lon1: Longitude of the first point.
        lat2: Latitude of the second point.
        lon2: Longitude of the second point.
    
    Returns:
        A JSON string with the distance in kilometers.
    """
    try:
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        return json.dumps({"distance_km": round(distance, 3)})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool
def point_in_polygon(latitude: float, longitude: float, polygon_wkt: str) -> str:
    """Check whether a geographic point lies inside a polygon defined in WKT.
    
    Args:
        latitude: Latitude of the point.
        longitude: Longitude of the point.
        polygon_wkt: A Well-Known Text (WKT) string of the polygon, e.g. 'POLYGON ((...))'.
    
    Returns:
        A JSON string with a boolean 'inside' field.
    """
    try:
        point = Point(longitude, latitude)
        polygon = shapely_wkt.loads(polygon_wkt)
        return json.dumps({"inside": point.within(polygon)})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Run with stdio transport (default for local MCP clients)
    mcp.run()