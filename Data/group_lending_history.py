from typing import Dict, List

def summarize_group_history(group_data: List[Dict]) -> Dict:
    """Summarize repayment rates and risk signals from group lending data."""
    total_loans = len(group_data)
    successful_repayments = sum(1 for g in group_data if g.get("repaid") == "yes")
    defaulted = total_loans - successful_repayments

    return {
        "total_loans": total_loans,
        "successful_repayments": successful_repayments,
        "default_rate": defaulted / total_loans if total_loans else 0
    }
