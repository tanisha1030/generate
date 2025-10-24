import streamlit as st
import requests
import pandas as pd

# Dictionary of states and districts (partial example; extend to all districts)
INDIA_REGIONS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "Kadapa"],
    "Maharashtra": ["Mumbai", "Pune", "Chandrapur", "Nagpur"]
}

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

@st.cache_data
def fetch_police_station(state, district):
    """
    Fetch at least one police station from OpenStreetMap using Overpass API.
    Returns a dict with name, district, state, address, phone, lat, lon.
    """
    query = f"""
    [out:json][timeout:25];
    area["name"="{state}"]["boundary"="administrative"]->.searchArea;
    (
      node["amenity"="police"](area.searchArea)["name"](if: t["addr:city"] == "{district}" || t["addr:suburb"] == "{district}");
      way["amenity"="police"](area.searchArea)["name"](if: t["addr:city"] == "{district}" || t["addr:suburb"] == "{district}");
      relation["amenity"="police"](area.searchArea)["name"](if: t["addr:city"] == "{district}" || t["addr:suburb"] == "{district}");
    );
    out center 1;
    """
    try:
        response = requests.post(OVERPASS_URL, data={'data': query}, timeout=25)
        data = response.json()
        elements = data.get("elements", [])
        if elements:
            el = elements[0]  # Take first result
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            tags = el.get("tags", {})
            return {
                "name": tags.get("name", "Police Station"),
                "district": district,
                "state": state,
                "address": tags.get("addr:full") or f"{district}, {state}",
                "phone": tags.get("phone", "Not available"),
                "latitude": lat,
                "longitude": lon
            }
        else:
            # If no result, return placeholder
            return {
                "name": "Police Station",
                "district": district,
                "state": state,
                "address": f"{district}, {state}",
                "phone": "Not available",
                "latitude": None,
                "longitude": None
            }
    except Exception as e:
        return {
            "name": "Police Station",
            "district": district,
            "state": state,
            "address": f"{district}, {state}",
            "phone": "Not available",
            "latitude": None,
            "longitude": None
        }

st.title("Indian Police Stations by District")

all_data = []
for state, districts in INDIA_REGIONS.items():
    for district in districts:
        st.write(f"Fetching for {district}, {state}...")
        ps_data = fetch_police_station(state, district)
        all_data.append(ps_data)

# Convert to DataFrame and show
df = pd.DataFrame(all_data)
st.dataframe(df)

# Download as JSON
st.download_button("Download JSON", df.to_json(orient="records", indent=2), file_name="police_stations.json")
