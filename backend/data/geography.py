"""
Official Geographical and Administrative Classifications for India.
Covers Central Government, all 28 States, and all 8 Union Territories.
"""

from typing import List, Dict, Optional, Tuple

INDIAN_STATES: Tuple[str, ...] = (
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
)

INDIAN_UNION_TERRITORIES: Tuple[str, ...] = (
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry"
)

GOVERNMENT_LEVELS: Tuple[str, ...] = (
    "Central",
    "State",
    "Union Territory"
)

SCHEME_STATUSES: Tuple[str, ...] = (
    "Active",
    "Inactive",
    "Under Review",
    "Discontinued"
)

SCHEME_CATEGORIES: Dict[str, Dict[str, str]] = {
    "education": {
        "name_en": "Education & Scholarships",
        "name_ta": "கல்வி & உதவித்தொகை",
        "name_hi": "शिक्षा और छात्रवृत्ति",
        "name_ml": "വിദ്യാഭ്യാസം & സ്കോളർഷിപ്പ്"
    },
    "agriculture": {
        "name_en": "Agriculture & Rural",
        "name_ta": "விவசாயம் & ஊரகம்",
        "name_hi": "कृषि और ग्रामीण विकास",
        "name_ml": "കൃഷി & ഗ്രാമവികസനം"
    },
    "health": {
        "name_en": "Healthcare & Wellness",
        "name_ta": "மருத்துவம் & நல்வாழ்வு",
        "name_hi": "स्वास्थ्य और कल्याण",
        "name_ml": "ആരോഗ്യം & സുസ്ഥിരത"
    },
    "women": {
        "name_en": "Women & Child Welfare",
        "name_ta": "பெண்கள் & குழந்தைகள் நலம்",
        "name_hi": "महिला एवं बाल कल्याण",
        "name_ml": "വനിതാ-ശിശു ക്ഷേമം"
    },
    "employment": {
        "name_en": "Employment & Livelihood",
        "name_ta": "வேலைவாய்ப்பு & வாழ்வாதாரம்",
        "name_hi": "रोजगार और आजीविका",
        "name_ml": "തൊഴിൽ & ജീവനോപാധി"
    },
    "business": {
        "name_en": "Business & MSME",
        "name_ta": "வணிகம் & குறுந்தொழில்",
        "name_hi": "व्यापार और एमएसएमई",
        "name_ml": "ബിസിനസ് & എംഎസ്എംഇ"
    },
    "housing": {
        "name_en": "Housing & Urban",
        "name_ta": "வீட்டுவசதி & நகர்ப்புறம்",
        "name_hi": "आवास और शहरी विकास",
        "name_ml": "ഭവനം & നഗരവികസനം"
    },
    "seniors": {
        "name_en": "Senior Citizens Welfare",
        "name_ta": "மூத்த குடிமக்கள் நலம்",
        "name_hi": "वरिष्ठ नागरिक कल्याण",
        "name_ml": "മുതിർന്ന പൗരന്മാരുടെ ക്ഷേമം"
    },
    "disability": {
        "name_en": "Disability Support",
        "name_ta": "மாற்றுத்திறனாளிகள் நலம்",
        "name_hi": "दिव्यांगजन सशक्तिकरण",
        "name_ml": "ഭിന്നശേഷി ക്ഷേമം"
    },
    "financial": {
        "name_en": "Financial Assistance & Pension",
        "name_ta": "நிதி உதவி & ஓய்வூதியம்",
        "name_hi": "वित्तीय सहायता और पेंशन",
        "name_ml": "സാമ്പത്തിക സഹായം & പെൻഷൻ"
    },
    "social_security": {
        "name_en": "Social Security & Welfare",
        "name_ta": "சமூக பாதுகாப்பு & நலம்",
        "name_hi": "सामाजिक सुरक्षा और कल्याण",
        "name_ml": "സാമൂഹിക സുരക്ഷ & ക്ഷേമം"
    },
    "skills": {
        "name_en": "Skill Development",
        "name_ta": "திறன் மேம்பாடு",
        "name_hi": "कौशल विकास",
        "name_ml": "നൈപുണ്യ വികസനം"
    },
    "other": {
        "name_en": "General Citizen Welfare",
        "name_ta": "பொது மக்கள் நலம்",
        "name_hi": "सामान्य नागरिक कल्याण",
        "name_ml": "പൊതുജന ക്ഷേമം"
    }
}

# Alias mapping for fuzzy/colloquial name resolution
_ALIAS_MAP: Dict[str, str] = {
    "all india": "All India",
    "central": "Central",
    "central government": "Central",
    "india": "All India",
    "tn": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "up": "Uttar Pradesh",
    "mp": "Madhya Pradesh",
    "ap": "Andhra Pradesh",
    "wb": "West Bengal",
    "hp": "Himachal Pradesh",
    "uk": "Uttarakhand",
    "nct of delhi": "Delhi",
    "national capital territory of delhi": "Delhi",
    "new delhi": "Delhi",
    "dnh and dd": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "pondicherry": "Puducherry",
    "orissa": "Odisha",
    "uttaranchal": "Uttarakhand",
    "j&k": "Jammu and Kashmir",
    "a&n islands": "Andaman and Nicobar Islands",
    "andaman & nicobar": "Andaman and Nicobar Islands"
}

def is_valid_state(name: str) -> bool:
    if not name:
        return False
    return name.strip() in INDIAN_STATES

def is_valid_ut(name: str) -> bool:
    if not name:
        return False
    return name.strip() in INDIAN_UNION_TERRITORIES

def normalize_jurisdiction(name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Normalizes a jurisdiction string into (canonical_name, level).
    Level is one of: "Central", "State", "Union Territory", or (None, None).
    """
    if not name or not name.strip():
        return None, None
    
    clean = name.strip()
    lower = clean.lower()

    if lower in ("central", "central government", "all india", "india"):
        return "All India", "Central"

    # Check alias
    if lower in _ALIAS_MAP:
        clean = _ALIAS_MAP[lower]
        lower = clean.lower()

    for s in INDIAN_STATES:
        if s.lower() == lower:
            return s, "State"

    for u in INDIAN_UNION_TERRITORIES:
        if u.lower() == lower:
            return u, "Union Territory"

    return clean, "State"

def get_all_jurisdictions() -> Dict[str, List[str]]:
    """Returns all 28 states and 8 union territories grouped by level."""
    return {
        "central": ["All India"],
        "states": list(INDIAN_STATES),
        "union_territories": list(INDIAN_UNION_TERRITORIES)
    }
