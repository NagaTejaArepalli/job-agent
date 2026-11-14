import re
from typing import Tuple

INDIA_CITIES = [
    "bangalore", "bengaluru", "hyderabad", "chennai", "pune", "mumbai", 
    "gurgaon", "gurugram", "noida", "delhi", "new delhi", "delhi ncr", 
    "kolkata", "ahmedabad", "kochi", "cochin", "trivandrum", "thiruvananthapuram",
    "chandigarh", "indore", "jaipur", "coimbatore", "mysore", "bhubaneswar",
    "karnataka", "telangana", "tamil nadu", "maharashtra", "haryana", "uttar pradesh"
]

NON_INDIA_INDICATORS = [
    "united states", "usa", "u.s.", "san francisco", "new york", "seattle", "austin", 
    "los gatos", "california", "london", "united kingdom", "uk", "canada", 
    "toronto", "vancouver", "germany", "berlin", "dublin", "ireland", "australia", 
    "sydney", "singapore", "tokyo", "japan", "amsterdam", "netherlands", "paris", "france",
    "colombia", "brazil", "mexico", "argentina", "chile", "peru", "latin america", "latam",
    "poland", "spain", "italy", "sweden", "switzerland", "romania", "ukraine", "czech",
    "philippines", "vietnam", "malaysia", "indonesia", "thailand", "taiwan", "china", "hong kong",
    "israel", "uae", "dubai", "egypt", "south africa", "nigeria", "kenya",
    "emea", "apac", "americas", "europe", "north america"
]

def is_india_location(location_str: str) -> Tuple[bool, str]:
    """
    Strictly verifies whether a job posting is located in India.
    Only allows:
    1. Explicit India location (e.g. 'India', 'Bangalore, India')
    2. Indian tech cities/states (e.g. 'Bangalore', 'Hyderabad', 'Pune')
    3. India Remote (e.g. 'India - Remote', 'Remote - India', 'Bangalore (Remote)')
    
    STRICTLY REJECTS:
    - Pure 'Remote' or generic 'Remote' without an explicit India mention
    - Remote in foreign countries (e.g. 'Colombia, Remote', 'US Remote', 'EMEA Remote')
    - Any foreign country or city
    """
    if not location_str:
        return False, "Unknown"
        
    loc_lower = location_str.lower().strip()
    
    # 1. Reject if foreign country or foreign region is present unless explicitly India
    has_foreign = any(re.search(r"\b" + re.escape(n_ind) + r"\b", loc_lower) for n_ind in NON_INDIA_INDICATORS)
    has_india = bool(re.search(r"\bindia\b", loc_lower) or re.search(r"\b\(?in\)?\b", loc_lower))
    
    if has_foreign and not has_india:
        return False, location_str.strip()
        
    # 2. Check for explicit India Remote patterns
    # e.g., "India - Remote", "Remote, India", "Remote - India", "India (Remote)", "Remote (India)", "IN-Remote"
    india_remote_patterns = [
        r"india\s*[-–,/|]\s*remote",
        r"remote\s*[-–,/|]\s*india",
        r"remote\s*\(india\)",
        r"india\s*\(remote\)",
        r"in-remote",
        r"remote\s*,\s*in\b"
    ]
    for pat in india_remote_patterns:
        if re.search(pat, loc_lower):
            return True, location_str.strip()

    # 3. Check for Indian metro tech hubs (with or without remote/hybrid)
    for city in INDIA_CITIES:
        if re.search(r"\b" + re.escape(city) + r"\b", loc_lower):
            if not has_foreign:
                return True, location_str.strip()
                
    # 4. Check for standalone explicit "India" (e.g., "India", "Remote in India", "All India")
    if has_india and not has_foreign:
        return True, location_str.strip()
        
    # All generic "Remote" without India, or any foreign locations are rejected
    return False, location_str.strip()
