from enum import Enum
from typing import Dict, List

# 36 States + FCT
NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo",
    "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos",
    "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers",
    "Sokoto", "Taraba", "Yobe", "Zamfara", "FCT"
]

class PropertyType(str, Enum):
    SELF_CONTAIN = "Self-Contain"
    MINI_FLAT = "Mini-Flat"
    FLAT_1BR = "1BR Flat"
    FLAT_2BR = "2BR Flat"
    FLAT_3BR = "3BR Flat"
    FLAT_4BR = "4BR Flat"
    TERRACE_DUPLEX = "Terrace Duplex"
    SEMI_DET_DUPLEX = "Semi-Detached Duplex"
    FULLY_DET_DUPLEX = "Fully-Detached Duplex"
    BUNGALOW = "Bungalow"
    PENTHOUSE = "Penthouse"

# Deviation Index Thresholds
DEVIATION_HIGH_FRAUD = -0.35
DEVIATION_OVERPRICED = 0.25
DEVIATION_FAIR_MIN = -0.15
DEVIATION_FAIR_MAX = 0.15

# LGA Data Mapping (Simplified placeholder, in a real app this would be a full 774 entry dict or DB table)
# For the purpose of this implementation, I'll include the most common LGAs for core states
STATE_LGA_MAP: Dict[str, List[str]] = {
    "Lagos": ["Ikeja", "Eti-Osa", "Alimosho", "Ikorodu", "Oshodi-Isolo", "Surulere", "Agege", "Ifako-Ijaiye", "Shomolu", "Amuwo-Odofin", "Lagos Mainland", "Lagos Island", "Apapa", "Badagry", "Epe", "Ibeju-Lekki", "Mushin", "Ojo", "Kosofe"],
    "FCT": ["Abuja Municipal", "Gwagwalada", "Kuje", "Bwari", "Abaji", "Kwali"],
    "Rivers": ["Port Harcourt City", "Obio-Akpor", "Ikwerre", "Oyigbo", "Eleme", "Tai", "Gokana", "Khana"],
    "Oyo": ["Ibadan North", "Ibadan North-East", "Ibadan North-West", "Ibadan South-East", "Ibadan South-West", "Akinyele", "Egbeda", "Oluyole", "Ona Ara", "Lagelu"],
    "Kano": ["Kano Municipal", "Fagge", "Dala", "Gwale", "Tarauni", "Nassarawa", "Kumbotso", "Ungogo"],
    "Kaduna": ["Kaduna North", "Kaduna South", "Chikun", "Igabi", "Zaria", "Sabon Gari"],
    # ... In a production script, this would be populated with all 774.
}

# Add all states to the map if not explicitly defined above to ensure consistency
for state in NIGERIAN_STATES:
    if state not in STATE_LGA_MAP:
        STATE_LGA_MAP[state] = [] # Placeholder for other states
