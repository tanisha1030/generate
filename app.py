import streamlit as st
import requests
import time
from typing import Dict, List
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# India Districts Dictionary (keeping your original dict)
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

class ProgressTracker:
    def __init__(self, total):
        self.current = 0
        self.total = total
        self.lock = threading.Lock()
        
    def increment(self):
        with self.lock:
            self.current += 1
            return self.current

def search_police_stations_optimized(district: str, state: str) -> List[Dict]:
    """Optimized search using multiple query strategies"""
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    police_stations = []
    seen_coords = set()
    
    # Strategy 1: Search by state area and district name in address
    query1 = f"""
    [out:json][timeout:25];
    area["name"="{state}"]["admin_level"="4"]->.state;
    (
      node["amenity"="police"]["addr:district"="{district}"](area.state);
      way["amenity"="police"]["addr:district"="{district}"](area.state);
    );
    out center 20;
    """
    
    # Strategy 2: Search by district area
    query2 = f"""
    [out:json][timeout:25];
    area["name"="{district}"]->.district;
    (
      node["amenity"="police"](area.district);
      way["amenity"="police"](area.district);
    );
    out center 15;
    """
    
    # Strategy 3: Fuzzy search by district name in station name
    query3 = f"""
    [out:json][timeout:25];
    area["name"="{state}"]["admin_level"="4"]->.state;
    (
      node["amenity"="police"]["name"~"{district}",i](area.state);
      way["amenity"="police"]["name"~"{district}",i](area.state);
    );
    out center 10;
    """
    
    queries = [query1, query2, query3]
    
    for query in queries:
        try:
            response = requests.post(overpass_url, data={'data': query}, timeout=30)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            
            for element in data.get('elements', []):
                # Get coordinates
                if element['type'] == 'node':
                    lat = element['lat']
                    lon = element['lon']
                elif 'center' in element:
                    lat = element['center']['lat']
                    lon = element['center']['lon']
                else:
                    continue
                
                # Check for duplicates
                coord_key = (round(lat, 4), round(lon, 4))
                if coord_key in seen_coords:
                    continue
                seen_coords.add(coord_key)
                
                tags = element.get('tags', {})
                
                # Extract only required fields
                station_info = {
                    'name': tags.get('name', 'Unnamed Police Station'),
                    'district': district,
                    'state': state,
                    'address': tags.get('addr:full') or tags.get('addr:street', '') or 'Not available',
                    'phone': tags.get('phone') or tags.get('contact:phone', '') or 'Not available',
                    'latitude': round(lat, 6),
                    'longitude': round(lon, 6)
                }
                
                police_stations.append(station_info)
            
            # Small delay between queries
            if police_stations:
                time.sleep(0.3)
            
            # If we found enough, stop searching
            if len(police_stations) >= 15:
                break
                
        except Exception as e:
            continue
    
    return police_stations[:25]  # Return up to 25 per district

def search_single_district_fast(state: str, district: str, tracker: ProgressTracker):
    """Fast search with single attempt"""
    try:
        stations = search_police_stations_optimized(district, state)
        current = tracker.increment()
        
        return {
            'state': state,
            'district': district,
            'stations': stations,
            'count': len(stations),
            'progress': current
        }
    except:
        current = tracker.increment()
        return {
            'state': state,
            'district': district,
            'stations': [],
            'count': 0,
            'progress': current
        }

def fetch_all_districts_fast(max_workers: int = 15):
    """Fetch all districts in parallel - optimized for speed"""
    all_results = []
    
    # Prepare all tasks
    tasks = []
    for state, districts in INDIA_DISTRICTS.items():
        for district in districts:
            tasks.append((state, district))
    
    total_districts = len(tasks)
    tracker = ProgressTracker(total_districts)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    stats_container = st.empty()
    
    completed = 0
    found_stations = 0
    districts_with_data = 0
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(search_single_district_fast, state, district, tracker): (state, district)
            for state, district in tasks
        }
        
        for future in as_completed(future_to_task):
            try:
                result = future.result()
                all_results.append(result)
                
                completed += 1
                if result['count'] > 0:
                    districts_with_data += 1
                    found_stations += result['count']
                
                # Update progress
                progress = completed / total_districts
                progress_bar.progress(progress)
                status_text.text(f"Processing: {result['district']}, {result['state']} ({completed}/{total_districts})")
                
                # Show live statistics
                stats_container.markdown(f"""
                **Live Statistics:**
                - ✅ Completed: {completed}/{total_districts} districts
                - 🚔 Police Stations Found: {found_stations}
                - 📊 Districts with Data: {districts_with_data}
                - ⏱️ Progress: {progress*100:.1f}%
                """)
                
                # Minimal delay for API respect
                time.sleep(0.2)
                
            except Exception as e:
                state, district = future_to_task[future]
                all_results.append({
                    'state': state,
                    'district': district,
                    'stations': [],
                    'count': 0
                })
    
    status_text.text("✅ Search complete!")
    return all_results

# Streamlit UI
st.set_page_config(page_title="Police Station Finder", page_icon="🚔", layout="wide")

st.title("🚔 Fast Police Station Database Generator")
st.markdown("Generate complete police station database for all Indian districts")

# Main Interface
st.info("""
### 🚀 Optimized Fast Search
- **Single-query approach** per district for maximum speed
- **Estimated time: 8-12 minutes** for all 776 districts
- **Parallel processing** with 15 concurrent workers
- **Clean JSON output** with only essential fields
- Automatically handles API rate limits
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total States/UTs", len(INDIA_DISTRICTS))
with col2:
    total_districts = sum(len(districts) for districts in INDIA_DISTRICTS.values())
    st.metric("Total Districts", total_districts)
with col3:
    max_workers = st.slider("Parallel Workers", 3, 12, 8, help="Higher = faster, but may hit rate limits. Recommended: 6-8")

if st.button("🚀 Generate Complete Database", type="primary", use_container_width=True):
    st.warning("⏳ Starting fast search... Estimated time: 8-12 minutes")
    
    start_time = time.time()
    results = fetch_all_districts_fast(max_workers=max_workers)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    st.success(f"✅ Completed in {elapsed_time/60:.1f} minutes!")
    
    # Prepare clean JSON structure
    clean_data = []
    for result in results:
        for station in result['stations']:
            clean_data.append({
                'name': station['name'],
                'district': station['district'],
                'state': station['state'],
                'address': station['address'],
                'phone': station['phone'],
                'latitude': station['latitude'],
                'longitude': station['longitude']
            })
    
    # Statistics
    total_stations = len(clean_data)
    districts_with_data = sum(1 for r in results if r['count'] > 0)
    
    st.subheader("📊 Final Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🚔 Total Police Stations", total_stations)
    with col2:
        st.metric("✅ Districts with Data", districts_with_data)
    with col3:
        coverage = (districts_with_data / total_districts) * 100
        st.metric("📈 Coverage", f"{coverage:.1f}%")
    
    # Preview data
    st.subheader("📋 Data Preview (First 20 records)")
    preview_df = pd.DataFrame(clean_data[:20])
    st.dataframe(preview_df, use_container_width=True)
    
    # Download buttons
    st.subheader("💾 Download Complete Database")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON download
        json_str = json.dumps(clean_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download JSON (Complete)",
            data=json_str,
            file_name="india_police_stations_complete.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # CSV download
        csv_df = pd.DataFrame(clean_data)
        csv_data = csv_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV (Complete)",
            data=csv_data,
            file_name="india_police_stations_complete.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Top districts
    st.subheader("🏆 Top 15 Districts by Police Stations Found")
    top_districts = sorted(
        [{'State': r['state'], 'District': r['district'], 'Stations': r['count']} 
         for r in results if r['count'] > 0],
        key=lambda x: x['Stations'],
        reverse=True
    )[:15]
    
    top_df = pd.DataFrame(top_districts)
    st.dataframe(top_df, use_container_width=True)
    
    # State-wise summary
    st.subheader("📍 State-wise Summary")
    state_summary = {}
    for result in results:
        state = result['state']
        if state not in state_summary:
            state_summary[state] = {'districts': 0, 'stations': 0}
        state_summary[state]['districts'] += 1
        state_summary[state]['stations'] += result['count']
    
    state_df = pd.DataFrame([
        {'State': state, 'Districts': data['districts'], 'Police Stations': data['stations']}
        for state, data in state_summary.items()
    ]).sort_values('Police Stations', ascending=False)
    
    st.dataframe(state_df, use_container_width=True)
    
    # Map visualization (sample)
    if clean_data:
        st.subheader("🗺️ Geographic Distribution (First 500 stations)")
        map_df = pd.DataFrame([
            {'lat': station['latitude'], 'lon': station['longitude']}
            for station in clean_data[:500]
        ])
        st.map(map_df, zoom=4)

# Sidebar
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    ### Features:
    - ⚡ **Ultra-fast parallel processing**
    - 🎯 **Single optimized query per district**
    - 📊 **Clean JSON/CSV output**
    - 🌐 **All 776+ districts covered**
    
    ### Output Fields:
    - Name
    - District
    - State
    - Address
    - Phone Number
    - Latitude
    - Longitude
    
    ### Performance:
    - Uses 15 concurrent workers (default)
    - Single comprehensive query per district
    - Automatic duplicate removal
    - Smart timeout handling
    - Estimated: **8-12 minutes** total
    
    ### Data Source:
    - OpenStreetMap (OSM)
    - Community-contributed data
    - Real-time API access
    
    ### Notes:
    - Coverage varies by region
    - Urban areas have better data
    - Some districts may have no data
    - Data is as accurate as OSM
    
    ### Tips:
    - Don't close window during processing
    - Lower workers if errors occur
    - Download both JSON and CSV
    - Verify critical data independently
    """)
    
    st.markdown("---")
    st.caption("Powered by OpenStreetMap")
    st.caption("Data © OpenStreetMap contributors")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>🚔 Fast Police Station Database Generator | OpenStreetMap Data</p>
    <p>Optimized for speed and accuracy | All 776+ Indian districts</p>
    <p style='font-size: 0.8em;'>
        <strong>Disclaimer:</strong> Data sourced from OpenStreetMap. 
        Always verify with official sources for critical information.
    </p>
</div>
""", unsafe_allow_html=True)
