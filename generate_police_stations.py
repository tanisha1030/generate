# generate_police_stations.py
import streamlit as st
import geopandas as gpd
import requests
import json
import time
import io
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

st.set_page_config(page_title="Police Station JSON Generator (OSM)", layout="wide")
st.title("🚓 Police Station JSON Generator (from OpenStreetMap)")
st.markdown("""
Upload an **India district GeoJSON** (same as used in your main project),  
and this app will query [OpenStreetMap (Overpass API)](https://overpass-api.de/)  
to collect **real police stations** for each district and export a JSON file.
""")

# --- Helper functions ---
def normalize_name(s):
    if s is None:
        return ""
    s = str(s).lower()
    for old, new in {
        'commr': 'commissioner',
        'commissionerate': 'commissioner',
        'dist': 'district',
        'district.': 'district',
        ' (rural)': '',
        ' (urban)': ''
    }.items():
        s = s.replace(old, new)
    s = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in s)
    s = " ".join(s.split())
    return s

def polygon_to_polystring(poly: Polygon):
    coords = []
    for x, y in poly.exterior.coords:
        coords.append(f"{y} {x}")
    return " ".join(coords)

def try_polystring(geom, simplify_tol=0.001, max_points=800):
    if isinstance(geom, MultiPolygon):
        geom = unary_union(geom)
    if not geom.is_valid:
        geom = geom.buffer(0)
    pts = len(geom.exterior.coords)
    if pts <= max_points:
        return polygon_to_polystring(geom)
    for tol in [simplify_tol, simplify_tol * 2, simplify_tol * 5]:
        simple = geom.simplify(tol, preserve_topology=True)
        if len(simple.exterior.coords) <= max_points:
            return polygon_to_polystring(simple)
    return None

def query_overpass(poly_str):
    query = f"""
    [out:json][timeout:120];
    (
      node["amenity"="police"](poly:"{poly_str}");
      way["amenity"="police"](poly:"{poly_str}");
      relation["amenity"="police"](poly:"{poly_str}");
    );
    out center tags;
    """
    url = "https://overpass-api.de/api/interpreter"
    r = requests.post(url, data={"data": query}, timeout=180)
    r.raise_for_status()
    return r.json()

def elem_to_station(elem):
    tags = elem.get("tags", {})
    name = tags.get("name") or "Police Station"
    phone = tags.get("phone") or tags.get("contact:phone") or ""
    addr_parts = []
    for k in ["addr:street", "addr:suburb", "addr:city", "addr:state"]:
        if k in tags and tags[k]:
            addr_parts.append(tags[k])
    address = ", ".join(addr_parts)
    lat, lon = None, None
    if "lat" in elem:
        lat, lon = elem["lat"], elem["lon"]
    elif "center" in elem:
        lat, lon = elem["center"]["lat"], elem["center"]["lon"]
    return {
        "name": name,
        "address": address,
        "phone": phone,
        "lat": lat,
        "lon": lon
    }

# --- Streamlit UI ---
uploaded_geojson = st.file_uploader("📁 Upload district-level GeoJSON", type=["geojson", "json"])

if uploaded_geojson is not None:
    gdf = gpd.read_file(uploaded_geojson)
    # Try to find name column
    name_col = None
    for c in ["NAME_2", "NAME", "district", "DISTRICT", "name"]:
        if c in gdf.columns:
            name_col = c
            break
    if name_col is None:
        name_col = gdf.columns[0]

    st.success(f"✅ Loaded {len(gdf)} districts using column '{name_col}'")

    if st.button("🔍 Generate Police Stations JSON (from OSM)"):
        results = {}
        progress = st.progress(0)
        total = len(gdf)
        overpass_errors = 0

        for i, row in enumerate(gdf.itertuples(), 1):
            district_raw = getattr(row, name_col)
            district_norm = normalize_name(district_raw)
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue

            poly_str = try_polystring(geom)
            if not poly_str:
                continue

            try:
                data = query_overpass(poly_str)
                elems = data.get("elements", [])
                stations = [elem_to_station(e) for e in elems if e.get("tags")]
                results[district_norm] = stations
            except Exception as e:
                overpass_errors += 1
                results[district_norm] = []
            progress.progress(i / total)
            time.sleep(1.0)  # polite delay

        st.success(f"✅ Completed! {len(results)} districts processed, {overpass_errors} Overpass errors.")

        # Download JSON
        json_bytes = io.BytesIO(json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8"))
        st.download_button(
            "⬇️ Download police_stations.json",
            data=json_bytes,
            file_name="police_stations.json",
            mime="application/json"
        )

        st.json({k: results[k] for k in list(results.keys())[:3]})  # preview first 3 districts
else:
    st.info("Upload your GeoJSON to start.")
