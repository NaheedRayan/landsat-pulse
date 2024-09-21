# import ee
import json
import os
import warnings
import datetime
# import fiona
# import geopandas as gpd
import folium
import streamlit as st
# import geemap.colormaps as cm
# import geemap.foliumap as geemap
from datetime import date
# from shapely.geometry import Polygon
import streamlit as st
import leafmap.foliumap as leafmap
import json




def app():
    today = date.today()

    st.title("LandSat Satellite path")


    # Create a leafmap map with minimap control
    m = leafmap.Map(minimap_control=True)

    # Allow users to upload a GeoJSON file
    st.sidebar.title("Upload GeoJSON")
    uploaded_file = st.sidebar.file_uploader("Choose a GeoJSON file", type="geojson")

    if uploaded_file:
        try:
            # Load the GeoJSON data
            geojson_data = json.load(uploaded_file)  # Read the file directly as JSON

            # Add the GeoJSON to the map
            m.add_geojson(geojson_data, layer_name="Uploaded GeoJSON")

            st.sidebar.success("GeoJSON data successfully loaded and displayed on the map.")
        except Exception as e:
            st.sidebar.error(f"Error loading GeoJSON: {e}")

    # Optionally, add some basemaps
    m.add_basemap("OpenTopoMap")
    m.add_xyz_service("qms.Google Satellite Hybrid")

    # Display the map with the uploaded GeoJSON layer (if any)
    m.to_streamlit()




app()