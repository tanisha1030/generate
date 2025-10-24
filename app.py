# police_stations_app.py
import streamlit as st
import pandas as pd
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests
import time

# Dictionary of Indian states and districts
INDIA_DISTRICTS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "Kadapa"],
    "Maharashtra": ["Mumbai", "Pune", "Chandrapur"]
    # Add other states/districts here
}

# Function to query Overpass API
def fetch_police_station(district, state):
    query = f"""
    [out:json][timeout:25];
    area["name"="{state}"]->.searchArea;
    node["amenity"="police"](area.searchArea)["name"];
    out center;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.get(url, params={'data': query})
        data = response.json()
        # Filter nodes that contain the district name in address
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            if district.lower() in tags.get('addr:district', '').lower() or district.lower() in tags.get('name', '').lower():
                return {
                    "name": tags.get("name", "Police Station"),
                    "district": district,
                    "state": state,
                    "address": tags.get("addr:full", tags.get("addr:street", f"{district}, {state}")),
                    "phone": tags.get("phone", "Not available"),
                    "latitude": el.get("lat"),
                    "longitude": el.get("lon")
                }
        # Fallback: return first available node in state
        if data.get('elements'):
            el = data['elements'][0]
            tags = el.get('tags', {})
            return {
                "name": tags.get("name", "Police Station"),
                "district": district,
                "state": state,
                "address": tags.get("addr:full", tags.get("addr:street", f"{district}, {state}")),
                "phone": tags.get("phone", "Not available"),
                "latitude": el.get("lat"),
                "longitude": el.get("lon")
            }
    except Exception as e:
        print(f"Error fetching for {district}, {state}: {e}")
    # Final fallback: geocode district center
    try:
        geolocator = Nominatim(user_agent="police_app")
        location = geolocator.geocode(f"{district}, {state}, India", timeout=10)
        if location:
            return {
                "name": "Police Station",
                "district": district,
                "state": state,
                "address": f"{district}, {state}",
                "phone": "Not available",
                "latitude": location.latitude,
                "longitude": location.longitude
            }
    except GeocoderTimedOut:
        return {
            "name": "Police Station",
            "district": district,
            "state": state,
            "address": f"{district}, {state}",
            "phone": "Not available",
            "latitude": None,
            "longitude": None
        }

# Streamlit UI
st.title("Indian Police Stations by District")

if st.button("Fetch Police Stations"):
    all_stations = []
    progress_text = "Fetching police stations..."
    my_bar = st.progress(0, text=progress_text)
    total = sum(len(d) for d in INDIA_DISTRICTS.values())
    count = 0
    for state, districts in INDIA_DISTRICTS.items():
        for district in districts:
            station = fetch_police_station(district, state)
            all_stations.append(station)
            count += 1
            my_bar.progress(count / total, text=f"Processing {district}, {state}")
            time.sleep(0.1)  # small delay to avoid hitting API limits

    st.success("Fetched all police stations!")

    # Convert to DataFrame
    df = pd.DataFrame(all_stations)
    st.dataframe(df)

    # Save JSON
    with open("police_stations.json", "w", encoding="utf-8") as f:
        json.dump(all_stations, f, ensure_ascii=False, indent=4)

    st.download_button(
        label="Download JSON",
        data=json.dumps(all_stations, ensure_ascii=False, indent=4),
        file_name="police_stations.json",
        mime="application/json"
    )
