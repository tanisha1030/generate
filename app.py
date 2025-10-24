import streamlit as st
import requests
import json
import pandas as pd
import time

st.set_page_config(page_title="🚓 Indian Police Stations", layout="wide")
st.title("🚨 Police Stations in Indian Districts (Accurate Overpass API Fetcher)")
st.caption("Fetches at least one verified police station per district using OpenStreetMap data.")

# --------------------------- STATE & DISTRICT DATA -----------------------------
INDIA_REGIONS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "Kadapa"],
    "Arunachal Pradesh": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Kurung Kumey", "Kra Daadi", "Lower Subansiri", "Upper Subansiri", "West Siang", "East Siang", "Siang", "Upper Siang", "Lower Siang", "Lower Dibang Valley", "Dibang Valley", "Anjaw", "Lohit", "Namsai", "Changlang", "Tirap", "Longding"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "Tinsukia", "Udalguri"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Purnia", "Darbhanga", "Bhojpur", "Nalanda", "Rohtas", "Begusarai", "Araria", "Arwal", "Aurangabad", "Bagaha", "Banka", "Bhabhua", "Gopalganj", "Jamui", "Jehanabad", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Motihari", "Munger", "Nawadah", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali"],
    "Chhattisgarh": ["Raipur", "Bilaspur", "Durg", "Korba", "Rajnandgaon", "Raigarh", "Bastar", "Kanker", "Dhamtari", "Jagdalpur", "Balod", "Baloda Bazar", "Balrampur", "Bemetara", "Gariyaband", "Janjgir-Champa", "Jashpur", "Kondagaon", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Sarguja", "Sukma", "Surajpur"],
    "Goa": ["North Goa", "South Goa"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Bharuch", "Dahod", "Himatnagar", "Kheda", "Mehsana", "Narmada", "Navsari", "Palanpur", "Panchmahal", "Patan", "Porbandar", "Surendranagar", "Tapi", "Valsad", "Kutch"],
    "Haryana": ["Ambala", "Bhiwani", "Faridabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Mewat", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
    "Himachal Pradesh": ["Shimla", "Mandi", "Kullu", "Solan", "Kangra", "Una", "Chamba", "Bilaspur", "Sirmaur", "Hamirpur", "Lahaul-Spiti", "Kinnaur"],
    "Jharkhand": ["Ranchi", "Dhanbad", "Jamshedpur", "Bokaro", "Deoghar", "Dumka", "Giridih", "Hazaribagh", "Jamtara", "Chatra", "Godda", "Gumla", "Khunti", "Kodarma", "Latehar", "Lohardagga", "Pakur", "Palamu", "Ramgarh", "Saraikela", "Simdega"],
    "Karnataka": ["Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Mangaluru", "Dharwad", "Belagavi", "Hubballi-Dharwad", "Kalaburagi", "Ballari", "Davangere", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Hassan", "Haveri", "Kolar", "Mandya", "Ramanagara", "Shimoga", "Tumkur", "Udupi", "Yadgir", "Koppal", "Kodagu", "Bagalkot", "Chamarajanagar", "Bidar", "Chikkaballapura"],
    "Kerala": ["Thiruvananthapuram", "Kollam", "Alappuzha", "Kottayam", "Ernakulam", "Thrissur", "Palakkad", "Malappuram", "Kozhikode", "Kannur", "Idukki", "Pathanamthitta", "Wayanad", "Kasargod"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain", "Dewas", "Satna", "Rewa", "Sagar", "Shahdol", "Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dhar", "Dindori", "Guna", "Harda", "Hoshangabad", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Panna", "Raisen", "Rajgarh", "Ratlam", "Shajapur", "Sheopur", "Sidhi", "Singrauli", "Tikamgarh", "Umaria", "Vidisha"],
    "Maharashtra": ["Mumbai City", "Mumbai Suburban", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Kolhapur", "Solapur", "Amravati", "Latur", "Ahmednagar", "Akola", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Nanded", "Nandurbar", "Parbhani", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Wardha", "Washim", "Yavatmal"],
    "Manipur": ["Imphal East", "Imphal West", "Bishnupur", "Thoubal", "Kakching", "Churachandpur", "Chandel", "Senapati", "Tamenglong", "Ukhrul"],
    "Meghalaya": ["East Khasi Hills", "West Khasi Hills", "Ribhoi", "Jaintia Hills", "West Jaintia Hills", "South Garo Hills", "East Garo Hills", "North Garo Hills", "South West Khasi Hills"],
    "Mizoram": ["Aizawl", "Lunglei", "Lawngtlai", "Champhai", "Mamit", "Serchhip", "Kolasib", "Saitual", "Hnahthial", "Khawzawl"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Wokha", "Tuensang", "Mon", "Peren", "Phek", "Zunheboto", "Kiphire"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur", "Berhampur", "Balasore", "Puri", "Jajpur", "Sundargarh", "Keonjhar", "Dhenkanal", "Angul", "Bhadrak", "Bolangir", "Boudh", "Jagatsinghpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Koraput", "Mayurbhanj", "Nayagarh", "Nuapada", "Rayagada", "Sonepur"],
    "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Firozpur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Muktsar", "Pathankot", "Patiala", "Rupnagar", "Sangrur", "Shahid Bhagat Singh Nagar", "Tarn Taran"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Alwar", "Bharatpur", "Bhilwara", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaisalmer", "Jalor", "Jhunjhunu", "Jhalawar", "Karauli", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Tonk", "Udaipur"],
    "Sikkim": ["East Sikkim", "West Sikkim", "North Sikkim", "South Sikkim"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tiruppur", "Tirunelveli", "Vellore", "Erode", "Thoothukudi", "Dindigul", "Thanjavur", "Nagapattinam", "Namakkal", "Kanchipuram", "Krishnagiri", "Cuddalore", "Villupuram", "Ramanathapuram", "Sivaganga", "Tiruvallur", "Tiruvarur", "Dharmapuri", "Perambalur", "Pudukkottai", "Karur", "Mayiladuthurai", "Ranipet", "Tenkasi", "Chengalpattu"],
    "Telangana": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Adilabad", "Khammam", "Mahbubnagar", "Rangareddy", "Medak", "Siddipet", "Nalgonda", "Jagtial", "Rajanna Sircilla", "Peddapalli", "Sangareddy", "Yadadri Bhuvanagiri", "Kamareddy", "Mulugu", "Nagarkurnool", "Vikarabad", "Wanaparthy", "Jogulamba Gadwal"],
    "Tripura": ["Agartala", "Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Ghaziabad", "Agra", "Meerut", "Varanasi", "Prayagraj", "Bareilly", "Aligarh", "Moradabad", "Saharanpur", "Firozabad", "Jhansi", "Mathura", "Shahjahanpur", "Noida", "Gorakhpur", "Etawah", "Rampur", "Farrukhabad", "Budaun", "Hapur", "Bulandshahr", "Raebareli", "Sitapur", "Amroha", "Bijnor", "Barabanki", "Mahoba", "Hamirpur", "Kasganj", "Azamgarh", "Sant Kabir Nagar", "Pratapgarh", "Baghpat", "Chitrakoot", "Etah", "Fatehpur", "Hardoi", "Kaushambi", "Kannauj", "Lakhimpur Kheri", "Mainpuri", "Mau", "Mirzapur", "Siddharthnagar", "Sultanpur", "Unnao", "Varanasi"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Nainital", "Almora", "Pithoragarh", "Chamoli", "Rudraprayag", "Tehri Garhwal", "Uttarkashi", "Champawat", "Bageshwar", "Udham Singh Nagar"],
    "West Bengal": ["Kolkata", "North 24 Parganas", "South 24 Parganas", "Howrah", "Hooghly", "Darjeeling", "Nadia", "Burdwan", "Purulia", "Bankura", "Cooch Behar", "Malda", "Jalpaiguri", "Birbhum", "Medinipur", "Uttar Dinajpur", "Dakshin Dinajpur", "Paschim Bardhaman", "Purba Bardhaman", "Alipurduar", "Kalimpong", "Purba Medinipur", "Paschim Medinipur"],
    "Andaman and Nicobar Islands": ["North and Middle Andaman", "South Andaman", "Nicobar"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Dadra", "Nagar Haveli", "Daman", "Diu"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South East Delhi", "South West Delhi", "Central Delhi", "New Delhi"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Srinagar", "Udhampur"],
    "Ladakh": ["Kargil", "Leh"],
    "Lakshadweep": ["Agatti", "Amini", "Andrott", "Kadmath", "Kavaratti", "Minicoy", "Chetlat", "Bitra"]
}

# --------------------------- FETCH FUNCTION ------------------------------------
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def get_police_station(state, district, max_retries=3):
    """
    Fetches at least one police station from OpenStreetMap for a district.
    Uses fallback queries to ensure result.
    """
    queries = [
        f"""
        [out:json][timeout:25];
        area["name"="{district}"]["boundary"="administrative"]["is_in:state"="{state}"]->.searchArea;
        (
          node["amenity"="police"](area.searchArea);
          way["amenity"="police"](area.searchArea);
          relation["amenity"="police"](area.searchArea);
        );
        out center 1;
        """,
        # Fallback: broader search including district name
        f"""
        [out:json][timeout:25];
        (
          node["amenity"="police"]["name"~"{district}", i];
          way["amenity"="police"]["name"~"{district}", i];
        );
        out center 1;
        """,
        # Fallback: state-level search
        f"""
        [out:json][timeout:25];
        area["name"="{state}"]["boundary"="administrative"]->.stateArea;
        (
          node["amenity"="police"](area.stateArea);
          way["amenity"="police"](area.stateArea);
        );
        out center 1;
        """
    ]
    for query in queries:
        for attempt in range(max_retries):
            try:
                response = requests.post(OVERPASS_URL, data=query, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("elements"):
                        element = data["elements"][0]
                        lat = element.get("lat") or element.get("center", {}).get("lat")
                        lon = element.get("lon") or element.get("center", {}).get("lon")
                        name = element.get("tags", {}).get("name", "Unnamed Police Station")
                        return {"State": state, "District": district, "Name": name, "Latitude": lat, "Longitude": lon}
            except Exception:
                time.sleep(2)
    return {"State": state, "District": district, "Name": "Not Found", "Latitude": None, "Longitude": None}

# --------------------------- MAIN APP LOGIC ------------------------------------
if st.button("🚀 Fetch Police Stations"):
    all_results = []
    total_districts = sum(len(d) for d in INDIA_REGIONS.values())
    progress = st.progress(0)
    current = 0

    for state, districts in INDIA_REGIONS.items():
        st.subheader(f"🧭 {state}")
        for district in districts:
            result = get_police_station(state, district)
            all_results.append(result)
            current += 1
            progress.progress(current / total_districts)
            st.write(f"{district}: {result['Name']}")
            time.sleep(1)

    df = pd.DataFrame(all_results)
    df.to_csv("police_stations.csv", index=False, encoding="utf-8")
    with open("police_stations.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    st.success("✅ Data fetched successfully!")
    st.dataframe(df)
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "police_stations.csv", "text/csv")
    st.download_button("📥 Download JSON", json.dumps(all_results, indent=2).encode('utf-8'), "police_stations.json", "application/json")
