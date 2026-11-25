import abc
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("nammasevai.providers.base")

# Standard schema definition for query analysis
ANALYSIS_PROMPT_TEMPLATE = """
You are NammaSevai AI, an expert government welfare scheme discovery assistant for Tamil Nadu, India.
Analyze the citizen's query in Tamil, Tanglish, Hindi, Hinglish, Malayalam, or English:
Query: "{text}"
Requested Response Language: "{lang}"

Extract the citizen's profile accurately into JSON with the following exact schema:
{{
  "age": integer or null,
  "gender": "female" or "male" or null,
  "occupation": "student" or "farmer" or "tailor" or "senior" or "unemployed" or "entrepreneur" or "housewife" or null,
  "annual_income": number in rupees or null,
  "district": "Tamil Nadu district name (e.g. Madurai, Chennai) or null",
  "education_level": "school_10th", "school_12th", "college_ug", "diploma", "graduate" or null,
  "school_type": "government" or "private" or null,
  "landholding_acres": number or null,
  "community_category": "SC", "ST", "BC", "MBC", "General" or null (ONLY if voluntarily stated),
  "disability_status": boolean or null (ONLY if voluntarily stated),
  "is_widow_or_destitute": boolean or null,
  "is_pregnant_or_lactating": boolean or null,
  "has_tailoring_training": boolean or null,
  "identified_categories": ["education", "women", "agriculture", "health", "employment", "seniors", "disability", "housing"],
  "missing_critical_info": [
    {{
      "field_name": "string (e.g. school_type, annual_income, landholding_acres)",
      "relevance_to_scheme": "string",
      "question_en": "Polite follow-up question in English",
      "question_ta": "எளிமையான தமிழ் தொடர் கேள்வி",
      "question_hi": "सरल हिंदी अनुवर्ती प्रश्न",
      "question_ml": "ലളിതമായ മലയാളം തുടർചോദ്യം"
    }}
  ]
}}

Guidelines:
1. Understand colloquial expressions in all supported languages:
   - Tamil (e.g. "கல்லூரி படிக்கிறேன்", "2 ஏக்கர் பூமி", "தையல் மெஷின்", "மாதம் 1000")
   - Tanglish (e.g. "naan college padikiren", "farming dryland", "thayyal machine")
   - Hindi (e.g. "कॉलेज में पढ़ रहा हूँ", "2 एकड़ ज़मीन", "सिलाई मशीन")
   - Hinglish (e.g. "college mein padh raha hu", "silai machine chahiye")
   - Malayalam (e.g. "കോളേജിൽ പഠിക്കുന്നു", "தையൽ മെഷീൻ")
   - English (e.g. "college student", "small farmer")
2. NEVER guess missing mandatory eligibility information. If a student does not specify whether they studied in a Tamil Nadu Government school (needed for Pudhumai Penn and Tamil Pudhalvan), include a polite follow-up question.
3. Return ONLY valid JSON without markdown fences.
"""

def sanitize_json_text(raw_text: str) -> str:
    """Strips markdown code fences and cleans up json output."""
    raw = raw_text.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()

def sanitize_secret_in_error(err_msg: str) -> str:
    """Removes API keys or authorization headers from error messages."""
    import re
    cleaned = re.sub(r'sk-[a-zA-Z0-9_\-\.]{8,}', 'sk-***REDACTED***', err_msg)
    cleaned = re.sub(r'xai-[a-zA-Z0-9_\-\.]{8,}', 'xai-***REDACTED***', cleaned)
    cleaned = re.sub(r'AIza[a-zA-Z0-9_\-\.]{10,}', 'AIza***REDACTED***', cleaned)
    cleaned = re.sub(r'AQ\.[a-zA-Z0-9_\-\.]{10,}', 'AQ.***REDACTED***', cleaned)
    cleaned = re.sub(r'Bearer\s+[^\s"\'}]+', 'Bearer ***REDACTED***', cleaned)
    cleaned = re.sub(r'key=[^\s"\'&]+', 'key=***REDACTED***', cleaned)
    return cleaned

class BaseAIProvider(abc.ABC):
    """Abstract base class for all NammaSevai AI providers."""
    
    def __init__(self, name: str, display_name: str, priority: int, model: str, api_key: str, timeout: int = 8):
        self.name = name
        self.display_name = display_name
        self.priority = priority
        self.model = model
        self.api_key = api_key.strip() if api_key else ""
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key)

    @abc.abstractmethod
    def analyze_query(self, text: str, lang: str = "ta") -> Optional[Dict[str, Any]]:
        """Extracts citizen profile attributes and missing info from query text."""
        pass

    @abc.abstractmethod
    def generate_response(self, query: str, matches: list, missing_info: list, lang: str = "ta") -> Optional[str]:
        """Generates a natural compassionate summary response in the requested language."""
        pass
