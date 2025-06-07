import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import AntPath
from io import BytesIO
from streamlit_folium import st_folium
from sky_brain import detect_conflicts

st.set_page_config(page_title="🛫 AIero Conflict Detector", layout="wide")
st.title("🛫 AIero Conflict Detector")

uploaded_file = st.file_uploader("Upload a CSV with flight data", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required = {'flight_id', 'lat', 'lon', 'altitude', 'timestamp'}
    if not required.issubset(df.columns):
        st.error(f"Missing columns. Required: {required}")
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        st.subheader("📄 Uploaded Flight Data")
        st.dataframe(df)

        st.subheader("🧠 Detected Conflicts")
        conflicts = detect_conflicts(df)
        st.dataframe(conflicts)

        # Plot Longitude vs Latitude
        st.subheader("📍 Flight Paths (Longitude vs Latitude)")
        fig, ax = plt.subplots(figsize=(10, 6))
        for flight_id, group in df.groupby("flight_id"):
            ax.scatter(group["lon"], group["lat"], label=flight_id)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize='small')
        st.pyplot(fig)

        # Altitude Over Time with legend BELOW
        st.subheader("📈 Altitude Over Time")
        fig_alt, ax_alt = plt.subplots(figsize=(10, 6))
        for flight_id, group in df.groupby("flight_id"):
            ax_alt.plot(group["timestamp"], group["altitude"], marker='x', linestyle='', label=flight_id)
        ax_alt.set_xlabel("Timestamp")
        ax_alt.set_ylabel("Altitude")
        ax_alt.set_title("Altitude Over Time")
        ax_alt.legend(
            title="Flights",
            loc='upper center',
            bbox_to_anchor=(0.5, -0.3),
            ncol=5,
            fontsize='small'
        )
        st.pyplot(fig_alt)

        # World Map
        st.subheader("🌍 World Map of Flight Paths")
        m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=2)
        for flight_id, group in df.groupby("flight_id"):
            coords = list(zip(group["lat"], group["lon"]))
            AntPath(locations=coords, tooltip=flight_id).add_to(m)
        st_folium(m, width=700, height=500)
