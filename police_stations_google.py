import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="Police Station JSON Generator (Google Maps)", layout="wide")
st.title("🚓 Police Station JSON Generator (Google Maps API)")

st.markdown("""
This app generates **district-wise police station data in India** using Google Maps Places API.  
You can download the results as a JSON file.
""")

# --- Input API Key ---
api_key = st.text_input("Enter your Google Maps API Key:", type="password")

# --- Optional: predefined district centers ---
# For demonstration, we'll use a few districts with coordinates
DISTRICTS = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707}
}

# --- Helper function to query Google Places ---
def get_police_stations(lat, lon, radius=20000, api_key=None):
    stations = []
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "police",
        "key": api_key
    }
    while True:
        res = requests.get(url, params=params)
        if res.status_code != 200:
            st.error(f"Error: {res.status_code}")
            break
        data = res.json()
        for place in data.get("results", []):
            stations.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "lat": place["geometry"]["location"]["lat"],
                "lon": place["geometry"]["location"]["lng"],
                "place_id": place.get("place_id")
            })
        # Check if there is a next page
        if "next_page_token" in data:
            next_token = data["next_page_token"]
            time.sleep(2)  # required delay for next_page_token
            params["pagetoken"] = next_token
        else:
            break
    return stations

# --- Main button ---
if st.button("🔍 Generate Police Stations JSON"):
    if not api_key:
        st.warning("Please enter your Google Maps API key!")
    else:
        results = {}
        progress = st.progress(0)
        total = len(DISTRICTS)

        for i, (district, coords) in enumerate(DISTRICTS.items(), 1):
            lat, lon = coords["lat"], coords["lon"]
            st.info(f"Fetching police stations for {district}...")
            try:
                stations = get_police_stations(lat, lon, api_key=api_key)
                results[district.lower()] = stations
            except Exception as e:
                st.error(f"Error fetching {district}: {e}")
                results[district.lower()] = []
            progress.progress(i / total)
            time.sleep(1)  # polite delay

        st.success(f"✅ Completed! Fetched data for {len(results)} districts.")

        # Download JSON
        json_bytes = io.BytesIO(json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8"))
        st.download_button(
            "⬇️ Download police_stations.json",
            data=json_bytes,
            file_name="police_stations.json",
            mime="application/json"
        )

        # Preview first district
        first_district = list(results.keys())[0]
        st.json({first_district: results[first_district][:5]})  # preview first 5 stations
