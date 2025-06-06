import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import AntPath
from io import BytesIO
from streamlit_folium import st_folium

st.set_page_config(page_title="AIero Conflict Detector", layout="wide")
st.title("✈️ AIero Conflict Detector")

uploaded_file = st.file_uploader("Upload a CSV with flight data", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Check required columns
    required = {'flight_id', 'lat', 'lon', 'altitude', 'timestamp'}
    if not required.issubset(df.columns):
        st.error(f"Missing columns. Required: {required}")
    else:
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        st.subheader("📊 Uploaded Flight Data")
        st.dataframe(df)

        # Plot 1: Flight Paths
        st.subheader("🛫 Flight Paths (Longitude vs Latitude)")
        fig1, ax1 = plt.subplots()
        for flight_id, group in df.groupby('flight_id'):
            ax1.plot(group['lon'], group['lat'], marker='o', label=flight_id)
        ax1.set_xlabel('Longitude')
        ax1.set_ylabel('Latitude')
        ax1.legend()
        st.pyplot(fig1)

        # Plot 2: Altitude over Time
        st.subheader("📈 Altitude Over Time")
        fig2, ax2 = plt.subplots()
        for flight_id, group in df.groupby('flight_id'):
            ax2.plot(group['timestamp'], group['altitude'], marker='x', label=flight_id)
        ax2.set_xlabel('Timestamp')
        ax2.set_ylabel('Altitude')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend()
        st.pyplot(fig2)

        # Plot 3: Interactive World Map
        st.subheader("🌍 World Map of Flight Paths")
        world_map = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=3)
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        for i, (flight_id, group) in enumerate(df.groupby('flight_id')):
            coords = list(zip(group['lat'], group['lon']))
            folium.PolyLine(coords, color=colors[i % len(colors)], weight=3, opacity=0.8, tooltip=flight_id).add_to(world_map)

        st_folium(world_map, width=800, height=500)
