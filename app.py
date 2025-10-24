
import streamlit as st
import pandas as pd
import requests
import json
import time
import io

st.set_page_config(page_title="🚓 All-India Police Station JSON Generator", layout="wide")
st.title("🚓 Police Stations in All Indian Districts (via OpenStreetMap)")

st.markdown("This app fetches police stations for **every Indian district** using the **Overpass API** (OpenStreetMap). No API key needed.")

@st.cache_data
def load_districts():
    return pd.read_csv("india_districts.csv")

def query_overpass(state, district):
    query = f"""
    [out:json][timeout:90];
    area["name"="{district}"]["boundary"="administrative"];
    (
      node["amenity"="police"](area);
      way["amenity"="police"](area);
      relation["amenity"="police"](area);
    );
    out center tags;
    """
    try:
        resp = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=120)
        resp.raise_for_status()
        return resp.json().get("elements", [])
    except Exception as e:
        st.warning(f"Error fetching {district}: {e}")
        return []

districts_df = load_districts()
if st.button("🚀 Fetch All India Police Stations"):
    result = {}
    progress = st.progress(0.0)
    for i, row in enumerate(districts_df.itertuples(), 1):
        elems = query_overpass(row.State, row.District)
        stations = []
        for e in elems:
            tags = e.get("tags", {})
            name = tags.get("name", "Police Station")
            phone = tags.get("phone", tags.get("contact:phone", ""))
            addr = ", ".join([tags.get(k, "") for k in ["addr:street", "addr:city", "addr:state"] if tags.get(k)])
            lat, lon = (e.get("lat"), e.get("lon")) if "lat" in e else (e.get("center", {}).get("lat"), e.get("center", {}).get("lon"))
            stations.append({"name": name, "address": addr, "phone": phone, "lat": lat, "lon": lon})
        result.setdefault(row.State, {})[row.District] = stations
        progress.progress(i / len(districts_df))
        time.sleep(1)
    json_bytes = io.BytesIO(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    st.download_button("⬇️ Download All-India police_stations.json", data=json_bytes, file_name="police_stations.json", mime="application/json")
