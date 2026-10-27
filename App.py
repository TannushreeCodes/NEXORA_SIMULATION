import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="NEXORA GIS",
    layout="wide"
)

st.title("🗺️ NEXORA — GIS Intelligence")

# Load building data
df = pd.read_csv("data/building.csv")

# Campus center
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

# Create map
m = folium.Map(
    location=[center_lat,center_lon],
    zoom_start=16
)

# Add buildings
for _, row in df.iterrows():

    if row["risk"] == "High":
        color = "red"
    elif row["risk"] == "Medium":
        color = "orange"
    else:
        color = "green"

    popup = f"""
    <b>{row['building']}</b><br>
    Energy: {row['energy_status']}<br>
    Water: {row['water_status']}<br>
    Waste: {row['waste_status']}<br>
    Risk: {row['risk']}
    """

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup,
        tooltip=row["building"],
        icon=folium.Icon(color=color)
    ).add_to(m)

# Display map
st_folium(m, width=1200, height=600)