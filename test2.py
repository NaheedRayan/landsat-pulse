import requests
import pprint

# USGS API URL for LLook Outlines service
USGS_URL = "https://nimbus.cr.usgs.gov/arcgis/rest/services/LLook_Outlines/MapServer/1/query"

def fetch_usgs_path_data(paths):
    # Convert paths list to a tuple for immutability
    paths = tuple(paths)
    
    # Format paths into a string for the SQL-like query
    paths_string = ', '.join(map(str, paths))  # Convert to a string like "25, 45, 56, 23"
    
    # Define the parameters for the API request
    params = {
        "returnGeometry": "true",  # Return the geometry of the features
        "where": f"PATH IN ({paths_string}) AND MODE='D'",  # SQL-like query condition
        "outSr": "4326",  # Output spatial reference
        "outFields": "*",  # Request all fields
        "inSr": "4326",  # Input spatial reference
        "geometry": '{"xmin":-180,"ymin":0,"xmax":0,"ymax":85.0511287798066,"spatialReference":{"wkid":4326}}',  # Bounding box geometry
        "geometryType": "esriGeometryEnvelope",  # Type of geometry
        "spatialRel": "esriSpatialRelIntersects",  # Spatial relationship
        "geometryPrecision": "6",  # Precision of the geometry
        "f": "geojson"  # Request GeoJSON format
    }
    
    try:
        # Send a GET request to the USGS service
        response = requests.get(USGS_URL, params=params)
        
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return response.json()  # Return the GeoJSON response
        else:
            print("Failed to load USGS data. Status Code:", response.status_code)
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
paths = [16]  # Define paths to query
usgs_data = fetch_usgs_path_data(paths)

if usgs_data:
    pprint.pprint(usgs_data)  # Process the data as needed
