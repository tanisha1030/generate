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
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Alwar", "Bharatpur", "Bhilwara", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaisalmer", "Jalor", "Jhunjhunu", "Jhalawar", "Karauli", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Tonk"],
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
  "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South East Delhi", "South West Delhi", "Central Delhi"],
  "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Budgam", "Doda", "Ganderbal", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Udhampur"],
  "Ladakh": ["Kargil", "Leh"],
  "Lakshadweep": ["Agatti", "Amini", "Andrott", "Kadmath", "Kavaratti", "Minicoy", "Chetlat", "Bitra"]
}
  
 


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
