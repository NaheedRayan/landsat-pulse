import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

st.sidebar.info(
    """
    - Web App URL: <https://github.com/NaheedRayan/landsat-pulse>
    - GitHub repository: <https://github.com/NaheedRayan/landsat-pulse>
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Quantum Voyagers at [GitHub](https://github.com/NaheedRayan/landsat-pulse 
    """
)


# import pandas as pd
# import numpy as np

# df = pd.DataFrame(
#     np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
#     columns=["lat", "lon"],
# )
# st.map(df)

m = leafmap.Map(minimap_control=True)
m.add_basemap("OpenTopoMap")
# m.to_streamlit(height=600)
m.to_streamlit()