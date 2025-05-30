import csv
from typing import List, Dict

def load_borrower_data(csv_path: str) -> List[Dict]:
    """Load borrower information from a CSV file."""
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def get_borrower_by_id(borrower_id: str, data: List[Dict]) -> Dict:
    """Retrieve a borrower's record by ID."""
    return next((b for b in data if b.get("id") == borrower_id), None)
