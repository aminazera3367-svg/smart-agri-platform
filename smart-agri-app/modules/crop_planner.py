from __future__ import annotations

import streamlit as st


LOCATION_ZONES = [
    {"name": "Semi-Arid Plateau", "lat_min": 12, "lat_max": 18.5, "lon_min": 75, "lon_max": 80.5, "soil": "Black", "climate": "Semi-arid", "crops": ["Groundnut", "Millet", "Chili"]},
    {"name": "Indo-Gangetic Plain", "lat_min": 24, "lat_max": 31, "lon_min": 77, "lon_max": 88, "soil": "Loamy", "climate": "Sub-tropical", "crops": ["Rice", "Onion", "Beans"]},
    {"name": "Coastal Humid Belt", "lat_min": 10, "lat_max": 19, "lon_min": 80, "lon_max": 88.5, "soil": "Clay", "climate": "Humid coastal", "crops": ["Rice", "Beans", "Tomato"]},
]

PROFILE_SCALE = {
    "Protective / Conservative": {"cost_bias": 0.88},
    "Growing / Balanced": {"cost_bias": 1.0},
    "Expansion / Aggressive": {"cost_bias": 1.12},
}


@st.cache_data(ttl=86400)
def recommend_crop_by_location(lat: float, lon: float) -> dict:
    for zone in LOCATION_ZONES:
        if zone["lat_min"] <= lat <= zone["lat_max"] and zone["lon_min"] <= lon <= zone["lon_max"]:
            return {
                "soil_type": zone["soil"],
                "climate_zone": zone["climate"],
                "suitable_crops": zone["crops"],
                "reason": f"Coordinates ({lat:.2f}, {lon:.2f}) align with the {zone['name']} profile where {zone['soil'].lower()} soils and {zone['climate'].lower()} conditions are common.",
            }
    fallback = "Loamy" if lat > 20 else "Red"
    crops = ["Millet", "Groundnut", "Beans"] if lon < 80 else ["Rice", "Tomato", "Beans"]
    return {
        "soil_type": fallback,
        "climate_zone": "Tropical transition",
        "suitable_crops": crops,
        "reason": f"Coordinates ({lat:.2f}, {lon:.2f}) fall outside the predefined zones, so the planner uses a regional transition profile.",
    }


def get_crop_plan(soil: str, water: str, budget: float, farmer_profile: str, location_hint: dict | None = None) -> list[dict]:
    location_crops = set(location_hint["suitable_crops"]) if location_hint else set()
    candidates = [
        {"crop": "Millet", "water_need": "Low", "soil_match": {"Sandy", "Red", "Black"}, "profit": "Medium", "risk": "Low"},
        {"crop": "Groundnut", "water_need": "Low", "soil_match": {"Sandy", "Black", "Loamy"}, "profit": "High", "risk": "Medium"},
        {"crop": "Rice", "water_need": "High", "soil_match": {"Clay", "Loamy"}, "profit": "High", "risk": "Medium"},
        {"crop": "Beans", "water_need": "Medium", "soil_match": {"Loamy", "Clay", "Red"}, "profit": "Medium", "risk": "Low"},
        {"crop": "Tomato", "water_need": "Medium", "soil_match": {"Loamy", "Red"}, "profit": "High", "risk": "Medium"},
        {"crop": "Onion", "water_need": "Medium", "soil_match": {"Loamy", "Black"}, "profit": "High", "risk": "Medium"},
        {"crop": "Chili", "water_need": "Medium", "soil_match": {"Black", "Red"}, "profit": "High", "risk": "High"},
    ]
    results = []
    cost_bias = PROFILE_SCALE.get(farmer_profile, PROFILE_SCALE["Growing / Balanced"])["cost_bias"]
    for item in candidates:
        score = 0
        reasons = []
        if soil in item["soil_match"]:
            score += 3
            reasons.append(f"{soil} soil is a good agronomic fit.")
        if item["water_need"] == water:
            score += 3
            reasons.append(f"{water} water availability suits the crop's irrigation demand.")
        budget_threshold = 1400 if item["crop"] in {"Tomato", "Chili", "Onion"} else 700
        if budget * cost_bias >= budget_threshold:
            score += 2
            reasons.append("Budget can support seed, nutrient, and crop care costs.")
        if item["crop"] in location_crops:
            score += 2
            reasons.append("Location intelligence indicates local climatic suitability.")
        results.append(
            {
                "crop": item["crop"],
                "risk": item["risk"],
                "profit": item["profit"],
                "score": score,
                "reasons": reasons or ["This crop remains a neutral backup option."],
                "water_strategy": "Low irrigation discipline" if item["water_need"] == "Low" else "Scheduled irrigation monitoring",
                "fertilizer_plan": "Split nitrogen application with one basal dose and one top dressing.",
            }
        )
    results.sort(key=lambda row: (-row["score"], row["risk"]))
    return results[:3]


def simulate_agronomy_scenario(
    soil_moisture: float,
    soil_ph: float,
    nitrogen_level: float,
    temperature: float,
    humidity: float,
    region: str,
    farmer_profile: str,
    location_hint: dict | None = None,
) -> dict:
    crop = "Millet"
    if nitrogen_level < 30 and soil_moisture < 38:
        crop = "Groundnut"
    elif soil_moisture > 65 and humidity > 75:
        crop = "Rice"
    elif 6.0 <= soil_ph <= 7.2 and 24 <= temperature <= 33:
        crop = "Maize"
    if location_hint and location_hint["suitable_crops"] and crop not in location_hint["suitable_crops"]:
        crop = location_hint["suitable_crops"][0]

    yield_index = round(
        max(
            25,
            min(
                95,
                0.45 * soil_moisture
                + 0.65 * nitrogen_level
                + (20 - abs(temperature - 28)) * 2
                + (12 - abs(soil_ph - 6.8)) * 3,
            ),
        ),
        1,
    )
    return {
        "crop": crop,
        "fertilizer": f"Recommended nitrogen dose: {max(18, int(55 - nitrogen_level * 0.4))} kg/acre",
        "irrigation": "Short interval irrigation" if soil_moisture < 35 else "Moisture is adequate; avoid over-irrigation",
        "yield_index": yield_index,
        "reason": (
            f"Soil moisture {soil_moisture}%, pH {soil_ph}, nitrogen {nitrogen_level}, "
            f"temperature {temperature}°C, and humidity {humidity}% align most closely with {crop}."
        ),
    }
