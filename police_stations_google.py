import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="🚓 All India Police Stations (OpenStreetMap)", layout="wide")

st.title("🚓 Police Stations in All Indian Districts (via OpenStreetMap)")
st.write("""
This script automatically queries **OpenStreetMap (Overpass API)** to fetch police stations for **all districts in India**.  
No API key is needed. Data includes **name, address, phone, latitude, and longitude**.  
You can download the complete dataset as a JSON file.
""")

# ✅ Full state + district mapping (short list here; you can expand)
INDIA_DISTRICTS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
    "Arunachal Pradesh": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Kurung Kumey", "Kra Daadi", "Lower Subansiri", "Upper Subansiri", "West Siang", "East Siang", "Upper Siang", "Lower Dibang Valley", "Dibang Valley", "Anjaw", "Lohit", "Namsai", "Changlang", "Tirap", "Longding"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara", "Tinsukia", "Udalguri", "West Karbi Anglong"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Purnia", "Darbhanga", "Bhojpur", "Nalanda", "Rohtas", "Begusarai", "Katihar", "Munger", "Aurangabad", "Vaishali", "Sitamarhi", "Samastipur", "Siwan", "Saran"],
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Kolhapur", "Solapur", "Amravati", "Latur", "Sangli", "Wardha"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tirunelveli", "Erode", "Vellore", "Thoothukudi"],
    "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Agra", "Varanasi", "Meerut", "Prayagraj", "Gorakhpur", "Noida", "Ghaziabad", "Bareilly", "Jhansi"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Jalpaiguri", "Siliguri", "Murshidabad", "Nadia", "Hooghly", "Purulia", "Bankura"],
}

# Overpass fetcher
def fetch_police_stations(state, district):
    query = f"""
    [out:json][timeout:60];
    area["name"="{district}"]->.district;
    node(area.district)["amenity"="police"];
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
                "address": tags.get("addr:full") or f"{district}, {state}",
                "phone": tags.get("phone") or tags.get("contact:phone", "N/A"),
                "lat": el.get("lat"),
                "lon": el.get("lon")
            })
        return stations
    except Exception as e:
        st.warning(f"⚠️ Skipped {district}: {e}")
        return []

if st.button("🚀 Start Fetching All Districts"):
    all_data = {}
    total_districts = sum(len(dlist) for dlist in INDIA_DISTRICTS.values())
    current = 0

    progress = st.progress(0)
    status = st.empty()

    for state, dlist in INDIA_DISTRICTS.items():
        all_data[state] = {}
        for district in dlist:
            current += 1
            status.text(f"Fetching {district}, {state} ({current}/{total_districts}) ...")
            stations = fetch_police_stations(state, district)
            all_data[state][district] = stations
            progress.progress(current / total_districts)
            time.sleep(1.5)  # respect API limits

    st.success(f"✅ Completed fetching for {total_districts} districts!")
    json_output = json.dumps(all_data, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download All India Police Stations JSON",
        data=json_output,
        file_name="india_police_stations.json",
        mime="application/json"
    )
    st.json(all_data)
