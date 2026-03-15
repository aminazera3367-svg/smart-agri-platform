from __future__ import annotations

import os
from pathlib import Path

import streamlit as st


APP_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = APP_ROOT / ".env"


def _load_dotenv() -> None:
    if os.environ.get("SMART_AGRI_DOTENV_LOADED") == "1":
        return
    os.environ["SMART_AGRI_DOTENV_LOADED"] = "1"

    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def get_config_value(name: str, default: str = "") -> str:
    _load_dotenv()

    try:
        secret_value = st.secrets.get(name)
    except Exception:
        secret_value = None

    if secret_value is not None:
        return str(secret_value).strip()

    return os.getenv(name, default).strip()


def get_service_status() -> dict[str, dict[str, str | bool]]:
    weather_key = get_config_value("OPENWEATHERMAP_API_KEY")
    mandi_key = get_config_value("DATA_GOV_API_KEY")
    mandi_resource = get_config_value("MANDI_RESOURCE_ID")

    return {
        "weather": {
            "enabled": bool(weather_key),
            "label": "Live weather",
            "detail": "OpenWeatherMap key detected" if weather_key else "Using bundled seasonal fallback",
        },
        "mandi": {
            "enabled": bool(mandi_key and mandi_resource),
            "label": "Live mandi prices",
            "detail": (
                "data.gov.in key and resource configured"
                if mandi_key and mandi_resource
                else "Using bundled mandi sample data"
            ),
        },
    }
