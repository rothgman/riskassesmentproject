def calculate_risk_score(borrower: dict, region_data: dict) -> float:
    """
    Calculate a base risk score using borrower info and regional economic data.
    """
    base = float(borrower.get("base_score", 0.5))
    unemployment = region_data.get("unemployment_rate", 0.1)
    income = region_data.get("avg_income", 200)

    # Simple scoring model: higher unemployment increases risk, higher income reduces it
    adjusted_score = base + (unemployment * 0.4) - (income / 1000.0)
    return min(max(adjusted_score, 0.0), 1.0)
