import json
import streamlit as st
from datetime import date
import leafmap.foliumap as leafmap
import requests
import urllib.parse

# URLs for the Landsat path and cycle data
LANDSAT_DATA_URL = "https://landsat.usgs.gov/sites/default/files/landsat_acq/assets/json/cycles_full.json"

# Caching the function to fetch data from the URL
@st.cache_data()
def fetch_landsat_data():
    try:
        response = requests.get(LANDSAT_DATA_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.error("Failed to load Landsat data.")
            return None
    except Exception as e:
        st.sidebar.error(f"Error fetching Landsat data: {e}")
        return None

# URL for the USGS LLook Outlines service
USGS_URL = "https://nimbus.cr.usgs.gov/arcgis/rest/services/LLook_Outlines/MapServer/1/query"

def fetch_usgs_path_data(custom_paths):
    # Base URL
    base_url = USGS_URL
    
    # Parameters
    params = {
        "returnGeometry": "true",
        "where": f"PATH IN ({','.join(map(str, custom_paths))}) AND MODE='D'",
        "outSr": "4326",
        "outFields": "*",
        "inSr": "4326",
        "geometry": '{"xmin":-180,"ymin":-85.0511287798066,"xmax":180,"ymax":85.0511287798066,"spatialReference":{"wkid":4326}}',
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "geometryPrecision": "6",
        "f": "geojson"
    }

    # Encode parameters
    query_string = urllib.parse.urlencode(params)

    # Construct full URL
    full_url = f"{base_url}?{query_string}"
    try:
        response = requests.get(full_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.error("Failed to load USGS data.")
            return None
    except Exception as e:
        st.sidebar.error(f"Error fetching USGS path data: {e}")
        return None

# Main app function
def app():
    st.set_page_config(layout="wide")
    
    today = date.today()
    st.title("LandSat Satellite Path and Cycle")

    # Initialize the map with a minimap control
    m = leafmap.Map(minimap_control=True)

    # Sidebar for GeoJSON upload
    st.sidebar.title("Upload GeoJSON")
    uploaded_file = st.sidebar.file_uploader("Choose a GeoJSON file", type="geojson")
    
    if uploaded_file:
        try:
            geojson_data = json.load(uploaded_file)
            m.add_geojson(geojson_data, layer_name="Uploaded GeoJSON")
            st.sidebar.success("GeoJSON data successfully loaded and displayed on the map.")
        except Exception as e:
            st.sidebar.error(f"Error loading GeoJSON: {e}")

    # Add basemap layers
    m.add_basemap("OpenTopoMap")
    m.add_xyz_service("qms.Google Satellite Hybrid")

    # Fetch Landsat data (cached)
    landsat_data = fetch_landsat_data()
    
    if landsat_data is None:
        return

    st.sidebar.title("Landsat Path and Cycles")

    # Satellite selection
    satellite = st.sidebar.selectbox("Select a satellite", ["Landsat 9", "Landsat 8", "Landsat 7"])

    # Date selection
    selected_date = st.sidebar.date_input("Select a date", today)
    selected_date_str = selected_date.strftime("%m/%d/%Y").lstrip("0").replace("/0", "/")

    # Check for the selected satellite's data
    satellite_key = satellite.lower().replace(" ", "_")
    
    if selected_date_str in landsat_data.get(satellite_key, {}):
        data_for_date = landsat_data[satellite_key][selected_date_str]
        paths = data_for_date["path"].split(",")
        cycle = data_for_date["cycle"]

        st.sidebar.write(f"Paths for {selected_date_str}: {', '.join(paths)}")
        st.sidebar.write(f"Cycle: {cycle}")

        # Fetch path data from USGS
        rows = fetch_usgs_path_data(paths)
        if rows is None or 'features' not in rows:
            st.sidebar.error("Failed to fetch valid USGS path data.")
            return
        
        # Create a GeoJSON structure to hold path data
        path_geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for row in rows['features']:
            path_geojson["features"].append(row)

        # Add the generated GeoJSON to the map
        m.add_geojson(path_geojson, layer_name=f"Paths on {selected_date_str}")
    else:
        st.sidebar.error(f"No path data available for {selected_date_str}")

    # Display the map with all layers
    m.to_streamlit()

# Run the app
app()
