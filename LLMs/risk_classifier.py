def classify_risk(score: float) -> str:
    """
    Classify risk score into Low, Medium, or High.
    """
    if score < 0.4:
        return "Low"
    elif score < 0.7:
        return "Medium"
    else:
        return "High"
