import streamlit as st
import requests
import json
import time

# ✅ Preloaded state & district list (shortened for demo — can expand)
INDIA_DISTRICTS = {
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad"],
    "Karnataka": ["Bengaluru Urban", "Mysuru", "Hubballi", "Mangaluru"],
    "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Varanasi", "Agra", "Meerut", "Prayagraj"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "Rajasthan": ["Jaipur", "Udaipur", "Jodhpur", "Ajmer"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
}

st.set_page_config(page_title="🚓 Police Stations of India", layout="wide")

st.title("🚓 Police Stations in All Indian Districts (via OpenStreetMap)")
st.write("""
This app queries **OpenStreetMap (Overpass API)** to fetch police stations in each Indian district.
No API key required! You can download results as a **JSON file**.
""")

# Select state and districts
state = st.selectbox("Select State", list(INDIA_DISTRICTS.keys()))
districts = INDIA_DISTRICTS[state]

selected_districts = st.multiselect("Select Districts", districts, default=districts[:1])

def fetch_police_stations(state, district):
    """Fetch police stations for a given district using Overpass API"""
    query = f"""
    [out:json][timeout:60];
    area["name"="{district}"]->.district;
    node(area.district)["amenity"="police"];
    out body;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        res = requests.post(url, data={'data': query})
        res.raise_for_status()
        data = res.json()

        stations = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            stations.append({
                "name": tags.get("name", "Unknown"),
                "address": tags.get("addr:full") or f"{district}, {state}",
                "phone": tags.get("phone") or tags.get("contact:phone", "N/A"),
                "lat": el.get("lat"),
                "lon": el.get("lon"),
            })
        return stations
    except Exception as e:
        st.error(f"Failed to fetch for {district}: {e}")
        return []

if st.button("Fetch Police Stations"):
    all_data = {}

    progress = st.progress(0)
    total = len(selected_districts)

    for i, district in enumerate(selected_districts, start=1):
        st.write(f"🔍 Fetching police stations for **{district}, {state}**...")
        stations = fetch_police_stations(state, district)
        all_data[district] = stations
        time.sleep(1)  # avoid rate limit
        progress.progress(i / total)

    # Display and download
    st.success(f"✅ Data fetched for {len(selected_districts)} districts.")
    st.json(all_data)

    json_data = json.dumps(all_data, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download JSON",
        data=json_data,
        file_name=f"{state.lower().replace(' ', '_')}_police_stations.json",
        mime="application/json"
    )

st.caption("Built using OpenStreetMap + Streamlit | No API key required 🌍")
