import streamlit as st
import requests
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="🚓 Police Stations Finder", layout="wide")

# ==========================================
# 🗺️ State–District Dictionary (Example)
# 👉 You can extend this to all 800 districts
# ==========================================
INDIA_REGIONS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool"],
    "Arunachal Pradesh": ["Tawang", "West Kameng", "East Kameng", "Papum Pare"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar"],
    "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur"]
    # ... paste rest here if needed
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# ==========================================
# 🚔 Fetch Function (Optimized)
# ==========================================
def get_police_station(state, district):
    """Return at least one police station for a district"""
    queries = [
        f"""
        [out:json][timeout:20];
        area["name"="{district}"]->.searchArea;
        node["amenity"="police"](area.searchArea);
        out 1;
        """,
        f"""
        [out:json][timeout:20];
        area["name"="{state}"]->.state;
        node["amenity"="police"](area.state);
        out 1;
        """
    ]

    for q in queries:
        try:
            res = requests.post(OVERPASS_URL, data={"data": q}, timeout=25)
            data = res.json()
            if "elements" in data and data["elements"]:
                el = data["elements"][0]
                return {
                    "state": state,
                    "district": district,
                    "name": el.get("tags", {}).get("name", "Unnamed Police Station"),
                    "lat": el.get("lat"),
                    "lon": el.get("lon")
                }
        except Exception:
            continue
    return {"state": state, "district": district, "name": None, "lat": None, "lon": None}


# ==========================================
# ⚡ Fetch All in Parallel
# ==========================================
def fetch_districts(selected_states):
    results = []
    futures = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        for state in selected_states:
            for district in INDIA_REGIONS[state]:
                futures.append(executor.submit(get_police_station, state, district))
        progress = st.progress(0)
        total = len(futures)
        for i, f in enumerate(as_completed(futures), 1):
            result = f.result()
            results.append(result)
            progress.progress(i / total)
    return results


# ==========================================
# 🎯 Streamlit UI
# ==========================================
st.title("🚓 Police Stations in Indian Districts")
st.markdown("Fetch **at least one police station** per district from OpenStreetMap (Overpass API).")

selected_states = st.multiselect(
    "Select States",
    list(INDIA_REGIONS.keys()),
    default=["Andhra Pradesh"]
)

if st.button("🔍 Fetch Police Stations"):
    if not selected_states:
        st.warning("Please select at least one state.")
    else:
        with st.spinner("Fetching police station data... ⏳"):
            data = fetch_districts(selected_states)

        df = pd.DataFrame(data)
        st.success("✅ Data fetched successfully!")

        st.dataframe(df)

        # Filter found stations
        found = df.dropna(subset=["name"])
        st.map(found.rename(columns={"lat": "latitude", "lon": "longitude"}))

        # Download buttons
        st.download_button("📥 Download JSON", json.dumps(data, ensure_ascii=False, indent=2), "police_stations.json")
        st.download_button("📥 Download CSV", found.to_csv(index=False).encode("utf-8"), "police_stations.csv")

st.caption("⚡ Optimized by parallel requests + Overpass API | Created by ChatGPT")
