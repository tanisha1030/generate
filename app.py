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
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam"],
    "Arunachal Pradesh": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Kurung Kumey", "Kra Daadi", "Lower Subansiri", "Upper Subansiri", "West Siang", "East Siang"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Purnia", "Darbhanga", "Bhojpur", "Nalanda", "Rohtas", "Begusarai"],
    "Chhattisgarh": ["Raipur", "Bilaspur", "Durg", "Korba", "Rajnandgaon", "Raigarh", "Bastar", "Kanker", "Dhamtari", "Jagdalpur"],
    "Goa": ["North Goa", "South Goa"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Bharuch"],
    "Haryana": ["Ambala", "Bhiwani", "Faridabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra"],
    "Himachal Pradesh": ["Shimla", "Mandi", "Kullu", "Solan", "Kangra", "Una", "Chamba", "Bilaspur", "Sirmaur", "Hamirpur"],
    "Jharkhand": ["Ranchi", "Dhanbad", "Jamshedpur", "Bokaro", "Deoghar", "Dumka", "Giridih", "Hazaribagh", "Jamtara", "Chatra"],
    "Karnataka": ["Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Mangaluru", "Dharwad", "Belagavi", "Hubballi", "Kalaburagi", "Ballari", "Davangere"],
    "Kerala": ["Thiruvananthapuram", "Kollam", "Alappuzha", "Kottayam", "Ernakulam", "Thrissur", "Palakkad", "Malappuram", "Kozhikode", "Kannur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain", "Dewas", "Satna", "Rewa", "Sagar", "Shahdol"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Kolhapur", "Solapur", "Amravati", "Latur"],
    "Manipur": ["Imphal East", "Imphal West", "Bishnupur", "Thoubal", "Kakching", "Churachandpur", "Chandel", "Senapati", "Tamenglong", "Ukhrul"],
    "Meghalaya": ["East Khasi Hills", "West Khasi Hills", "Ribhoi", "Jaintia Hills", "West Jaintia Hills", "South Garo Hills", "East Garo Hills", "North Garo Hills", "Ri Bhoi", "South West Khasi Hills"],
    "Mizoram": ["Aizawl", "Lunglei", "Lawngtlai", "Champhai", "Mamit", "Serchhip", "Kolasib", "Saitual", "Hnahthial", "Khawzawl"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Wokha", "Tuensang", "Mon", "Peren", "Phek", "Zunheboto", "Kiphire"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur", "Berhampur", "Balasore", "Puri", "Jajpur", "Sundargarh", "Keonjhar"],
    "Punjab": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Firozpur", "Hoshiarpur", "Rupnagar", "Sangrur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar", "Bharatpur", "Sikar", "Banswara"],
    "Sikkim": ["Gangtok", "Namchi", "Geyzing", "Mangan", "Ravangla", "Soreng", "Rimbi", "Pakyong", "Yuksom", "Dzongu"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tirunelveli", "Erode", "Vellore", "Thoothukudi", "Kanchipuram"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Mahbubnagar", "Suryapet", "Adilabad", "Nalgonda", "Rangareddy"],
    "Tripura": ["Agartala", "West Tripura", "Dhalai", "North Tripura", "South Tripura", "Khowai", "Gomati", "Sepahijala", "Unakoti", "Sipahijala"],
    "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Agra", "Varanasi", "Meerut", "Prayagraj", "Gorakhpur", "Noida", "Ghaziabad", "Bareilly"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Rudraprayag", "Tehri Garhwal", "Uttarkashi", "Chamoli", "Champawat", "Bageshwar"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Jalpaiguri", "Siliguri", "Murshidabad", "Nadia", "Hooghly", "Purulia", "Bankura"],
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

# Overpass fetcher (fixed)
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

            # Build address from available tags
            address_parts = [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:suburb"),
                tags.get("addr:city") or city,
                tags.get("addr:state") or state,
                tags.get("addr:postcode")
            ]
            address = ", ".join([part for part in address_parts if part]) or f"{city}, {state}"

            # Phone handling
            phone = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or "N/A"

            stations.append({
                "name": tags.get("name", "Unknown"),
                "address": address,
                "phone": phone,
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
            time.sleep(1.5)  # Respect API limits

    st.success(f"✅ Completed fetching for {total_cities} capitals!")

    json_output = json.dumps(all_data, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download JSON of Capitals Police Stations",
        data=json_output,
        file_name="india_capitals_police_stations.json",
        mime="application/json"
    )

    st.json(all_data)
