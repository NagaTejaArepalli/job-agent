import re
from typing import Tuple

INDIA_CITIES = [
    "bangalore", "bengaluru", "hyderabad", "chennai", "pune", "mumbai", 
    "gurgaon", "gurugram", "noida", "delhi", "new delhi", "delhi ncr", 
    "kolkata", "ahmedabad", "kochi", "cochin", "trivandrum", "thiruvananthapuram",
    "chandigarh", "indore", "jaipur", "coimbatore", "mysore", "bhubaneswar", "karnataka", "telangana", "tamil nadu", "maharashtra"
]

NON_INDIA_INDICATORS = [
    "united states", "usa", "san francisco", "new york", "seattle", "austin", 
    "los gatos", "california", "london", "united kingdom", "uk", "canada", 
    "toronto", "vancouver", "germany", "berlin", "dublin", "ireland", "australia", 
    "sydney", "singapore", "tokyo", "japan", "amsterdam", "netherlands", "paris", "france"
]

def is_india_location(location_str: str) -> Tuple[bool, str]:
    """
    Strictly verifies whether a job posting is located in India.
    Returns (is_in_india: bool, normalized_location: str).
    """
    if not location_str:
        return False, "Unknown"
        
    loc_lower = location_str.lower().strip()
    
    # 1. Explicit mention of India
    # Matches "India", "Remote - India", "Bangalore, India", etc.
    if re.search(r"\bindia\b", loc_lower) or "in-remote" in loc_lower or "remote, india" in loc_lower or "remote - india" in loc_lower:
        return True, location_str.strip()
        
    # 2. Check for Indian metro tech hubs
    for city in INDIA_CITIES:
        if re.search(r"\b" + re.escape(city) + r"\b", loc_lower):
            # Guard against edge cases like "London, UK"
            if not any(re.search(r"\b" + re.escape(n_ind) + r"\b", loc_lower) for n_ind in NON_INDIA_INDICATORS):
                return True, location_str.strip()
                
    # 3. Check for pure "Remote" without explicit foreign country
    if "remote" in loc_lower and not any(re.search(r"\b" + re.escape(n_ind) + r"\b", loc_lower) for n_ind in NON_INDIA_INDICATORS):
        return True, f"{location_str.strip()} (India Eligible)"
        
    return False, location_str.strip()
