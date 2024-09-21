import streamlit as st
import leafmap.foliumap as leafmap

# Set page layout to wide
st.set_page_config(layout="wide")

# Sidebar Information
st.sidebar.info(
    """
    - Web App URL: [Github](https://github.com/NaheedRayan/landsat-pulse)
    - GitHub repository: [Github](https://github.com/NaheedRayan/landsat-pulse)
    """
)

# Sidebar Contact Title and Info
st.sidebar.title("Contact")
st.sidebar.info(
    """
    Quantum Voyagers at [GitHub](https://github.com/NaheedRayan/landsat-pulse)
    """
)




m = leafmap.Map(minimap_control=True ,draw_export=True)
m.add_basemap("OpenTopoMap")
m.add_xyz_service("qms.Google Satellite Hybrid")

m.to_streamlit()