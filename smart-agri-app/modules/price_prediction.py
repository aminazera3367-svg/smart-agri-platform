from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
import streamlit as st

from .config import get_config_value

try:
    from sklearn.ensemble import RandomForestRegressor  # type: ignore
except Exception:  # pragma: no cover
    RandomForestRegressor = None


PRICE_BASE = {
    "Tomato": 920,
    "Onion": 1725,
    "Millet": 3080,
    "Groundnut": 5920,
    "Chili": 7240,
    "Beans": 2380,
    "Rice": 2240,
}

REGION_FACTOR = {
    "Central Valley": 1.03,
    "North Belt": 0.98,
    "South Plains": 1.01,
    "Coastal Delta": 1.05,
}

SEASON_FACTOR = {
    "Winter (Rabi)": 1.02,
    "Summer (Zaid)": 0.96,
    "Monsoon (Kharif)": 1.04,
}

CROP_CODES = {name: idx for idx, name in enumerate(PRICE_BASE, start=1)}
REGION_CODES = {name: idx for idx, name in enumerate(REGION_FACTOR, start=1)}
SEASON_CODES = {name: idx for idx, name in enumerate(SEASON_FACTOR, start=1)}


def _fallback_mandi_frame(crop: str) -> pd.DataFrame:
    base = PRICE_BASE.get(crop, 2000)
    today = datetime.now().date()
    rows = []
    for offset in range(35):
        date_value = today - timedelta(days=34 - offset)
        slope = (offset - 17) * 6
        seasonality = np.sin(offset / 4.2) * (55 if crop in {"Tomato", "Chili"} else 28)
        noise = ((sum(ord(ch) for ch in crop) + offset) % 9) - 4
        modal_price = round(base + slope + seasonality + noise, 2)
        rows.append(
            {
                "date": pd.Timestamp(date_value),
                "market": "Agmarknet Sample",
                "crop": crop,
                "modal_price": max(200, modal_price),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def fetch_mandi_prices(crop: str, region: str | None = None) -> dict:
    api_key = get_config_value("DATA_GOV_API_KEY")
    resource_id = get_config_value("MANDI_RESOURCE_ID")

    df = pd.DataFrame()
    source = "Bundled mandi sample"
    if api_key and resource_id:
        try:
            response = requests.get(
                f"https://api.data.gov.in/resource/{resource_id}",
                params={
                    "api-key": api_key,
                    "format": "json",
                    "limit": 50,
                    "filters[commodity]": crop,
                },
                timeout=10,
            )
            response.raise_for_status()
            records = response.json().get("records", [])
            parsed = []
            for record in records:
                modal_price = record.get("modal_price")
                if not modal_price:
                    continue
                parsed.append(
                    {
                        "date": pd.to_datetime(record.get("arrival_date"), errors="coerce"),
                        "market": record.get("market", "Unknown"),
                        "crop": crop,
                        "modal_price": float(modal_price),
                    }
                )
            df = pd.DataFrame(parsed).dropna(subset=["date"])
            if not df.empty:
                source = "data.gov.in / mandi dataset"
        except Exception:
            df = pd.DataFrame()

    if df.empty:
        df = _fallback_mandi_frame(crop)

    df = df.sort_values("date").tail(30).reset_index(drop=True)
    recent_prices = df["modal_price"].round(2).tolist()
    avg_price = round(float(df["modal_price"].mean()), 2)
    first_window = float(df["modal_price"].head(7).mean())
    last_window = float(df["modal_price"].tail(7).mean())
    delta = last_window - first_window
    if delta > avg_price * 0.03:
        trend = "Rising"
    elif delta < -avg_price * 0.03:
        trend = "Falling"
    else:
        trend = "Stable"

    return {
        "data": df,
        "recent_prices": recent_prices,
        "average_price": avg_price,
        "trend": trend,
        "source": source,
    }


def _fallback_price_estimate(features: pd.DataFrame, target: pd.Series, future_row: pd.DataFrame) -> float:
    coeffs = np.array([0.26, 0.18, 0.14, 0.06, 0.06, 0.06, 0.10, 0.06, 0.08])
    coeffs = coeffs[: features.shape[1]]
    coeffs = coeffs / coeffs.sum()
    baseline = float(target.tail(5).mean())
    feature_signal = float(np.dot(future_row.iloc[0].to_numpy(dtype=float), coeffs))
    historical_signal = float(features.tail(5).mean().to_numpy(dtype=float).dot(coeffs))
    return baseline + (feature_signal - historical_signal) * 0.35


@st.cache_data(ttl=3600)
def predict_crop_price(
    crop: str,
    season: str,
    region: str,
    weather: dict,
    demand_index: float,
) -> dict:
    mandi = fetch_mandi_prices(crop, region)
    df = mandi["data"].copy()
    df["lag_1"] = df["modal_price"].shift(1)
    df["rolling_3"] = df["modal_price"].rolling(3).mean()
    df["rolling_7"] = df["modal_price"].rolling(7).mean()
    df["crop_code"] = CROP_CODES.get(crop, 0)
    df["season_code"] = SEASON_CODES.get(season, 0)
    df["region_code"] = REGION_CODES.get(region, 0)
    df["temperature"] = weather["temperature"]
    df["humidity"] = weather["humidity"]
    df["demand_index"] = demand_index
    model_df = df.dropna().copy()

    feature_columns = [
        "lag_1",
        "rolling_3",
        "rolling_7",
        "crop_code",
        "season_code",
        "region_code",
        "temperature",
        "humidity",
        "demand_index",
    ]
    features = model_df[feature_columns]
    target = model_df["modal_price"]
    future_row = pd.DataFrame(
        [
            {
                "lag_1": float(df["modal_price"].iloc[-1]),
                "rolling_3": float(df["modal_price"].tail(3).mean()),
                "rolling_7": float(df["modal_price"].tail(7).mean()),
                "crop_code": CROP_CODES.get(crop, 0),
                "season_code": SEASON_CODES.get(season, 0),
                "region_code": REGION_CODES.get(region, 0),
                "temperature": weather["temperature"],
                "humidity": weather["humidity"],
                "demand_index": demand_index,
            }
        ]
    )

    model_used = "Fallback ensemble regressor"
    if RandomForestRegressor and len(features) >= 10:
        model = RandomForestRegressor(
            n_estimators=120,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42,
        )
        model.fit(features, target)
        predicted = float(model.predict(future_row)[0])
        model_used = "RandomForestRegressor"
    else:
        predicted = _fallback_price_estimate(features, target, future_row)

    predicted *= SEASON_FACTOR.get(season, 1.0) * REGION_FACTOR.get(region, 1.0)
    predicted = round(predicted, 2)

    volatility = float(df["modal_price"].tail(10).std() or 0)
    base_conf = 92 - min(18, volatility / max(1, mandi["average_price"]) * 100)
    confidence = round(max(68, min(95, base_conf)), 1)

    delta = predicted - mandi["average_price"]
    if delta > mandi["average_price"] * 0.025:
        trend = "Rising"
    elif delta < -mandi["average_price"] * 0.025:
        trend = "Falling"
    else:
        trend = "Stable"

    explanation = {
        "price_trend": (
            f"{crop} mandi prices are {mandi['trend'].lower()} with a 30-day average near "
            f"INR {mandi['average_price']:.0f}/quintal."
        ),
        "environmental_reasoning": (
            f"Weather in {region} is {weather['description'].lower()} at {weather['temperature']}°C "
            f"with humidity near {weather['humidity']}%, which affects arrivals and storage quality."
        ),
        "recommendation_reason": (
            f"Demand index at {demand_index:.0f} and the recent mandi curve support a {trend.lower()} "
            f"price outlook for {season}."
        ),
    }

    return {
        "predicted_price": predicted,
        "confidence_score": confidence,
        "trend": trend,
        "historical_prices": mandi["recent_prices"],
        "average_price": mandi["average_price"],
        "source": mandi["source"],
        "model_used": model_used,
        "explanation": explanation,
    }
