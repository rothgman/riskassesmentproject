def generate_explanation(borrower: dict, region_data: dict, score: float, classification: str) -> str:
    """
    Generate a human-readable explanation for the given score and classification.
    """
    return (
        f"{borrower['name']} from {borrower['region']} was given a risk score of {score:.2f}, "
        f"classified as '{classification}'. Regional unemployment is {region_data['unemployment_rate']:.2%}, "
        f"with an average income of ${region_data['avg_income']}. Adjustments were made based on these factors."
    )
