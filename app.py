import streamlit as st
import requests
import time
from typing import Dict, List, Optional
import pandas as pd
import json

# India Districts Dictionary
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

def search_police_stations(district: str, state: str, limit: int = 10) -> List[Dict]:
    """Search for police stations in a district using Overpass API (OpenStreetMap)"""
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Overpass QL query to find police stations
    query = f"""
    [out:json][timeout:25];
    area["name"="{state}"]["admin_level"="4"]->.state;
    (
      node["amenity"="police"](area.state);
      way["amenity"="police"](area.state);
      relation["amenity"="police"](area.state);
    );
    out center {limit};
    """
    
    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        police_stations = []
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
            
            tags = element.get('tags', {})
            
            # Extract police station info
            station_info = {
                'name': tags.get('name', 'Unnamed Police Station'),
                'latitude': lat,
                'longitude': lon,
                'address': tags.get('addr:full') or tags.get('addr:street', ''),
                'city': tags.get('addr:city', ''),
                'district': tags.get('addr:district', district),
                'state': state,
                'phone': tags.get('phone') or tags.get('contact:phone', ''),
                'police_type': tags.get('police', 'Unknown'),
                'operator': tags.get('operator', '')
            }
            
            police_stations.append(station_info)
        
        return police_stations
    
    except Exception as e:
        st.error(f"Error fetching police stations: {str(e)}")
        return []

def fetch_all_police_stations():
    """Fetch police stations for all districts"""
    all_data = {}
    total_districts = sum(len(districts) for districts in INDIA_DISTRICTS.values())
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    current = 0
    
    for state, districts in INDIA_DISTRICTS.items():
        all_data[state] = {}
        
        for district in districts:
            current += 1
            status_text.text(f"Searching police stations in: {district}, {state} ({current}/{total_districts})")
            
            # Search for police stations
            stations = search_police_stations(district, state, limit=10)
            
            all_data[state][district] = {
                "district": district,
                "state": state,
                "police_stations": stations,
                "total_found": len(stations)
            }
            
            progress_bar.progress(current / total_districts)
            time.sleep(2)  # Rate limiting for Overpass API
    
    status_text.text("✅ Search complete!")
    return all_data

# Streamlit UI
st.set_page_config(page_title="Police Station Finder", page_icon="🚔", layout="wide")

st.title("🚔 Police Station Finder for Indian Districts")
st.markdown("Find police stations across all districts in India using OpenStreetMap data")

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["🔍 Search by District", "📊 View All Data", "🗺️ Generate Complete Database"])

with tab1:
    st.subheader("Search Police Stations by District")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_state = st.selectbox("Select State/UT:", sorted(INDIA_DISTRICTS.keys()))
    
    with col2:
        selected_district = st.selectbox("Select District:", sorted(INDIA_DISTRICTS[selected_state]))
    
    num_results = st.slider("Number of results to fetch:", 5, 50, 10)
    
    if st.button("🔍 Search Police Stations", type="primary", key="search_single"):
        with st.spinner(f"Searching for police stations in {selected_district}, {selected_state}..."):
            stations = search_police_stations(selected_district, selected_state, limit=num_results)
            
            if stations:
                st.success(f"✅ Found {len(stations)} police station(s)")
                
                # Display in cards
                for idx, station in enumerate(stations, 1):
                    with st.expander(f"🚔 {idx}. {station['name']}", expanded=(idx==1)):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**📍 Address:** {station['address'] or 'Not available'}")
                            st.write(f"**🏙️ City:** {station['city'] or 'Not available'}")
                            st.write(f"**📍 District:** {station['district']}")
                            st.write(f"**🗺️ State:** {station['state']}")
                            st.write(f"**📞 Phone:** {station['phone'] or 'Not available'}")
                            st.write(f"**🚨 Type:** {station['police_type']}")
                            if station['operator']:
                                st.write(f"**👮 Operator:** {station['operator']}")
                        
                        with col2:
                            st.write(f"**Coordinates:**")
                            st.write(f"Lat: {station['latitude']:.6f}")
                            st.write(f"Lon: {station['longitude']:.6f}")
                            
                            osm_link = f"https://www.openstreetmap.org/?mlat={station['latitude']}&mlon={station['longitude']}&zoom=17"
                            st.markdown(f"[📍 View on Map]({osm_link})")
                            
                            gmaps_link = f"https://www.google.com/maps?q={station['latitude']},{station['longitude']}"
                            st.markdown(f"[🗺️ Google Maps]({gmaps_link})")
                
                # Show on map
                st.subheader("🗺️ Map View")
                map_df = pd.DataFrame([
                    {'lat': s['latitude'], 'lon': s['longitude'], 'name': s['name']}
                    for s in stations
                ])
                st.map(map_df, zoom=10)
                
                # Download as CSV
                st.subheader("💾 Download Data")
                csv_data = pd.DataFrame(stations).to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"police_stations_{selected_district}_{selected_state}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No police stations found in OpenStreetMap database for this district.")
                st.info("💡 Try searching for a different district or the data might not be available in OSM.")

with tab2:
    st.subheader("📊 View Previously Generated Data")
    
    if 'police_data' in st.session_state:
        data = st.session_state['police_data']
        
        # Statistics
        total_districts = sum(len(districts) for districts in data.values())
        total_stations = sum(
            district_data['total_found'] 
            for state_data in data.values() 
            for district_data in state_data.values()
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Total Districts", total_districts)
        with col2:
            st.metric("🚔 Total Police Stations", total_stations)
        with col3:
            avg_per_district = total_stations / total_districts if total_districts > 0 else 0
            st.metric("📊 Avg per District", f"{avg_per_district:.1f}")
        
        # State-wise breakdown
        st.subheader("📈 State-wise Breakdown")
        state_stats = []
        for state, districts in data.items():
            state_total = sum(d['total_found'] for d in districts.values())
            state_stats.append({
                'State': state,
                'Districts': len(districts),
                'Police Stations': state_total
            })
        
        stats_df = pd.DataFrame(state_stats).sort_values('Police Stations', ascending=False)
        st.dataframe(stats_df, use_container_width=True)
        
        # Flatten data for CSV
        st.subheader("💾 Download Complete Data")
        flat_data = []
        for state, districts in data.items():
            for district, district_data in districts.items():
                for station in district_data['police_stations']:
                    flat_data.append({
                        'State': state,
                        'District': district,
                        'Station_Name': station['name'],
                        'Address': station['address'],
                        'City': station['city'],
                        'Phone': station['phone'],
                        'Police_Type': station['police_type'],
                        'Operator': station['operator'],
                        'Latitude': station['latitude'],
                        'Longitude': station['longitude']
                    })
        
        if flat_data:
            flat_df = pd.DataFrame(flat_data)
            
            col1, col2 = st.columns(2)
            with col1:
                csv_data = flat_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Stations (CSV)",
                    data=csv_data,
                    file_name="all_police_stations_india.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download All Stations (JSON)",
                    data=json_str,
                    file_name="all_police_stations_india.json",
                    mime="application/json"
                )
    else:
        st.info("ℹ️ No data available. Please generate the database from Tab 3.")

with tab3:
    st.subheader("🗺️ Generate Complete Police Station Database")
    st.info("""
    This will search for police stations in all 787+ districts across India.
    
    ⚠️ **Important Notes:**
    - This process will take approximately **30-45 minutes** due to API rate limits
    - It will make ~787 API requests to OpenStreetMap Overpass API
    - Please be patient and do not refresh the page
    - Some districts may have limited data in OpenStreetMap
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total States/UTs", len(INDIA_DISTRICTS))
    with col2:
        total_districts = sum(len(districts) for districts in INDIA_DISTRICTS.values())
        st.metric("Total Districts", total_districts)
    
    if st.button("🚀 Start Generating Police Station Data", type="primary", key="generate_all"):
        st.warning("⏳ This will take 30-45 minutes. Please don't close this window.")
        
        start_time = time.time()
        all_police_data = fetch_all_police_stations()
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        st.success(f"✅ Completed in {elapsed_time/60:.1f} minutes!")
        
        # Store in session state
        st.session_state['police_data'] = all_police_data
        
        # Display summary
        st.subheader("📊 Summary")
        total_stations = 0
        districts_with_data = 0
        districts_without_data = 0
        
        for state, districts in all_police_data.items():
            for district, data in districts.items():
                if data['total_found'] > 0:
                    districts_with_data += 1
                    total_stations += data['total_found']
                else:
                    districts_without_data += 1
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🚔 Total Police Stations", total_stations)
        with col2:
            st.metric("✅ Districts with Data", districts_with_data)
        with col3:
            st.metric("❌ Districts without Data", districts_without_data)
        with col4:
            avg_per_district = total_stations / districts_with_data if districts_with_data > 0 else 0
            st.metric("📊 Avg per District", f"{avg_per_district:.1f}")
        
        # Top districts
        st.subheader("🏆 Top 10 Districts by Police Stations")
        top_districts = []
        for state, districts in all_police_data.items():
            for district, data in districts.items():
                if data['total_found'] > 0:
                    top_districts.append({
                        'State': state,
                        'District': district,
                        'Police Stations': data['total_found']
                    })
        
        top_df = pd.DataFrame(top_districts).sort_values('Police Stations', ascending=False).head(10)
        st.dataframe(top_df, use_container_width=True)
        
        # Preview data
        st.subheader("📋 Sample Data Preview")
        preview_data = []
        for state, districts in all_police_data.items():
            for district, district_data in districts.items():
                for station in district_data['police_stations'][:2]:  # First 2 from each
                    preview_data.append({
                        'State': state,
                        'District': district,
                        'Station Name': station['name'],
                        'Address': station['address'],
                        'Phone': station['phone'],
                        'Latitude': station['latitude'],
                        'Longitude': station['longitude']
                    })
                    if len(preview_data) >= 20:
                        break
                if len(preview_data) >= 20:
                    break
            if len(preview_data) >= 20:
                break
        
        preview_df = pd.DataFrame(preview_data)
        st.dataframe(preview_df, use_container_width=True)
        
        # Download buttons
        st.subheader("💾 Download Options")
        
        # Flatten data
        flat_data = []
        for state, districts in all_police_data.items():
            for district, district_data in districts.items():
                for station in district_data['police_stations']:
                    flat_data.append({
                        'State': state,
                        'District': district,
                        'Station_Name': station['name'],
                        'Address': station['address'],
                        'City': station['city'],
                        'Phone': station['phone'],
                        'Police_Type': station['police_type'],
                        'Operator': station['operator'],
                        'Latitude': station['latitude'],
                        'Longitude': station['longitude']
                    })
        
        flat_df = pd.DataFrame(flat_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv_data = flat_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV (Flat)",
                data=csv_data,
                file_name="india_police_stations_complete.csv",
                mime="text/csv",
                key="download_csv"
            )
        
        with col2:
            # JSON download
            json_str = json.dumps(all_police_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download as JSON (Hierarchical)",
                data=json_str,
                file_name="india_police_stations_complete.json",
                mime="application/json",
                key="download_json"
            )
        
        # Map visualization
        st.subheader("🗺️ Map Visualization (Sample)")
        if not flat_df.empty:
            map_sample = flat_df.head(100)[['Latitude', 'Longitude']].rename(
                columns={'Latitude': 'lat', 'Longitude': 'lon'}
            )
            st.map(map_sample, zoom=4)
            st.caption("Showing first 100 police stations on map")

# Sidebar
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    ### Features:
    - 🔍 Search police stations by district
    - 🗺️ Uses OpenStreetMap Overpass API
    - 📍 Get exact coordinates & addresses
    - 📞 Contact information when available
    - 📊 Generate complete database
    - 💾 Export to CSV/JSON
    
    ### Coverage:
    - All 787+ districts across India
    - 36 States and Union Territories
    
    ### Data Source:
    - OpenStreetMap (OSM) database
    - Community-contributed data
    - May not be 100% complete
    
    ### Tips:
    - Data availability varies by district
    - Urban areas have better coverage
    - You can contribute to OSM to improve data
    
    ### Rate Limits:
    - 2 seconds between requests
    - Bulk operations take time
    - Please be patient
    """)
    
    st.markdown("---")
    
    st.subheader("📊 Quick Stats")
    if 'police_data' in st.session_state:
        data = st.session_state['police_data']
        total_stations = sum(
            district_data['total_found'] 
            for state_data in data.values() 
            for district_data in state_data.values()
        )
        st.metric("🚔 Stations in Database", total_stations)
    else:
        st.info("No data loaded yet")
    
    st.markdown("---")
    st.caption("Powered by OpenStreetMap Overpass API")
    st.caption("⚠️ Please respect API usage policies")
    st.caption("Data © OpenStreetMap contributors")
