"""
generate_city_expansion.py — One-off script that expands PropValuate AI's
city coverage from the original 10 trained cities to a much larger list of
Tier 1 / Tier 2 / Tier 3 Indian cities, as requested.

IMPORTANT — what this does and doesn't do:
The XGBoost model was only ever trained on real transaction data for the
original 10 cities. There is no real transaction data for the ~60 new
cities added here, so this script does NOT invent fake "real" data and
pass it off as ground truth. Instead:

  1. Each new city is assigned a tier (1/2/3) and, for MODEL PREDICTION
     PURPOSES ONLY, is mapped to a "proxy" reference city from the original
     10 that best represents its tier (Mumbai for Tier 1, Coimbatore for
     Tier 2, Madurai for Tier 3). The model's `location_c` feature for a
     new city reuses its proxy's code, so the model doesn't extrapolate
     into a categorical code it never saw during training.
  2. The features that actually carry most of the location signal into the
     model — demand_index, local_market_index, location_convenience_score,
     and the five distance-to-facility features — are generated per
     sub-locality from tier-calibrated ranges (calibrated against the
     min/max actually observed across the 10 real cities), with a
     deterministic per-sub-locality seed so results are reproducible.
  3. Every synthetic sub-locality is flagged `"estimated": true` in
     sub_stats.json, exactly like the existing "not enough sampled
     listings" mechanism the app already had — the UI already renders a
     note for this case, so no frontend work was needed there.

Run once:
    python3 generate_city_expansion.py
It rewrites data/meta.json, data/sub_stats.json, and data/heatmap.json.
"""
import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------- Tier lists
TIER1_RAW = ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"]
TIER2_RAW = [
    "Coimbatore", "Madurai", "Tiruchirappalli (Trichy)", "Salem", "Tirunelveli", "Vellore", "Erode",
    "Thanjavur", "Kochi", "Thiruvananthapuram", "Kozhikode", "Jaipur", "Lucknow", "Kanpur", "Indore",
    "Bhopal", "Chandigarh", "Bhubaneswar", "Surat", "Vadodara", "Visakhapatnam", "Vijayawada", "Mysuru",
    "Mangaluru", "Hubballi–Dharwad", "Nagpur", "Nashik", "Aurangabad", "Jodhpur", "Udaipur", "Gwalior",
    "Raipur", "Dehradun", "Jammu", "Guwahati",
]
TIER3_RAW = [
    "Dindigul", "Karur", "Namakkal", "Kumbakonam", "Sivakasi", "Virudhunagar", "Nagercoil", "Cuddalore",
    "Karaikudi", "Pollachi", "Hosur", "Pudukkottai", "Rajahmundry", "Kakinada", "Nellore", "Guntur",
    "Warangal", "Roorkee", "Haridwar", "Aligarh", "Bareilly", "Gorakhpur", "Ajmer", "Bikaner", "Kolhapur",
    "Solapur", "Belagavi", "Davanagere", "Udupi", "Siliguri",
]

# Names that map onto a city already present in the trained dataset (avoid duplicates)
NAME_ALIAS = {
    "Delhi": "Delhi NCR",
    "Tiruchirappalli (Trichy)": "Tiruchirappalli",
}

# Approximate city-centre coordinates for the new cities (existing 10 already
# have precise per-sub-locality coordinates in sub_stats.json)
COORDS = {
    "Kolkata": (22.5726, 88.3639),
    "Tiruchirappalli": (10.7905, 78.7047), "Salem": (11.6643, 78.1460),
    "Tirunelveli": (8.7139, 77.7567), "Vellore": (12.9165, 79.1325),
    "Erode": (11.3410, 77.7172), "Thanjavur": (10.7870, 79.1378),
    "Thiruvananthapuram": (8.5241, 76.9366), "Kozhikode": (11.2588, 75.7804),
    "Jaipur": (26.9124, 75.7873), "Lucknow": (26.8467, 80.9462),
    "Kanpur": (26.4499, 80.3319), "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126), "Chandigarh": (30.7333, 76.7794),
    "Bhubaneswar": (20.2961, 85.8245), "Surat": (21.1702, 72.8311),
    "Vadodara": (22.3072, 73.1812), "Visakhapatnam": (17.6868, 83.2185),
    "Vijayawada": (16.5062, 80.6480), "Mysuru": (12.2958, 76.6394),
    "Mangaluru": (12.9141, 74.8560), "Hubballi–Dharwad": (15.3647, 75.1240),
    "Nagpur": (21.1458, 79.0882), "Nashik": (19.9975, 73.7898),
    "Aurangabad": (19.8762, 75.3433), "Jodhpur": (26.2389, 73.0243),
    "Udaipur": (24.5854, 73.7125), "Gwalior": (26.2183, 78.1828),
    "Raipur": (21.2514, 81.6296), "Dehradun": (30.3165, 78.0322),
    "Jammu": (32.7266, 74.8570), "Guwahati": (26.1445, 91.7362),
    "Dindigul": (10.3624, 77.9695), "Karur": (10.9601, 78.0766),
    "Namakkal": (11.2189, 78.1674), "Kumbakonam": (10.9601, 79.3788),
    "Sivakasi": (9.4491, 77.7972), "Virudhunagar": (9.5851, 77.9573),
    "Nagercoil": (8.1790, 77.4338), "Cuddalore": (11.7480, 79.7714),
    "Karaikudi": (10.0733, 78.7817), "Pollachi": (10.6588, 77.0084),
    "Hosur": (12.7409, 77.8253), "Pudukkottai": (10.3833, 78.8001),
    "Rajahmundry": (17.0005, 81.8040), "Kakinada": (16.9891, 82.2475),
    "Nellore": (14.4426, 79.9865), "Guntur": (16.3067, 80.4365),
    "Warangal": (17.9689, 79.5941), "Roorkee": (29.8543, 77.8880),
    "Haridwar": (29.9457, 78.1642), "Aligarh": (27.8974, 78.0880),
    "Bareilly": (28.3670, 79.4304), "Gorakhpur": (26.7606, 83.3732),
    "Ajmer": (26.4499, 74.6399), "Bikaner": (28.0229, 73.3119),
    "Kolhapur": (16.7050, 74.2433), "Solapur": (17.6599, 75.9064),
    "Belagavi": (15.8497, 74.4977), "Davanagere": (14.4644, 75.9218),
    "Udupi": (13.3409, 74.7421), "Siliguri": (26.7271, 88.3953),
}

# Tier-calibrated ranges, min/max drawn from what's actually observed across
# the 10 real trained cities in sub_stats.json (see README for the numbers).
TIER_RANGES = {
    1: dict(psf=(950, 1550), demand=(55, 92), conv=(40, 63), lmi=(115, 190),
            dist=(0.7, 2.3), zones=["Stable", "Moderate Growth"]),
    2: dict(psf=(620, 1250), demand=(28, 50), conv=(28, 50), lmi=(80, 105),
            dist=(1.2, 3.0), zones=["Moderate Growth", "High Growth"]),
    3: dict(psf=(320, 650), demand=(12, 30), conv=(15, 35), lmi=(55, 80),
            dist=(1.8, 4.2), zones=["High Growth", "Moderate Growth"]),
}

REFERENCE_CITY_BY_TIER = {1: "Mumbai", 2: "Coimbatore", 3: "Madurai"}

SUB_NAME_POOL = [
    "City Centre", "Civil Lines", "New Town", "Model Colony", "Railway Colony",
    "Industrial Area", "College Road", "Ring Road", "Old Town", "Green Park",
]

FACILITY_NAMES = {
    "school": "{city} Public School", "hospital": "{city} General Hospital",
    "supermarket": "{city} Central Mart", "transit": "{city} Railway Station",
    "park": "{city} City Park",
}


def build_new_city_list():
    """Returns [(canonical_name, tier), ...] for cities not already in the dataset."""
    existing = set(json.loads((DATA_DIR / "meta.json").read_text())["locations"])
    out = []
    for tier, raw_list in ((1, TIER1_RAW), (2, TIER2_RAW), (3, TIER3_RAW)):
        for raw in raw_list:
            name = NAME_ALIAS.get(raw, raw)
            if name in existing or any(name == n for n, _ in out):
                continue
            out.append((name, tier))
    return out


def gen_sub_locality(city: str, tier: int, sub_name: str, idx: int):
    rng = random.Random(f"{city}|{sub_name}|{idx}")
    r = TIER_RANGES[tier]
    lat0, lon0 = COORDS[city]
    psf = rng.uniform(*r["psf"])
    return {
        "latitude": lat0 + rng.uniform(-0.05, 0.05),
        "longitude": lon0 + rng.uniform(-0.05, 0.05),
        "local_market_index": rng.uniform(*r["lmi"]),
        "demand_index": rng.uniform(*r["demand"]),
        "price_per_sqft": psf,
        "distance_to_school_km": rng.uniform(*r["dist"]),
        "distance_to_hospital_km": rng.uniform(*r["dist"]),
        "distance_to_supermarket_km": rng.uniform(r["dist"][0] * 0.7, r["dist"][1] * 0.8),
        "distance_to_transit_km": rng.uniform(*r["dist"]),
        "distance_to_park_km": rng.uniform(r["dist"][0], r["dist"][1] * 1.1),
        "location_convenience_score": rng.uniform(*r["conv"]),
        "growth_rate_zone": rng.choice(r["zones"]),
        "nearest_school": FACILITY_NAMES["school"].format(city=city),
        "nearest_hospital": FACILITY_NAMES["hospital"].format(city=city),
        "nearest_supermarket": FACILITY_NAMES["supermarket"].format(city=city),
        "nearest_transit_station": FACILITY_NAMES["transit"].format(city=city),
        "nearest_park": FACILITY_NAMES["park"].format(city=city),
        "sample_size": 0,
        "nearest_property_km": round(rng.uniform(2.0, 6.0), 2),
        "estimated": True,  # no real sampled listings — flagged, same as the app's existing pattern
        "location": city,
        "sublocality": sub_name,
    }


def main():
    meta = json.loads((DATA_DIR / "meta.json").read_text())
    sub_stats = json.loads((DATA_DIR / "sub_stats.json").read_text())
    heatmap = json.loads((DATA_DIR / "heatmap.json").read_text())

    new_cities = build_new_city_list()
    print(f"Adding {len(new_cities)} new cities...")

    city_tier = {c: 1 for c in meta["locations"]}  # existing 10 are all metro-scale; treat as Tier 1
    # ...except the existing ones that are genuinely Tier 2 in the source lists:
    for c in ("Coimbatore", "Kochi", "Madurai"):
        if c in city_tier:
            city_tier[c] = 2

    for city, tier in new_cities:
        city_tier[city] = tier
        meta["locations"].append(city)
        meta["loc_map"][city] = meta["loc_map"][REFERENCE_CITY_BY_TIER[tier]]  # proxy code, see module docstring
        meta["city_ptypes"][city] = ["Apartment", "Independent House"] if tier == 3 else meta["ptypes"]

        subs = {}
        n_subs = 5 if tier == 1 else 4
        pool = SUB_NAME_POOL[:]
        random.Random(city).shuffle(pool)
        for i, sub_name in enumerate(pool[:n_subs]):
            subs[sub_name] = gen_sub_locality(city, tier, sub_name, i)
        sub_stats[city] = subs

        for sub_name, s in subs.items():
            heatmap.append({
                "location": city, "sublocality": sub_name,
                "latitude": s["latitude"], "longitude": s["longitude"],
                "price_per_sqft": s["price_per_sqft"], "demand_index": s["demand_index"],
                "growth_rate_zone": s["growth_rate_zone"],
            })

    meta["locations"] = sorted(meta["locations"])
    meta["city_tier"] = city_tier

    (DATA_DIR / "meta.json").write_text(json.dumps(meta))
    (DATA_DIR / "sub_stats.json").write_text(json.dumps(sub_stats))
    (DATA_DIR / "heatmap.json").write_text(json.dumps(heatmap))
    print(f"Done. Total cities: {len(meta['locations'])}. Total heatmap points: {len(heatmap)}.")


if __name__ == "__main__":
    main()
