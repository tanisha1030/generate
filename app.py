import streamlit as st
import re
import requests
import time
from typing import Dict, List, Tuple, Optional
import pandas as pd
import json

# India Districts Dictionary
INDIA_DISTRICTS = {
    "Andhra Pradesh": ["Alluri Sitharama Raju", "Anakapalli", "Anantapur", "Annamayya", "Bapatla", "Chittoor", "Dr. B.R. Ambedkar Konaseema", "East Godavari", "Eluru", "Guntur", "Kakinada", "Krishna", "Kurnool", "Nandyal", "NTR", "Palnadu", "Parvathipuram Manyam", "Prakasam", "Sri Potti Sriramulu Nellore", "Sri Sathya Sai", "Srikakulam", "Tirupati", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
    "Arunachal Pradesh": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Kamle", "Kra Daadi", "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang", "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang", "Bichom", "Keyi Panyor"],
    "Assam": ["Bajali", "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dima Hasao", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
    "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"],
    "Chhattisgarh": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Gaurela-Pendra-Marwahi", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Manendragarh-Chirmiri-Bharatpur", "Mohla-Manpur-Ambagarh Chowki", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sakti", "Sarangarh-Bilaigarh", "Sukma", "Surajpur", "Surguja", "Khairagarh-Chhuikhadan-Gandai", "Bastar"],
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

def geocode_with_nominatim(query: str) -> Optional[Dict]:
    """Geocode address using OpenStreetMap Nominatim API"""
    base_url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'in',
        'addressdetails': 1
    }
    
    headers = {
        'User-Agent': 'AddressExtractorApp/1.0'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()
        
        if results:
            result = results[0]
            return {
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'display_name': result['display_name'],
                'address': result.get('address', {})
            }
    except Exception as e:
        return None
    
    return None

def fetch_all_districts_data():
    """Fetch geocoding data for all districts"""
    all_data = {}
    total_districts = sum(len(districts) for districts in INDIA_DISTRICTS.values())
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    current = 0
    
    for state, districts in INDIA_DISTRICTS.items():
        all_data[state] = {}
        
        for district in districts:
            current += 1
            status_text.text(f"Processing: {district}, {state} ({current}/{total_districts})")
            
            # Create search query
            search_query = f"{district}, {state}, India"
            
            # Geocode
            location_data = geocode_with_nominatim(search_query)
            
            if location_data:
                all_data[state][district] = {
                    "district": district,
                    "state": state,
                    "latitude": location_data['latitude'],
                    "longitude": location_data['longitude'],
                    "display_name": location_data['display_name'],
                    "address": location_data['address']
                }
            else:
                all_data[state][district] = {
                    "district": district,
                    "state": state,
                    "latitude": None,
                    "longitude": None,
                    "display_name": None,
                    "address": None,
                    "error": "Geocoding failed"
                }
            
            progress_bar.progress(current / total_districts)
            time.sleep(1.5)  # Rate limiting for Nominatim API
    
    status_text.text("✅ Processing complete!")
    return all_data

def extract_phone_numbers(text: str) -> List[str]:
    """Extract Indian phone numbers from text"""
    patterns = [
        r'\+91[-\s]?\d{10}',
        r'\b\d{10}\b',
        r'\b\d{5}[-\s]?\d{5}\b',
        r'\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',
    ]
    
    phone_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    cleaned = []
    for num in phone_numbers:
        cleaned_num = re.sub(r'[-\s]', '', num)
        if len(cleaned_num) == 10 or (len(cleaned_num) == 12 and cleaned_num.startswith('91')):
            if cleaned_num not in cleaned:
                cleaned.append(cleaned_num)
    
    return cleaned

def extract_pincode(text: str) -> Optional[str]:
    """Extract Indian pincode from text"""
    pincode_pattern = r'\b[1-9]\d{5}\b'
    matches = re.findall(pincode_pattern, text)
    return matches[0] if matches else None

def find_district_and_state(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Find district and state from text using the districts dictionary"""
    text_lower = text.lower()
    
    for state, districts in INDIA_DISTRICTS.items():
        if state.lower() in text_lower:
            for district in districts:
                if district.lower() in text_lower:
                    return district, state
            return None, state
        
        for district in districts:
            if district.lower() in text_lower:
                return district, state
    
    return None, None

def extract_full_address(text: str) -> str:
    """Extract the full address from text by cleaning and formatting"""
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', text.strip())
    # Remove common prefixes
    prefixes = ['address:', 'location:', 'office:', 'addr:']
    for prefix in prefixes:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    return cleaned

def extract_address_components(text: str) -> Dict:
    """Extract all address components from text"""
    district, state = find_district_and_state(text)
    phone_numbers = extract_phone_numbers(text)
    pincode = extract_pincode(text)
    full_address = extract_full_address(text)
    
    location_data = None
    if district and state:
        search_query = f"{district}, {state}, India"
        time.sleep(1)
        location_data = geocode_with_nominatim(search_query)
    elif state:
        search_query = f"{state}, India"
        time.sleep(1)
        location_data = geocode_with_nominatim(search_query)
    
    return {
        'full_address': full_address,
        'district': district,
        'state': state,
        'pincode': pincode,
        'phone_numbers': phone_numbers,
        'location_data': location_data
    }

# Streamlit UI
st.set_page_config(page_title="Address & Location Extractor", page_icon="📍", layout="wide")

st.title("📍 Address & Location Extractor")
st.markdown("Extract address details, phone numbers, and coordinates using OpenStreetMap")

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["📝 Text Input", "📊 Bulk Processing", "🗺️ Generate All Districts Data"])

with tab1:
    st.subheader("Enter Text to Extract Information")
    
    text_input = st.text_area(
        "Paste address or text containing location information:",
        height=150,
        placeholder="Example: Office located at MG Road, Bangalore, Karnataka 560001. Contact: 9876543210"
    )
    
    if st.button("Extract Information", type="primary", key="extract_single"):
        if text_input.strip():
            with st.spinner("Extracting information..."):
                result = extract_address_components(text_input)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📄 Extracted Information")
                    
                    if result['full_address']:
                        st.success(f"**Full Address:** {result['full_address']}")
                    
                    if result['state']:
                        st.success(f"**State:** {result['state']}")
                    else:
                        st.warning("State not found")
                    
                    if result['district']:
                        st.success(f"**District:** {result['district']}")
                    else:
                        st.warning("District not found")
                    
                    if result['pincode']:
                        st.success(f"**Pincode:** {result['pincode']}")
                    else:
                        st.info("Pincode not found")
                    
                    if result['phone_numbers']:
                        st.success(f"**Phone Numbers:** {', '.join(result['phone_numbers'])}")
                    else:
                        st.info("No phone numbers found")
                
                with col2:
                    st.subheader("🗺️ Location Data")
                    
                    if result['location_data']:
                        loc = result['location_data']
                        st.success(f"**Latitude:** {loc['latitude']}")
                        st.success(f"**Longitude:** {loc['longitude']}")
                        st.info(f"**Full Address:** {loc['display_name']}")
                        
                        df_map = pd.DataFrame({
                            'lat': [loc['latitude']],
                            'lon': [loc['longitude']]
                        })
                        st.map(df_map, zoom=12)
                        
                        osm_link = f"https://www.openstreetmap.org/?mlat={loc['latitude']}&mlon={loc['longitude']}&zoom=15"
                        st.markdown(f"[📍 View on OpenStreetMap]({osm_link})")
                    else:
                        st.warning("Could not geocode the location.")
        else:
            st.warning("Please enter some text.")

with tab2:
    st.subheader("Bulk Processing from CSV")
    st.info("Upload a CSV file with a column containing addresses or text.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        
        columns = df.columns.tolist()
        text_column = st.selectbox("Select the column containing address/text:", columns)
        
        if st.button("Process All Rows", type="primary", key="process_bulk"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, row in df.iterrows():
                status_text.text(f"Processing row {idx + 1} of {len(df)}...")
                text = str(row[text_column])
                
                extracted = extract_address_components(text)
                
                result_row = {
                    'Original_Text': text,
                    'Full_Address': extracted['full_address'],
                    'State': extracted['state'],
                    'District': extracted['district'],
                    'Pincode': extracted['pincode'],
                    'Phone_Numbers': ', '.join(extracted['phone_numbers']) if extracted['phone_numbers'] else None,
                    'Latitude': extracted['location_data']['latitude'] if extracted['location_data'] else None,
                    'Longitude': extracted['location_data']['longitude'] if extracted['location_data'] else None,
                    'Geocoded_Address': extracted['location_data']['display_name'] if extracted['location_data'] else None
                }
                results.append(result_row)
                
                progress_bar.progress((idx + 1) / len(df))
                time.sleep(1.5)
            
            status_text.text("Processing complete!")
            
            results_df = pd.DataFrame(results)
            st.success(f"Processed {len(results)} rows successfully!")
            st.dataframe(results_df)
            
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="extracted_addresses.csv",
                mime="text/csv"
            )

with tab3:
    st.subheader("Generate Complete Districts Database")
    st.info("""
    This will fetch latitude, longitude, and address information for all 787+ districts in India.
    
    ⚠️ **Important Notes:**
    - This process will take approximately **20-30 minutes** due to API rate limits
    - It will make ~787 API requests to OpenStreetMap Nominatim
    - Please be patient and do not refresh the page
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total States/UTs", len(INDIA_DISTRICTS))
    with col2:
        total_districts = sum(len(districts) for districts in INDIA_DISTRICTS.values())
        st.metric("Total Districts", total_districts)
    
    if st.button("🚀 Start Generating District Data", type="primary", key="generate_all"):
        st.warning("⏳ This will take 20-30 minutes. Please don't close this window.")
        
        start_time = time.time()
        all_districts_data = fetch_all_districts_data()
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        st.success(f"✅ Completed in {elapsed_time/60:.1f} minutes!")
        
        # Store in session state
        st.session_state['districts_data'] = all_districts_data
        
        # Display summary
        st.subheader("📊 Summary")
        total_successful = 0
        total_failed = 0
        
        for state, districts in all_districts_data.items():
            for district, data in districts.items():
                if data.get('latitude') is not None:
                    total_successful += 1
                else:
                    total_failed += 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Successful", total_successful)
        with col2:
            st.metric("❌ Failed", total_failed)
        with col3:
            success_rate = (total_successful / (total_successful + total_failed)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Preview data
        st.subheader("📋 Data Preview")
        
        # Convert to flat list for preview
        preview_data = []
        for state, districts in all_districts_data.items():
            for district, data in districts.items():
                preview_data.append({
                    'State': state,
                    'District': district,
                    'Latitude': data.get('latitude'),
                    'Longitude': data.get('longitude'),
                    'Display Name': data.get('display_name')
                })
        
        preview_df = pd.DataFrame(preview_data)
        st.dataframe(preview_df.head(20), use_container_width=True)
        
        # Download buttons
        st.subheader("💾 Download Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            json_str = json.dumps(all_districts_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name="india_districts_complete_data.json",
                mime="application/json",
                key="download_json"
            )
        
        with col2:
            # CSV download
            csv_data = preview_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name="india_districts_complete_data.csv",
                mime="text/csv",
                key="download_csv"
            )
        
        # Map visualization
        st.subheader("🗺️ Map Visualization")
        map_df = preview_df[preview_df['Latitude'].notna()][['Latitude', 'Longitude']].rename(
            columns={'Latitude': 'lat', 'Longitude': 'lon'}
        )
        if not map_df.empty:
            st.map(map_df, zoom=4)
    
    # If data exists in session state, show download buttons
    if 'districts_data' in st.session_state:
        st.divider()
        st.subheader("💾 Download Previously Generated Data")
        
        all_districts_data = st.session_state['districts_data']
        
        # Preview
        preview_data = []
        for state, districts in all_districts_data.items():
            for district, data in districts.items():
                preview_data.append({
                    'State': state,
                    'District': district,
                    'Latitude': data.get('latitude'),
                    'Longitude': data.get('longitude'),
                    'Display Name': data.get('display_name')
                })
        
        preview_df = pd.DataFrame(preview_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            json_str = json.dumps(all_districts_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download JSON (Hierarchical)",
                data=json_str,
                file_name="india_districts_complete_data.json",
                mime="application/json",
                key="download_json_saved"
            )
        
        with col2:
            csv_data = preview_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV (Flat)",
                data=csv_data,
                file_name="india_districts_complete_data.csv",
                mime="text/csv",
                key="download_csv_saved"
            )

# Sidebar
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    ### Features:
    - 🗺️ Uses OpenStreetMap Nominatim API
    - 📍 Extracts district, state, pincode
    - 📞 Finds phone numbers
    - 🌍 Gets latitude & longitude
    - 📊 Supports bulk CSV processing
    - 💾 Generate complete districts database
    
    ### Supported Districts:
    - All 787+ districts across India
    - 36 States and UTs covered
    
    ### Rate Limits:
    - 1 request per second for Nominatim API
    - Bulk operations may take time
    
    ### JSON Structure:
    ```json
    {
      "State Name": {
        "District Name": {
          "district": "...",
          "state": "...",
          "latitude": 12.34,
          "longitude": 56.78,
          "display_name": "...",
          "address": {...}
        }
      }
    }
    ```
    
    ### Tips:
    - Include district/state names for better results
    - Add pincode if available
    - More specific text = better geocoding
    - Use Tab 3 to generate complete database
    """)
    
    st.markdown("---")
    st.caption("Powered by OpenStreetMap Nominatim API")
    st.caption("⚠️ Please respect API usage policies")
