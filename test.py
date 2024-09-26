import requests
import pprint
# URL for the LLook Outlines service
USGS_URL = "https://nimbus.cr.usgs.gov/arcgis/rest/services/LLook_Outlines/MapServer/1/query"

def fetch_usgs_data():
    params = {
        "returnGeometry": "true",
        "where": "PATH IN (91,107) AND MODE='D'",
        "outSr": "4326",
        "outFields": "*",
        "inSr": "4326",
        "geometry": '{"xmin":-180,"ymin":0,"xmax":0,"ymax":85.0511287798066,"spatialReference":{"wkid":4326}}',
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "geometryPrecision": "6",
        "f": "json"
    }
    
    response = requests.get(USGS_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        
        return None
    


pprint.pprint(fetch_usgs_data())    