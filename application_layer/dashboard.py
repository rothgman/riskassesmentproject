from typing import List, Dict
from tabulate import tabulate

def render_dashboard(borrowers: List[Dict]) -> None:
    """
    Display a basic text-based dashboard of borrowers and their risk profiles.
    """
    headers = ["ID", "Name", "Region", "Loan", "Score", "Risk"]
    table = [
        [b["id"], b["name"], b["region"], b["loan_amount"], b.get("adjusted_score", "N/A"), b.get("risk")]
        for b in borrowers
    ]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
