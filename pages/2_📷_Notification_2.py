import time
import json
import streamlit as st
from datetime import date
import leafmap.foliumap as leafmap
import requests
import urllib.parse
import pytz
from skyfield.api import EarthSatellite, load
from datetime import datetime
import folium

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

@st.cache_data()
def get_TLE_data():
    # Landsat 9 
    url = 'https://www.n2yo.com/sat/gettle.php?s=49260'

    # Send a GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response (as JSON if it's a JSON API)
        data = response.json()  # Use .text for raw data as a string
        return data
    else:
        print(f"Error: {response.status_code}")


# Function to get current satellite coordinates and system time
def get_satellite_position(ts, satellite):
    # Get current time in UTC
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)

    # Convert the current time to the Skyfield time format
    time_now = ts.utc(utc_now.year, utc_now.month, utc_now.day, utc_now.hour, utc_now.minute, utc_now.second)

    # Get the satellite's position relative to Earth at the current time
    geocentric = satellite.at(time_now)

    # Convert geocentric coordinates to latitude, longitude, and altitude
    subpoint = geocentric.subpoint()
    latitude = subpoint.latitude.degrees
    longitude = subpoint.longitude.degrees
    altitude = subpoint.elevation.km

    # Get the system time in local format
    system_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = {
        "System_time": system_time,
        "LAT": latitude,
        "LONG": longitude,
        "ALT": altitude
    }
    return data


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

    # Retrieve TLE data only once and store in session_state to avoid refetching on every rerun
    if "landsat9_pos" not in st.session_state:
        st.session_state.landsat9_pos = get_TLE_data()

    landsat9_pos = st.session_state.landsat9_pos
    # TLE Data for Landsat 9
    tle_line1 = landsat9_pos[0]
    tle_line2 = landsat9_pos[1]

    # Create a timescale object
    ts = load.timescale()

    # Create the EarthSatellite object
    satellite = EarthSatellite(tle_line1, tle_line2, "Landsat 9", ts)

    # Continuously update satellite position every second
    while True:
        # Get the current position of the satellite
        satellite_pos = get_satellite_position(ts=ts, satellite=satellite)
        
        # Add satellite position as a marker on the map
        m.add_marker([satellite_pos['LAT'], satellite_pos["LONG"]],
                     popup="Satellite Real-time Position",
                     icon=folium.Icon(icon="satellite"))  # or any other valid folium icon
        
        # Display the map with updated satellite position
        m.to_streamlit()

        # Pause for 1 second and then rerun the app
        time.sleep(1)
        st.rerun()

# Run the app
app()
