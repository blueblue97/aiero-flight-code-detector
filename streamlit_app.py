import streamlit as st
from opensky_api import OpenSkyApi
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# OpenSky login from secrets
api = OpenSkyApi(
    username=st.secrets["opensky_username"],
    password=st.secrets["opensky_password"]
)

st.title("🛫 Flight Conflict Detector by Flight Number")

flight_number = st.text_input("Enter Flight Number (e.g., TP344)")

if flight_number:
    st.write(f"Searching for flight: **{flight_number.upper()}**")

    states = api.get_states()

    target = None
    for s in states.states:
        if s.callsign and flight_number.upper() in s.callsign.strip():
            target = s
            break

    if target:
        st.success(f"Found flight {target.callsign.strip()}")

        lat, lon = target.latitude, target.longitude
        alt = target.baro_altitude

        st.write(f"Location: ({lat}, {lon}) at {alt} m")

        m = folium.Map(location=[lat, lon], zoom_start=6)
        folium.Marker([lat, lon], tooltip=f"{target.callsign.strip()} (Target)", icon=folium.Icon(color='red')).add_to(m)

        conflict_flights = []
        for s in states.states:
            if s != target and s.latitude and s.longitude:
                dist = geodesic((lat, lon), (s.latitude, s.longitude)).km
                alt_diff = abs((s.baro_altitude or 0) - (alt or 0))

                risk = None
                color = "green"

                if dist < 10 and alt_diff < 300:
                    risk = "⚠️ High"
                    color = "red"
                elif dist < 50 and alt_diff < 600:
                    risk = "⚠ Medium"
                    color = "orange"
                elif dist < 100 and alt_diff < 1000:
                    risk = "Low"
                    color = "yellow"

                if risk:
                    conflict_flights.append((s, dist, alt_diff, risk))
                    folium.Marker(
                        [s.latitude, s.longitude],
                        tooltip=f"{s.callsign.strip()} | {risk} | {dist:.1f}km | Alt Δ: {alt_diff:.0f}m",
                        icon=folium.Icon(color=color)
                    ).add_to(m)

        st_folium(m, width=700)

        st.subheader("🛑 Conflict Risk Summary")
        if conflict_flights:
            for c, d, a, r in conflict_flights:
                st.markdown(f"- `{c.callsign.strip()}` | **{r}** | Distance: {d:.1f} km | Altitude Diff: {a:.0f} m")
        else:
            st.success("No conflicts detected.")

    else:
        st.error("Flight not found.")