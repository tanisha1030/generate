import streamlit as st
import requests
import pandas as pd

# Example dictionary (extend to all states/districts)
INDIA_REGIONS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "Kadapa"],
    "Maharashtra": ["Mumbai", "Pune", "Chandrapur", "Nagpur"]
}

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

@st.cache_data
def fetch_police_stations_batch(state, districts):
    """
    Fetch at least one police station per district in a single Overpass query per state.
    Latitude and longitude are excluded.
    """
    query = f"""
    [out:json][timeout:60];
    area["name"="{state}"]["boundary"="administrative"]->.searchArea;
    (
      node["amenity"="police"](area.searchArea);
      way["amenity"="police"](area.searchArea);
      relation["amenity"="police"](area.searchArea);
    );
    out center;
    """
    try:
        response = requests.post(OVERPASS_URL, data={'data': query}, timeout=60)
        data = response.json().get("elements", [])
        results = []

        for district in districts:
            found = None
            for el in data:
                tags = el.get("tags", {})
                addr = tags.get("addr:city") or tags.get("addr:suburb") or ""
                if district.lower() in addr.lower():
                    found = {
                        "name": tags.get("name", "Police Station"),
                        "district": district,
                        "state": state,
                        "address": tags.get("addr:full") or f"{district}, {state}",
                        "phone": tags.get("phone", "Not available")
                    }
                    break
            if not found:
                found = {
                    "name": "Police Station",
                    "district": district,
                    "state": state,
                    "address": f"{district}, {state}",
                    "phone": "Not available"
                }
            results.append(found)
        return results

    except Exception:
        return [{
            "name": "Police Station",
            "district": d,
            "state": state,
            "address": f"{d}, {state}",
            "phone": "Not available"
        } for d in districts]

# Streamlit UI
st.title("Indian Police Stations by District (Faster Version, No Lat/Long)")

all_data = []
progress = st.progress(0)
total_states = len(INDIA_REGIONS)
state_count = 0

for state, districts in INDIA_REGIONS.items():
    st.write(f"Fetching {state}...")
    state_data = fetch_police_stations_batch(state, districts)
    all_data.extend(state_data)
    state_count += 1
    progress.progress(state_count / total_states)

df = pd.DataFrame(all_data)
st.dataframe(df)

st.download_button(
    "Download JSON", 
    df.to_json(orient="records", indent=2), 
    file_name="police_stations.json"
)
