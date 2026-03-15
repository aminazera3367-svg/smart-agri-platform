from __future__ import annotations

from datetime import datetime

import requests
import streamlit as st

from .config import get_config_value


REGION_TO_LOCATION = {
    "Central Valley": "Hyderabad,IN",
    "North Belt": "Lucknow,IN",
    "South Plains": "Bengaluru,IN",
    "Coastal Delta": "Visakhapatnam,IN",
}


WEATHER_FALLBACK = {
    1: {"temperature": 24, "humidity": 58, "description": "clear winter morning", "rainfall_probability": 8},
    2: {"temperature": 27, "humidity": 54, "description": "dry and mild", "rainfall_probability": 10},
    3: {"temperature": 31, "humidity": 48, "description": "warming pre-monsoon conditions", "rainfall_probability": 12},
    4: {"temperature": 34, "humidity": 42, "description": "hot and dry", "rainfall_probability": 16},
    5: {"temperature": 36, "humidity": 46, "description": "hot with scattered cloud build-up", "rainfall_probability": 22},
    6: {"temperature": 32, "humidity": 66, "description": "monsoon onset conditions", "rainfall_probability": 48},
    7: {"temperature": 29, "humidity": 78, "description": "active monsoon pattern", "rainfall_probability": 72},
    8: {"temperature": 28, "humidity": 82, "description": "humid with recurrent rain bands", "rainfall_probability": 76},
    9: {"temperature": 29, "humidity": 79, "description": "wet and cloudy", "rainfall_probability": 68},
    10: {"temperature": 28, "humidity": 70, "description": "retreating monsoon conditions", "rainfall_probability": 36},
    11: {"temperature": 26, "humidity": 62, "description": "mild with isolated showers", "rainfall_probability": 20},
    12: {"temperature": 23, "humidity": 60, "description": "cool and stable", "rainfall_probability": 10},
}


@st.cache_data(ttl=1800)
def get_real_weather(location: str) -> dict:
    api_key = get_config_value("OPENWEATHERMAP_API_KEY")
    mapped_location = REGION_TO_LOCATION.get(location, location)
    fallback = WEATHER_FALLBACK[datetime.now().month].copy()
    fallback["source"] = "Local seasonal fallback"

    if not api_key:
        return fallback

    try:
        current = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": mapped_location, "appid": api_key, "units": "metric"},
            timeout=8,
        )
        current.raise_for_status()
        current_json = current.json()
        forecast = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": current_json["coord"]["lat"],
                "lon": current_json["coord"]["lon"],
                "appid": api_key,
                "units": "metric",
            },
            timeout=8,
        )
        forecast.raise_for_status()
        forecast_json = forecast.json()
        rain_probability = 0
        for item in forecast_json.get("list", [])[:8]:
            rain_probability = max(rain_probability, int(round(item.get("pop", 0) * 100)))
        return {
            "temperature": round(current_json["main"]["temp"], 1),
            "humidity": int(current_json["main"]["humidity"]),
            "description": current_json["weather"][0]["description"].title(),
            "rainfall_probability": rain_probability,
            "source": "OpenWeatherMap",
        }
    except Exception:
        return fallback
