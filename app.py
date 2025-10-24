import requests
import json
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# =============================
# 1️⃣ Your full state-district data
# =============================
INDIA_REGIONS = {
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "Kadapa"],
    "Arunachal Pradesh": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Kurung Kumey", "Kra Daadi", "Lower Subansiri", "Upper Subansiri", "West Siang", "East Siang", "Siang", "Upper Siang", "Lower Siang", "Lower Dibang Valley", "Dibang Valley", "Anjaw", "Lohit", "Namsai", "Changlang", "Tirap", "Longding"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Goalpara", "Golaghat", "Hailakandi", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "Tinsukia", "Udalguri"],
}

# =============================
# 2️⃣ Function to query Overpass
# =============================
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def get_police_station(state, district):
    """
    Try to fetch at least one police station in a district using Overpass API
    """
    queries = [
        f"""
        [out:json][timeout:20];
        area["name"="{state}"]->.state;
        area["name"="{district}"]->.district;
        node["amenity"="police"](area.district);
        out 1;
        """,
        f"""
        [out:json][timeout:20];
        node["amenity"="police"]["addr:district"="{district}"](area);
        out 1;
        """,
        f"""
        [out:json][timeout:20];
        node["amenity"="police"](if:is_in("{district}", "{state}"));
        out 1;
        """,
        f"""
        [out:json][timeout:20];
        node["amenity"="police"]["name"~"{district}",i];
        out 1;
        """
    ]
    
    for query in queries:
        try:
            res = requests.post(OVERPASS_URL, data={"data": query}, timeout=25)
            data = res.json()
            if "elements" in data and len(data["elements"]) > 0:
                el = data["elements"][0]
                return {
                    "state": state,
                    "district": district,
                    "name": el.get("tags", {}).get("name", "Unnamed Station"),
                    "lat": el.get("lat"),
                    "lon": el.get("lon")
                }
        except Exception:
            continue
    return {"state": state, "district": district, "name": None, "lat": None, "lon": None}

# =============================
# 3️⃣ Parallel fetcher
# =============================
def fetch_all_police_stations(max_workers=15):
    results = []
    futures = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for state, districts in INDIA_REGIONS.items():
            for district in districts:
                futures.append(executor.submit(get_police_station, state, district))

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if result["name"]:
                print(f"✅ {result['district']}, {result['state']} → {result['name']}")
            else:
                print(f"❌ {result['district']}, {result['state']} → Not found")

    return results

# =============================
# 4️⃣ Run and save results
# =============================
if __name__ == "__main__":
    print("Fetching police station data for all districts in India...")
    start = time.time()
    all_results = fetch_all_police_stations()
    print(f"\nDone in {round(time.time()-start, 2)} seconds")

    # Save as JSON
    with open("police_stations.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # Save as CSV
    with open("police_stations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["state", "district", "name", "lat", "lon"])
        writer.writeheader()
        writer.writerows(all_results)

    print("\n✅ Saved results to police_stations.json and police_stations.csv")
