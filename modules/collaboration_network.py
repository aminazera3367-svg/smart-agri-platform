from __future__ import annotations

import pandas as pd


def get_collaboration_recommendation(df: pd.DataFrame) -> str:
    scored = df.assign(gap=df["Demand_Index"] - df["Farmers_Count"] * 0.75).sort_values("gap", ascending=False)
    return str(scored.iloc[0]["Crop"])


def get_market_story(crop: str) -> str:
    stories = {
        "Tomato": "Fresh arrivals are heavy, so timing and buyer reach matter more than raw production volume.",
        "Onion": "Storage behavior is shaping the market; disciplined release can protect margins.",
        "Beans": "Retail demand remains stable, giving beans a dependable diversification role.",
        "Chili": "Quality premiums remain stronger than bulk premiums, especially for cleaner lots.",
        "Millet": "Nutrition demand and water efficiency support millet as a resilient rotation crop.",
        "Groundnut": "Oilseed demand remains steady when shelling quality stays consistent.",
        "Rice": "Rice remains liquid, but weather resilience and selling windows still drive margins.",
    }
    return stories.get(crop, "The market is holding in a moderate trading band.")
