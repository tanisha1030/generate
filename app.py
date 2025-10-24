# app_fast_one_per_district.py
import streamlit as st
import requests
import pandas as pd
import json
from pathlib import Path
import time

st.set_page_config(page_title="🚔 India Police Stations — Fast One-per-District", layout="wide")

st.title("🚔 Fast Police Station Fetch — One per District")
st.markdown(
    "This app fetches **one representative police station per district** in India using OSM/Overpass API. "
    "Faster and lighter than accurate mode."
)

# ------------------------
# 1) State -> districts dictionary
# ------------------------
INDIA_DISTRICTS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "Kadapa"],
    "Karnataka": ["Bagalkot", "Bangalore Urban", "Bangalore Rural", "Belagavi", "Bellary", "Bidar", "Chamarajanagar", "Chikkaballapura", "Chikkamagaluru", "Chitradurga"],
    "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli"],
    # ... add all other states/districts as needed
}

# ------------------------
# 2) Settings
# ------------------------
timeout_sec = st.sidebar.slider("HTTP timeout (s)", 10, 60, 20)
pause_between_requests = st.sidebar.slider("Pause between requests (s)", 0.0, 2.0, 0.1, step=0.1)

output_json = Path("police_stations_one_per_district.json")
output_csv = Path("police_stations_one_per_district.csv")

# ------------------------
# 3) Overpass query
# ------------------------
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def fetch_one_police_station(state: str, district: str):
    query = f"""
    [out:json][timeout:{timeout_sec}];
    area["name"="{district}"]["boundary"="administrative"]->.a;
    (
      node["amenity"="police"](area.a);
      way["amenity"="police"](area.a);
      relation["amenity"="police"](area.a);
    );
    out center 1;
    """
    try:
        r = requests.post(OVERPASS_URL, data={"data": query}, timeout=timeout_sec)
        r.raise_for_status()
        data = r.json()
        elems = data.get("elements", [])
        if not elems:
            return None
        el = elems[0]
        tags = el.get("tags", {})
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        name = tags.get("name") or "Unnamed Police Station"
        phone = tags.get("phone") or tags.get("contact:phone") or "Not available"
        address_parts = []
        for k in ["addr:street", "addr:housename", "addr:housenumber", "addr:place", "addr:city", "addr:district", "addr:state"]:
            if tags.get(k):
                address_parts.append(tags[k])
        address = ", ".join(address_parts) if address_parts else "Not available"
        return {
            "name": name,
            "district": district,
            "state": state,
            "address": address,
            "phone": phone,
            "latitude": round(lat,6) if lat else None,
            "longitude": round(lon,6) if lon else None
        }
    except Exception:
        return None

# ------------------------
# 4) Main UI
# ------------------------
st.header("Run controls")
run_button = st.button("🚀 Fetch One Police Station Per District")

if run_button:
    st.info("Fetching one police station per district...")
    results = []
    total_districts = sum(len(lst) for lst in INDIA_DISTRICTS.values())
    completed = 0
    progress_bar = st.progress(0)
    status = st.empty()
    
    for state, districts in INDIA_DISTRICTS.items():
        for district in districts:
            info = fetch_one_police_station(state, district)
            if info:
                results.append(info)
            completed += 1
            progress_bar.progress(completed / total_districts)
            status.text(f"Processed {completed}/{total_districts}: {district}, {state}")
            time.sleep(pause_between_requests)
    
    # Save results
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    
    st.success(f"Fetched {len(results)} police stations. Saved to JSON & CSV.")
    st.dataframe(df.head(50))
    st.map(df.dropna(subset=["latitude","longitude"]))
    
    st.download_button("📥 Download JSON", output_json.read_text(encoding="utf-8"), file_name=output_json.name)
    st.download_button("📥 Download CSV", output_csv.read_bytes(), file_name=output_csv.name)
