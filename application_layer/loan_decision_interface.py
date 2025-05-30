from typing import Dict

def approve_loan(risk_level: str, policy: Dict[str, bool]) -> bool:
    """
    Return True if loan is approved under current policy rules.
    """
    return policy.get(risk_level, False)

def override_decision(borrower_id: str, current_status: bool, reason: str) -> dict:
    """
    Log override decision for auditing.
    """
    return {
        "borrower_id": borrower_id,
        "override_to": not current_status,
        "reason": reason
    }
