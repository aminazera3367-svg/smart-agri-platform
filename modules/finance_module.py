from __future__ import annotations


def calculate_farm_profit(crop: str, expected_yield: float, predicted_price: float, loan_amount: float) -> dict:
    crop_costs = {
        "Tomato": 42000,
        "Onion": 36000,
        "Millet": 18000,
        "Groundnut": 26000,
        "Chili": 48000,
        "Beans": 22000,
        "Rice": 34000,
    }
    base_cost = crop_costs.get(crop, 25000)
    revenue = expected_yield * predicted_price
    total_cost = base_cost + loan_amount * 0.08
    expected_profit = revenue - total_cost
    repayment_capacity = revenue / max(1, loan_amount)
    if expected_profit < 0 or repayment_capacity < 1.1:
        risk = "High"
    elif repayment_capacity < 1.5:
        risk = "Medium"
    else:
        risk = "Low"
    ability = "Weak" if repayment_capacity < 1.1 else "Moderate" if repayment_capacity < 1.5 else "Strong"
    return {
        "expected_profit": round(expected_profit, 2),
        "repayment_ability": ability,
        "risk_level": risk,
        "revenue": round(revenue, 2),
        "total_cost": round(total_cost, 2),
    }
