import json

def load_regional_data(file_path: str) -> dict:
    """Load static regional economic data from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_region_stats(region: str, data: dict) -> dict:
    """Retrieve economic stats for a given region."""
    return data.get(region, {})
