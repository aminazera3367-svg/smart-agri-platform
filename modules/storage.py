from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


DB_PATH = Path(__file__).resolve().parent.parent / "smart_agri.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_resource
def init_db() -> str:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS farmer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            role TEXT,
            region TEXT,
            farmer_profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            crop TEXT NOT NULL,
            season TEXT NOT NULL,
            region TEXT NOT NULL,
            predicted_price REAL NOT NULL,
            confidence REAL NOT NULL,
            trend TEXT,
            explanation TEXT,
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS crop_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            region TEXT,
            soil TEXT,
            water TEXT,
            budget REAL,
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS collaboration_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            region TEXT NOT NULL,
            crop TEXT NOT NULL,
            acreage REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS buyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_name TEXT NOT NULL,
            crop_needed TEXT NOT NULL,
            price_offered REAL NOT NULL,
            location TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )
        """
    )
    cur.execute("SELECT COUNT(*) AS count FROM buyers")
    if cur.fetchone()["count"] == 0:
        cur.executemany(
            """
            INSERT INTO buyers (buyer_name, crop_needed, price_offered, location)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("Annapurna Foods", "Rice", 2280, "Warangal"),
                ("Deccan Fresh", "Tomato", 960, "Hyderabad"),
                ("Krishi Retail Network", "Onion", 1760, "Nashik"),
                ("Green Basket", "Beans", 2460, "Bengaluru"),
                ("Surya Traders", "Groundnut", 5980, "Anantapur"),
                ("Spice Route Exports", "Chili", 7310, "Guntur"),
                ("NutriGrain Collective", "Millet", 3125, "Mysuru"),
            ],
        )
    conn.commit()
    conn.close()
    return str(DB_PATH)


def save_farmer_profile(user_name: str, role: str, region: str, farmer_profile: str) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT INTO farmer_profiles (user_name, role, region, farmer_profile)
        VALUES (?, ?, ?, ?)
        """,
        (user_name, role, region, farmer_profile),
    )
    conn.commit()
    conn.close()


def save_prediction(
    user_name: str,
    crop: str,
    season: str,
    region: str,
    predicted_price: float,
    confidence: float,
    trend: str,
    explanation: str,
    payload: dict[str, Any],
) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT INTO predictions (
            user_name, crop, season, region, predicted_price, confidence, trend, explanation, payload
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_name,
            crop,
            season,
            region,
            predicted_price,
            confidence,
            trend,
            explanation,
            json.dumps(payload),
        ),
    )
    conn.commit()
    conn.close()


def save_crop_plan(
    user_name: str,
    region: str,
    soil: str,
    water: str,
    budget: float,
    payload: dict[str, Any],
) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT INTO crop_plans (user_name, region, soil, water, budget, payload)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_name, region, soil, water, budget, json.dumps(payload)),
    )
    conn.commit()
    conn.close()


def save_collaboration_submission(user_name: str, region: str, crop: str, acreage: float) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT INTO collaboration_submissions (user_name, region, crop, acreage)
        VALUES (?, ?, ?, ?)
        """,
        (user_name, region, crop, acreage),
    )
    conn.commit()
    conn.close()


@st.cache_data(ttl=300)
def get_buyer_marketplace(crop: str | None = None) -> pd.DataFrame:
    conn = _connect()
    if crop and crop != "All":
        df = pd.read_sql_query(
            "SELECT buyer_name, crop_needed, price_offered, location FROM buyers WHERE active = 1 AND crop_needed = ?",
            conn,
            params=(crop,),
        )
    else:
        df = pd.read_sql_query(
            "SELECT buyer_name, crop_needed, price_offered, location FROM buyers WHERE active = 1",
            conn,
        )
    conn.close()
    return df.rename(
        columns={
            "buyer_name": "Buyer",
            "crop_needed": "Crop Needed",
            "price_offered": "Price Offered (INR/quintal)",
            "location": "Location",
        }
    )


def build_collaboration_frame(base_df: pd.DataFrame, region: str) -> pd.DataFrame:
    conn = _connect()
    df = pd.read_sql_query(
        """
        SELECT crop, SUM(acreage) AS acreage
        FROM collaboration_submissions
        WHERE region = ?
        GROUP BY crop
        """,
        conn,
        params=(region,),
    )
    conn.close()
    merged = base_df.copy()
    if not df.empty:
        increments = dict(zip(df["crop"], df["acreage"]))
        for idx, row in merged.iterrows():
            acreage = increments.get(row["Crop"], 0.0)
            if acreage:
                merged.at[idx, "Farmers_Count"] = int(row["Farmers_Count"] + max(1, acreage / 8))
    return merged
