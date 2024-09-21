import streamlit as st
import leafmap.foliumap as leafmap
import json

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
