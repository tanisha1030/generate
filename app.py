import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="🚓 All India Police Stations (Capitals Only)", layout="wide")

st.title("🚓 Police Stations in State & UT Capitals (via OpenStreetMap)")
st.write("""
This script fetches **police stations** only for **state and union territory capitals** in India via **OpenStreetMap (Overpass API)**.  
No API key is needed. Data includes **name, address, phone, latitude, and longitude**.  
You can download the dataset as a JSON file.
""")

# ✅ State & UT capitals
CAPITALS = {
    "Andhra Pradesh": ["Amaravati"],
    "Arunachal Pradesh": ["Itanagar"],
    "Assam": ["Dispur"],
    "Bihar": ["Patna"],
    "Chhattisgarh": ["Raipur"],
    "Goa": ["Panaji"],
    "Gujarat": ["Gandhinagar"],
    "Haryana": ["Chandigarh"],
    "Himachal Pradesh": ["Shimla"],
    "Jharkhand": ["Ranchi"],
    "Karnataka": ["Bengaluru"],
    "Kerala": ["Thiruvananthapuram"],
    "Madhya Pradesh": ["Bhopal"],
    "Maharashtra": ["Mumbai"],
    "Manipur": ["Imphal"],
    "Meghalaya": ["Shillong"],
    "Mizoram": ["Aizawl"],
    "Nagaland": ["Kohima"],
    "Odisha": ["Bhubaneswar"],
    "Punjab": ["Chandigarh"],
    "Rajasthan": ["Jaipur"],
    "Sikkim": ["Gangtok"],
    "Tamil Nadu": ["Chennai"],
    "Telangana": ["Hyderabad"],
    "Tripura": ["Agartala"],
    "Uttar Pradesh": ["Lucknow"],
    "Uttarakhand": ["Dehradun"],
    "West Bengal": ["Kolkata"],
    # Union Territories
    "Andaman and Nicobar Islands": ["Port Blair"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman & Diu": ["Daman"],
    "Delhi": ["New Delhi"],
    "Jammu & Kashmir": ["Srinagar"],
    "Ladakh": ["Leh"],
    "Lakshadweep": ["Kavaratti"],
    "Puducherry": ["Puducherry"]
}

# Overpass fetcher
def fetch_police_stations(state, city):
    query = f"""
    [out:json][timeout:60];
    area["name"="{city}"]->.city;
    node(area.city)["amenity"="police"];
    out body;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        r = requests.post(url, data={"data": query})
        r.raise_for_status()
        data = r.json()
        stations = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            stations.append({
                "name": tags.get("name", "Unknown"),
                "address": tags.get("addr:full") or f"{city}, {state}",
                "phone": tags.get("phone") or tags.get("contact:phone", "N/A"),
                "lat": el.get("lat"),
                "lon": el.get("lon")
            })
        return stations
    except Exception as e:
        st.warning(f"⚠️ Skipped {city}: {e}")
        return []

if st.button("🚀 Fetch All Capitals"):
    all_data = {}
    total_cities = sum(len(clist) for clist in CAPITALS.values())
    current = 0

    progress = st.progress(0)
    status = st.empty()

    for state, clist in CAPITALS.items():
        all_data[state] = {}
        for city in clist:
            current += 1
            status.text(f"Fetching {city}, {state} ({current}/{total_cities}) ...")
            stations = fetch_police_stations(state, city)
            all_data[state][city] = stations
            progress.progress(current / total_cities)
            time.sleep(1.5)  # respect API limits

    st.success(f"✅ Completed fetching for {total_cities} capitals!")
    json_output = json.dumps(all_data, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download JSON of Capitals Police Stations",
        data=json_output,
        file_name="india_capitals_police_stations.json",
        mime="application/json"
    )

    st.json(all_data)
