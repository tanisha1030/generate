import streamlit as st
import requests
import json
import pandas as pd
import concurrent.futures
import time

st.set_page_config(page_title="🚓 Fast Police Station Fetcher", layout="wide")
st.title("⚡ Fast Police Station Finder (Per Indian District)")
st.caption("Fetches at least one accurate police station per district using concurrent Overpass API calls.")

# --------------------------- STATE & DISTRICT DATA -----------------------------
INDIA_REGIONS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore",
                       "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "Kadapa"],
    "Arunachal Pradesh": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Kurung Kumey", "Kra Daadi",
                          "Lower Subansiri", "Upper Subansiri", "West Siang", "East Siang", "Siang",
                          "Upper Siang", "Lower Siang", "Lower Dibang Valley", "Dibang Valley", "Anjaw",
                          "Lohit", "Namsai", "Changlang", "Tirap", "Longding"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang",
              "Dhemaji", "Dhubri", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat",
              "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur",
              "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar",
              "Tinsukia", "Udalguri", "West Karbi Anglong"],
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# --------------------------- FAST FETCH FUNCTION -------------------------------
def get_police_station(state, district):
    """
    Fetches one police station from OpenStreetMap for a district (fast version).
    """
    query = f"""
    [out:json][timeout:25];
    area["name"="{district}"]["boundary"="administrative"]["is_in:state"="{state}"]->.searchArea;
    (
      node["amenity"="police"](area.searchArea);
    );
    out center 1;
    """
    try:
        response = requests.post(OVERPASS_URL, data=query, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("elements"):
                el = data["elements"][0]
                return {
                    "State": state,
                    "District": district,
                    "Name": el.get("tags", {}).get("name", "Unnamed Police Station"),
                    "Latitude": el.get("lat"),
                    "Longitude": el.get("lon"),
                }
    except Exception:
        pass

    # Fallback (if not found)
    return {"State": state, "District": district, "Name": "Not Found", "Latitude": None, "Longitude": None}


# --------------------------- STREAMLIT APP -------------------------------------
if st.button("🚀 Fetch Police Stations (Fast Mode)"):
    start_time = time.time()
    st.info("Fetching police stations concurrently... Please wait ⏳")

    # Create task list
    tasks = [(state, district) for state, districts in INDIA_REGIONS.items() for district in districts]
    total = len(tasks)
    results = []
    progress = st.progress(0)

    # Run with ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(get_police_station, s, d): (s, d) for s, d in tasks}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            results.append(res)
            progress.progress((i + 1) / total)

    # Save outputs
    df = pd.DataFrame(results)
    df.to_csv("police_stations_fast.csv", index=False, encoding="utf-8")
    with open("police_stations_fast.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    st.success(f"✅ Completed in {elapsed:.1f} seconds for {total} districts!")
    st.dataframe(df.head(20))

    # Download buttons
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'),
                       "police_stations_fast.csv", "text/csv")
    st.download_button("📥 Download JSON", json.dumps(results, indent=2).encode('utf-8'),
                       "police_stations_fast.json", "application/json")
