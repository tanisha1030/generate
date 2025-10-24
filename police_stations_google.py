import streamlit as st
import requests
import json
import pandas as pd
import time
import io

st.set_page_config(page_title="🚓 India Police Station JSON Generator (OSM)", layout="wide")
st.title("🚓 Police Stations in All Indian Districts (via OpenStreetMap)")
st.markdown("""
This app queries **OpenStreetMap (Overpass API)** to fetch police stations in every Indian district.  
No API key is needed. The data includes **name, address, phone, and GPS coordinates**,  
and you can download it as a JSON file.
""")

# -----------------------------
# Load district coordinates
# -----------------------------
@st.cache_data
def load_district_coordinates():
    try:
        # Example public dataset with Indian district centroids
        url = "https://raw.githubusercontent.com/datameet/india-maps/master/geojson/districts/districts.csv"
        df = pd.read_csv(url)
        # Ensure standard column names
        if 'DISTRICT' in df.columns and 'CEN_LAT' in df.columns and 'CEN_LON' in df.columns:
            df = df.rename(columns={'DISTRICT': 'District', 'CEN_LAT': 'Latitude', 'CEN_LON': 'Longitude'})
        else:
            raise Exception("CSV missing expected columns")
        return df[['District', 'Latitude', 'Longitude']]
    except Exception as e:
        st.error(f"⚠️ Failed to load district list: {e}")
        return pd.DataFrame(columns=["District", "Latitude", "Longitude"])

districts_df = load_district_coordinates()

if districts_df.empty:
    st.stop()

# -----------------------------
# Query OpenStreetMap
# -----------------------------
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
            addr_parts = [tags.get(k, "") for k in [
                "addr:housenumber", "addr:street", "addr:suburb", "addr:city",
                "addr:district", "addr:state", "addr:postcode"
            ] if tags.get(k)]
            if not addr_parts:
                for fallback in ["vicinity", "description"]:
                    if tags.get(fallback):
                        addr_parts.append(tags[fallback])
            address = ", ".join(addr_parts)
            phone = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or ""
            lat_s, lon_s = elem.get("lat"), elem.get("lon")
            if not lat_s and "center" in elem:
                lat_s, lon_s = elem["center"]["lat"], elem["center"]["lon"]
            stations.append({
                "name": name,
                "address": address,
                "phone": phone,
                "lat": lat_s,
                "lon": lon_s
            })
        return stations
    except Exception as e:
        st.warning(f"Overpass error near ({lat}, {lon}): {e}")
        return []

# -----------------------------
# Main button
# -----------------------------
if st.button("🔍 Generate All India Police Stations JSON"):
    results = {}
    progress = st.progress(0)
    total = len(districts_df)

    for i, row in districts_df.iterrows():
        district = row['District']
        lat, lon = row['Latitude'], row['Longitude']
        st.write(f"Fetching stations for **{district}** ({lat:.2f}, {lon:.2f}) ...")
        stations = get_police_stations(lat, lon)
        results[district] = stations
        progress.progress((i + 1) / total)
        time.sleep(1.0)  # polite delay for Overpass API

    st.success(f"✅ Completed! {len(results)} districts processed successfully.")

    json_data = json.dumps(results, ensure_ascii=False, indent=2)
    st.download_button(
        "⬇️ Download police_stations_india.json",
        data=json_data.encode("utf-8"),
        file_name="police_stations_india.json",
        mime="application/json"
    )

    st.json({k: results[k][:3] for k in list(results.keys())[:2]})
else:
    st.info("Press the button above to start generating police station data.")
