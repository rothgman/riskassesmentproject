def get_default_policy() -> dict:
    """
    Default loan approval policy by risk level.
    """
    return {
        "Low": True,
        "Medium": True,
        "High": False  # High risk not approved by default
    }

def adjust_thresholds(thresholds: dict, risk_weights: dict) -> dict:
    """
    Update scoring thresholds or factor weights.
    """
    thresholds.update(risk_weights)
    return thresholds
