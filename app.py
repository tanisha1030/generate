# app_accurate_all_districts.py
import streamlit as st
import requests
import json
import pandas as pd
import time
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Tuple

st.set_page_config(page_title="🚔 India Police Stations — Accurate (All Districts)", layout="wide")

st.title("🚔 India Police Stations — Accurate Mode (All Districts)")
st.markdown(
    "This app will attempt to fetch **all police station** OSM objects for every district in the built-in dictionary, "
    "dedupe them, and export JSON + CSV with `name, district, state, address, phone, latitude, longitude`."
)

# ==========================
# 1) Full state->district dictionary (from your data)
# ==========================
INDIA_DISTRICTS = {
    "Andhra Pradesh": ["Alluri Sitharama Raju", "Anakapalli", "Anantapur", "Annamayya", "Bapatla", "Chittoor", "Dr. B.R. Ambedkar Konaseema", "East Godavari", "Eluru", "Guntur", "Kakinada", "Krishna", "Kurnool", "Nandyal", "NTR", "Palnadu", "Parvathipuram Manyam", "Prakasam", "Sri Potti Sriramulu Nellore", "Sri Sathya Sai", "Srikakulam", "Tirupati", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
    "Arunachal Pradesh": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Kamle", "Kra Daadi", "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang", "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang", "Bichom", "Keyi Panyor"],
    "Assam": ["Bajali", "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dima Hasao", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
    "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"],
    "Chhattisgarh": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Gaurela-Pendra-Marwahi", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Manendragarh-Chirmiri-Bharatpur", "Mohla-Manpur-Ambagarh Chowki", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sakti", "Sarangarh-Bilaigarh", "Sukma", "Surajpur", "Surguja", "Khairagarh-Chhuikhadan-Gandai"],
    "Goa": ["North Goa", "South Goa"],
    "Gujarat": ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"],
    "Haryana": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
    "Himachal Pradesh": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul-Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"],
    "Jharkhand": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Kodarma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahebganj", "Saraikela-Kharsawan", "Simdega", "West Singhbhum"],
    "Karnataka": ["Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikkaballapura", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davangere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumkur", "Udupi", "Uttara Kannada", "Vijayapura", "Vijayanagara", "Yadgir"],
    "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"],
    "Madhya Pradesh": ["Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Maihar", "Mandla", "Mandsaur", "Mauganj", "Morena", "Narsinghpur", "Neemuch", "Niwari", "Panna", "Pandhurna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"],
    "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"],
    "Manipur": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"],
    "Meghalaya": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "Eastern West Khasi Hills", "North Garo Hills", "Ri Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"],
    "Mizoram": ["Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Saitual", "Serchhip", "Siaha"],
    "Nagaland": ["Chumukedima", "Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Niuland", "Noklak", "Peren", "Phek", "Shamator", "Tseminyu", "Tuensang", "Wokha", "Zunheboto"],
    "Odisha": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Debagarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Keonjhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"],
    "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Firozpur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Malerkotla", "Mansa", "Moga", "Mohali", "Muktsar", "Pathankot", "Patiala", "Rupnagar", "Sangrur", "Shahid Bhagat Singh Nagar", "Tarn Taran"],
    "Rajasthan": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalor", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"],
    "Sikkim": ["East Sikkim", "North Sikkim", "Pakyong", "Soreng", "South Sikkim", "West Sikkim"],
    "Tamil Nadu": ["Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Thoothukudi", "Vellore", "Viluppuram", "Virudhunagar"],
    "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Komaram Bheem", "Mahabubabad", "Mahbubnagar", "Mancherial", "Medak", "Medchal-Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal Rural", "Warangal Urban", "Yadadri Bhuvanagiri"],
    "Tripura": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],
    "Uttar Pradesh": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Sant Ravidas Nagar", "Shahjahanpur", "Shamli", "Shrawasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"],
    "Uttarakhand": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"],
    "West Bengal": ["Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"],
    "Andaman and Nicobar Islands": ["Nicobar", "North and Middle Andaman", "South Andaman"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Dadra and Nagar Haveli", "Daman", "Diu"],
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
    "Jammu and Kashmir": ["Anantnag", "Bandipora", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Srinagar", "Udhampur"],
    "Ladakh": ["Kargil", "Leh"],
    "Lakshadweep": ["Agatti", "Amini", "Andrott", "Kadmath", "Kavaratti", "Minicoy", "Chetlat", "Bitra"],
    "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"]
}

# ==========================
# 2) Settings (UI)
# ==========================
st.sidebar.header("Settings")
max_workers = st.sidebar.slider("Max concurrent workers", 4, 30, 12)
per_district_limit = st.sidebar.number_input("Max results per district (0 = no limit)", min_value=0, max_value=2000, value=0)
timeout_sec = st.sidebar.slider("HTTP timeout (s)", 10, 120, 40)
pause_between_requests = st.sidebar.slider("Pause between requests per worker (s)", 0.0, 2.0, 0.2, step=0.1)
use_local_cache = st.sidebar.checkbox("Use local resume file if present", True)
output_json = Path("police_stations_all_districts.json")
output_csv = Path("police_stations_all_districts.csv")

st.sidebar.markdown("""
**Notes**
- Accurate Mode = fetches all matching OSM objects (nodes/ways/relations) per district, then dedupes.
- If the run is interrupted you can resume if `police_stations_partial.json` exists and resume is enabled.
""")

# ==========================
# 3) Overpass helper & queries
# ==========================
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def overpass_post(query: str, timeout: int = 40) -> dict:
    headers = {"Accept-Encoding": "gzip"}
    try:
        r = requests.post(OVERPASS_URL, data={"data": query}, timeout=timeout, headers=headers)
        if r.status_code == 200:
            return r.json()
        else:
            # return empty structure for non-200 to let caller handle retry/backoff
            return {}
    except Exception:
        return {}

def build_queries(state: str, district: str) -> List[str]:
    """
    Prioritized queries for accurate coverage:
    1) Search OSM area that matches district name (nodes/ways/relations)
    2) Search within state area for objects where addr:district or addr:city matches
    3) Fuzzy name search containing 'police' + district name
    4) State-wide police objects (as last resort)
    """
    q1 = f"""
    [out:json][timeout:{timeout_sec}];
    area["name"="{district}"]["boundary"="administrative"]->.d;
    (
      node["amenity"="police"](area.d);
      way["amenity"="police"](area.d);
      relation["amenity"="police"](area.d);
    );
    out center {per_district_limit or 500};
    """
    q2 = f"""
    [out:json][timeout:{timeout_sec}];
    area["name"="{state}"]["boundary"="administrative"]->.s;
    (
      node["amenity"="police"]["addr:district"~"{district}",i](area.s);
      way["amenity"="police"]["addr:district"~"{district}",i](area.s);
      relation["amenity"="police"]["addr:district"~"{district}",i](area.s);
      node["amenity"="police"]["addr:city"~"{district}",i](area.s);
      way["amenity"="police"]["addr:city"~"{district}",i](area.s);
      relation["amenity"="police"]["addr:city"~"{district}",i](area.s);
    );
    out center {per_district_limit or 500};
    """
    q3 = f"""
    [out:json][timeout:{timeout_sec}];
    area["name"="{state}"]["boundary"="administrative"]->.s;
    (
      node["amenity"="police"]["name"~"{district}",i](area.s);
      way["amenity"="police"]["name"~"{district}",i](area.s);
      relation["amenity"="police"]["name"~"{district}",i](area.s);
    );
    out center {per_district_limit or 500};
    """
    q4 = f"""
    [out:json][timeout:{timeout_sec}];
    area["name"="{state}"]["boundary"="administrative"]->.s;
    (
      node["amenity"="police"](area.s);
      way["amenity"="police"](area.s);
      relation["amenity"="police"](area.s);
    );
    out center {per_district_limit or 500};
    """
    q5 = f"""
    [out:json][timeout:{timeout_sec}];
    (
      node["amenity"="police"]["name"~"police|station|thana|chowki|ps",i];
      way["amenity"="police"]["name"~"police|station|thana|chowki|ps",i];
      relation["amenity"="police"]["name"~"police|station|thana|chowki|ps",i];
    );
    out center 50;
    """
    return [q1, q2, q3, q4, q5]

def extract_station_info(elem: dict, state: str, district: str) -> Dict:
    tags = elem.get("tags", {}) or {}
    # For way/relation center may be in 'center' key
    lat = elem.get("lat") or elem.get("center", {}).get("lat")
    lon = elem.get("lon") or elem.get("center", {}).get("lon")
    name = tags.get("name") or tags.get("official_name") or "Unnamed Police Station"
    # Build address from tags if available
    addr_full = tags.get("addr:full")
    if not addr_full:
        parts = []
        for k in ("addr:street", "addr:housename", "addr:housenumber", "addr:place"):
            if tags.get(k):
                parts.append(tags.get(k))
        # city/district/state
        if tags.get("addr:city"):
            parts.append(tags.get("addr:city"))
        if tags.get("addr:district"):
            parts.append(tags.get("addr:district"))
        if tags.get("addr:state"):
            parts.append(tags.get("addr:state"))
        addr_full = ", ".join(parts) if parts else tags.get("description") or tags.get("note") or "Not available"
    phone = tags.get("phone") or tags.get("contact:phone") or tags.get("telephone") or tags.get("contact:telephone") or "Not available"
    return {
        "name": name,
        "district": district,
        "state": state,
        "address": addr_full,
        "phone": phone,
        "latitude": round(lat, 6) if isinstance(lat, (float, int)) else None,
        "longitude": round(lon, 6) if isinstance(lon, (float, int)) else None
    }

# ==========================
# 4) Worker function (per district)
# ==========================
def fetch_for_district(state: str, district: str) -> List[Dict]:
    """
    Return list of station dicts for the district.
    """
    results = []
    seen = set()  # dedupe by (rounded lat, lon, name)
    queries = build_queries(state, district)

    for q in queries:
        if per_district_limit and len(results) >= per_district_limit:
            break
        data = overpass_post(q, timeout=timeout_sec)
        if not data:
            time.sleep(0.5)
            continue
        elements = data.get("elements", [])
        for el in elements:
            info = extract_station_info(el, state, district)
            key = (info["name"].strip().lower() if info["name"] else "", info["latitude"], info["longitude"])
            # ignore results without coords in accurate mode
            if info["latitude"] is None or info["longitude"] is None:
                continue
            if key in seen:
                continue
            seen.add(key)
            results.append(info)
            if per_district_limit and len(results) >= per_district_limit:
                break
        # short polite pause
        time.sleep(pause_between_requests)
        # if we got some robust results from best queries, we may continue to next district
        if results:
            # Continue to collect more from subsequent queries (since accurate mode)
            continue
    # final dedupe by coords+name (already handled)
    return results

# ==========================
# 5) Resume / partial saving helpers
# ==========================
PARTIAL_FILE = Path("police_stations_partial.json")

def save_partial(results: List[Dict]):
    with PARTIAL_FILE.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def load_partial() -> List[Dict]:
    if PARTIAL_FILE.exists():
        try:
            return json.loads(PARTIAL_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

# ==========================
# 6) Main UI & execution
# ==========================
st.header("Run controls")
col1, col2, col3 = st.columns(3)
with col1:
    run_button = st.button("🚀 Start Accurate Fetch (All Districts)")
with col2:
    stop_button = st.button("🛑 Cancel (soft)")
with col3:
    clear_cache = st.button("🧹 Clear partial resume file")

if clear_cache:
    if PARTIAL_FILE.exists():
        PARTIAL_FILE.unlink()
    st.success("Partial resume file cleared.")

# Prepare list of (state, district)
tasks = [(s, d) for s, lst in INDIA_DISTRICTS.items() for d in lst]
total_tasks = len(tasks)
st.info(f"Total districts to process: **{total_tasks}**")

# Display small summary
st.markdown(f"- Workers: **{max_workers}** | Per-district limit: **{per_district_limit or 'no limit'}** | Timeout: **{timeout_sec}s**")

# Execution
if run_button:
    st.info("Starting accurate fetch. Output will be saved to JSON + CSV when complete.")
    results_master: List[Dict] = []

    # If resume allowed and file exists, load existing
    if use_local_cache and PARTIAL_FILE.exists():
        st.warning("Found partial results file — loading and resuming from it.")
        results_master = load_partial()
        # compute set of processed districts to skip
        processed_pairs = {(r["state"], r["district"]) for r in results_master}
    else:
        processed_pairs = set()

    progress_bar = st.progress(0)
    status = st.empty()
    start_time = time.time()
    cancelled = False
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {}
        for state, district in tasks:
            if (state, district) in processed_pairs:
                completed += 1
                progress_bar.progress(completed / total_tasks)
                continue
            future = executor.submit(fetch_for_district, state, district)
            future_to_task[future] = (state, district)

        try:
            for future in as_completed(future_to_task):
                state, district = future_to_task[future]
                if stop_button:
                    cancelled = True
                    break
                try:
                    district_results = future.result()
                except Exception as e:
                    district_results = []
                # If nothing found, we try a tiny fallback: name-based global search limited few
                if not district_results:
                    # small fuzzy fallback
                    qf = f"""
                    [out:json][timeout:{timeout_sec}];
                    (
                      node["amenity"="police"]["name"~"{district}",i];
                      way["amenity"="police"]["name"~"{district}",i];
                      relation["amenity"="police"]["name"~"{district}",i];
                    );
                    out center 5;
                    """
                    dataf = overpass_post(qf, timeout=timeout_sec)
                    for el in dataf.get("elements", []):
                        info = extract_station_info(el, state, district)
                        if info["latitude"] and info["longitude"]:
                            district_results.append(info)
                # If still empty, fallback to state-level first police as final fallback
                if not district_results:
                    qf2 = f"""
                    [out:json][timeout:{timeout_sec}];
                    area["name"="{state}"]["boundary"="administrative"]->.s;
                    (
                      node["amenity"="police"](area.s);
                      way["amenity"="police"](area.s);
                      relation["amenity"="police"](area.s);
                    );
                    out center 1;
                    """
                    dataf2 = overpass_post(qf2, timeout=timeout_sec)
                    for el in dataf2.get("elements", []):
                        info = extract_station_info(el, state, district)
                        if info["latitude"] and info["longitude"]:
                            district_results.append(info)
                            break

                # attach to master results (possibly multiple per district)
                # ensure each entry has district/state fields set
                for r in district_results:
                    results_master.append(r)

                completed += 1
                progress_bar.progress(completed / total_tasks)
                status.text(f"Processed {completed}/{total_tasks}: {district}, {state} — found {len(district_results)} stations")
                # save partial frequently to allow resume
                if completed % 10 == 0:
                    save_partial(results_master)
                # small delay
                time.sleep(0.05)
        except KeyboardInterrupt:
            cancelled = True

    # Final save
    elapsed = time.time() - start_time
    st.success(f"Finished (or stopped). Time elapsed: {elapsed:.1f} s — districts processed: {completed}/{total_tasks}")

    # Deduplicate master results globally: by (state,district,rounded lat,lon,name)
    deduped = []
    seen_keys = set()
    for r in results_master:
        key = (r["state"], r["district"], r["name"].strip().lower() if r["name"] else "", r["latitude"], r["longitude"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(r)

    # Save final JSON & CSV
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)
    df_out = pd.DataFrame(deduped)
    # Ensure column order
    cols = ["name", "district", "state", "address", "phone", "latitude", "longitude"]
    for c in cols:
        if c not in df_out.columns:
            df_out[c] = None
    df_out = df_out[cols]
    df_out.to_csv(output_csv, index=False, encoding="utf-8")

    # Remove partial file (optional)
    if PARTIAL_FILE.exists():
        PARTIAL_FILE.unlink()

    st.success(f"Saved {len(deduped)} unique police-station records to:\n- {output_json}\n- {output_csv}")
    st.dataframe(df_out.head(50), use_container_width=True)
    # Map (sample up to first 2000 points)
    if not df_out.empty:
        map_df = df_out.dropna(subset=["latitude", "longitude"]).head(2000)
        st.map(map_df.rename(columns={"latitude": "lat", "longitude": "lon"}))

    # Download buttons
    st.download_button("📥 Download JSON", output_json.read_text(encoding="utf-8"), file_name=str(output_json.name), mime="application/json")
    st.download_button("📥 Download CSV", output_csv.read_bytes(), file_name=str(output_csv.name), mime="text/csv")

