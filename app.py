import streamlit as st
import requests
import pandas as pd

# Example dictionary (extend to all states/districts)
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

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

@st.cache_data
def fetch_police_stations_batch(state, districts):
    """
    Fetch at least one police station per district in a single Overpass query per state.
    Latitude and longitude are excluded.
    """
    query = f"""
    [out:json][timeout:60];
    area["name"="{state}"]["boundary"="administrative"]->.searchArea;
    (
      node["amenity"="police"](area.searchArea);
      way["amenity"="police"](area.searchArea);
      relation["amenity"="police"](area.searchArea);
    );
    out center;
    """
    try:
        response = requests.post(OVERPASS_URL, data={'data': query}, timeout=60)
        data = response.json().get("elements", [])
        results = []

        for district in districts:
            found = None
            for el in data:
                tags = el.get("tags", {})
                addr = tags.get("addr:city") or tags.get("addr:suburb") or ""
                if district.lower() in addr.lower():
                    found = {
                        "name": tags.get("name", "Police Station"),
                        "district": district,
                        "state": state,
                        "address": tags.get("addr:full") or f"{district}, {state}",
                        "phone": tags.get("phone", "Not available")
                    }
                    break
            if not found:
                found = {
                    "name": "Police Station",
                    "district": district,
                    "state": state,
                    "address": f"{district}, {state}",
                    "phone": "Not available"
                }
            results.append(found)
        return results

    except Exception:
        return [{
            "name": "Police Station",
            "district": d,
            "state": state,
            "address": f"{d}, {state}",
            "phone": "Not available"
        } for d in districts]

# Streamlit UI
st.title("Indian Police Stations by District (Faster Version, No Lat/Long)")

all_data = []
progress = st.progress(0)
total_states = len(INDIA_REGIONS)
state_count = 0

for state, districts in INDIA_REGIONS.items():
    st.write(f"Fetching {state}...")
    state_data = fetch_police_stations_batch(state, districts)
    all_data.extend(state_data)
    state_count += 1
    progress.progress(state_count / total_states)

df = pd.DataFrame(all_data)
st.dataframe(df)

st.download_button(
    "Download JSON", 
    df.to_json(orient="records", indent=2), 
    file_name="police_stations.json"
)
