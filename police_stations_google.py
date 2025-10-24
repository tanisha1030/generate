import streamlit as st
import requests
import json
import pandas as pd
import time

# Load district coordinates
@st.cache
def load_district_coordinates():
    url = "https://raw.githubusercontent.com/yourusername/yourrepository/main/district_coordinates.csv"
    return pd.read_csv(url)

districts_df = load_district_coordinates()

st.set_page_config(page_title="Police Station JSON Generator (OSM)", layout="wide")
st.title("🚓 District-wise Police Stations (OpenStreetMap)")

st.markdown("""
This app fetches **police stations for all districts in India** using OpenStreetMap (Overpass API).  
No API key or file upload is required. You can download the results as a JSON file.
""")

def get_police_stations(lat, lon, radius=20000):
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
            name = tags.get("name") or tags.get("official_name") or "Police Station"
            address_parts = []
            for k in ["addr:street", "addr:housenumber", "addr:suburb", "addr:city", "addr:state", "addr:postcode"]:
                if tags.get(k):
                    address_parts.append(tags[k])
            if not address_parts:
                for fallback in ["vicinity", "description"]:
                    if tags.get(fallback):
                        address_parts.append(tags[fallback])
            address = ", ".join(address_parts)
            phone = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or ""
            lat_station, lon_station = None, None
            if "lat" in elem:
                lat_station, lon_station = elem["lat"], elem["lon"]
            elif "center" in elem:
                lat_station, lon_station = elem["center"]["lat"], elem["center"]["lon"]
            stations.append({
                "name": name,
                "address": address,
                "phone": phone,
                "lat": lat_station,
                "lon": lon_station
            })
        return stations
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

if st.button("🔍 Generate Police Stations JSON"):
    results = {}
    progress = st.progress(0)
    total = len(districts_df)

    for i, row in districts_df.iterrows():
        district = row['District']
        lat, lon = row['Latitude'], row['Longitude']
        st.info(f"Fetching police stations for {district}...")
        stations = get_police_stations(lat, lon)
        results[district] = stations
        progress.progress((i + 1) / total)
        time.sleep(1)

    st.success(f"✅ Completed! Fetched data for {len(results)} districts.")

    json_bytes = json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        "⬇️ Download police_stations.json",
        data=json_bytes,
        file_name="police_stations.json",
        mime="application/json"
    )

    first_district = list(results.keys())[0]
    st.json({first_district: results[first_district][:5]})
