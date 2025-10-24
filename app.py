import streamlit as st
import requests
import json
from time import sleep

# Dictionary of states and districts (abbreviated example; replace with full)
INDIA_REGIONS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna"],
    "Maharashtra": ["Mumbai", "Pune", "Chandrapur"],
    # Add all other states/districts here...
}

# Function to fetch one police station per district
def fetch_one_police_station(state: str, district: str):
    query = f"""
    [out:json][timeout:20];
    area["name"="{district}"]["boundary"="administrative"]->.a;
    (
      node["amenity"="police"](area.a);
      way["amenity"="police"](area.a);
      relation["amenity"="police"](area.a);
    );
    out center 1;
    """
    try:
        r = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=20)
        r.raise_for_status()
        data = r.json()
        elems = data.get("elements", [])
        if not elems:
            return {
                "name": "Police Station",
                "district": district,
                "state": state,
                "address": f"{district}, {state}",
                "phone": "Not available",
                "latitude": None,
                "longitude": None
            }
        el = elems[0]
        tags = el.get("tags", {})

        # Name
        name = tags.get("name") or "Unnamed Police Station"

        # Phone
        phone = (
            tags.get("phone") or 
            tags.get("contact:phone") or
            tags.get("contact:mobile") or
            tags.get("contact:fax") or
            "Not available"
        )

        # Address
        addr_parts = []
        for key in ["addr:housename", "addr:housenumber", "addr:street", "addr:place",
                    "addr:city", "addr:suburb", "addr:district", "addr:state", "addr:postcode"]:
            if tags.get(key):
                addr_parts.append(tags[key])
        address = ", ".join(addr_parts)
        if not address:
            address = f"{district}, {state}"  # fallback

        # Coordinates
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")

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
        return {
            "name": "Police Station",
            "district": district,
            "state": state,
            "address": f"{district}, {state}",
            "phone": "Not available",
            "latitude": None,
            "longitude": None
        }

# Streamlit UI
st.title("Indian Police Stations by District")
st.write("This app fetches at least one police station per district from OpenStreetMap.")

if st.button("Fetch Police Stations"):
    all_data = []
    progress_text = "Fetching police stations..."
    my_bar = st.progress(0, text=progress_text)
    total_districts = sum(len(d) for d in INDIA_REGIONS.values())
    count = 0

    for state, districts in INDIA_REGIONS.items():
        for district in districts:
            station = fetch_one_police_station(state, district)
            all_data.append(station)
            count += 1
            my_bar.progress(count/total_districts)
            sleep(0.5)  # avoid overloading Overpass API

    st.success(f"Fetched police stations for {count} districts!")
    st.dataframe(all_data)

    # JSON download
    json_data = json.dumps(all_data, indent=2)
    st.download_button("Download JSON", data=json_data, file_name="police_stations.json")
