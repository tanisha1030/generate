import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="Police Station JSON Generator (OSM)", layout="wide")
st.title("🚓 District-wise Police Stations (OpenStreetMap)")

st.markdown("""
This app automatically fetches **police stations for major districts in India** using OpenStreetMap (Overpass API).  
No API key or file upload is required. You can download the results as a JSON file.
""")

# --- Example districts with lat/lon bounding boxes (approx center) ---
# For a full list, you can extend this dict
DISTRICTS = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707}
}

# --- Helper function to query OSM Overpass API ---
def get_police_stations(lat, lon, radius=20000):
    """
    Query OSM Overpass API to get police stations near (lat, lon) within radius (meters)
    """
    query = f"""
    [out:json][timeout:60];
    (
      node["amenity"="police"](around:{radius},{lat},{lon});
      way["amenity"="police"](around:{radius},{lat},{lon});
      relation["amenity"="police"](around:{radius},{lat},{lon});
    );
    out center tags;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        res = requests.post(url, data={"data": query}, timeout=120)
        res.raise_for_status()
        data = res.json()
        stations = []
        for elem in data.get("elements", []):
            tags = elem.get("tags", {})
            name = tags.get("name") or "Police Station"
            address_parts = []
            for k in ["addr:street", "addr:suburb", "addr:city", "addr:state"]:
                if k in tags and tags[k]:
                    address_parts.append(tags[k])
            address = ", ".join(address_parts)
            lat_station, lon_station = None, None
            if "lat" in elem:
                lat_station, lon_station = elem["lat"], elem["lon"]
            elif "center" in elem:
                lat_station, lon_station = elem["center"]["lat"], elem["center"]["lon"]
            stations.append({
                "name": name,
                "address": address,
                "lat": lat_station,
                "lon": lon_station
            })
        return stations
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# --- Main button ---
if st.button("🔍 Generate Police Stations JSON"):
    results = {}
    progress = st.progress(0)
    total = len(DISTRICTS)

    for i, (district, coords) in enumerate(DISTRICTS.items(), 1):
        st.info(f"Fetching police stations for {district}...")
        stations = get_police_stations(coords["lat"], coords["lon"])
        results[district.lower()] = stations
        progress.progress(i / total)
        time.sleep(1)  # polite delay

    st.success(f"✅ Completed! Fetched data for {len(results)} districts.")

    # Download JSON
    json_bytes = json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        "⬇️ Download police_stations.json",
        data=json_bytes,
        file_name="police_stations.json",
        mime="application/json"
    )

    # Preview first district
    first_district = list(results.keys())[0]
    st.json({first_district: results[first_district][:5]})  # first 5 stations
