from typing import List, Dict

def update_score_with_feedback(borrowers: List[Dict], feedback: Dict[str, float]) -> List[Dict]:
    """Apply repayment feedback to borrower risk scores."""
    for b in borrowers:
        if b['id'] in feedback:
            b['adjusted_score'] = float(b.get('base_score', 0)) + feedback[b['id']]
    return borrowers
