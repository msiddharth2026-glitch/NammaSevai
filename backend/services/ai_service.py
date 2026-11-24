import os
import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple, List
from ..config import settings
from .extractor import CitizenInfoExtractor

logger = logging.getLogger("nammasevai.ai_service")

class AIService:
    """
    Real AI Language Understanding & Response Generation for NammaSevai AI.
    Integrates with Google Gemini API (or OpenAI API) when configured,
    and falls back to high-precision Tamil/Tanglish rule extraction
    with transparent configuration instructions when keys are absent.
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.rule_extractor = CitizenInfoExtractor()

    def is_api_configured(self) -> bool:
        return bool(self.gemini_api_key or self.openai_api_key)

    def get_configuration_instruction(self) -> Optional[Dict[str, str]]:
        if not self.is_api_configured():
            return {
                "status": "unconfigured",
                "message_en": "To enable generative AI language reasoning with Google Gemini, please set GEMINI_API_KEY in your .env file. The system is currently using verified Tamil/Tanglish NLP rule matching.",
                "message_ta": "கூகுள் ஜெமினி AI மொழிப் புரிதலை செயல்படுத்த .env கோப்பில் GEMINI_API_KEY ஐ உள்ளிடவும். தற்போது சரிபார்க்கப்பட்ட தமிழ்/தங்கிலீஷ் விதிமுறைப் பொறிமுறை இயங்குகிறது.",
                "env_variable": "GEMINI_API_KEY",
                "docs_url": "https://aistudio.google.com/app/apikey"
            }
        return None

    def analyze_with_gemini(self, text: str, lang: str = "ta") -> Optional[Dict[str, Any]]:
        """Calls Google Gemini API for deep natural language understanding."""
        if not self.gemini_api_key:
            return None

        # Gemini 1.5 Flash endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        prompt = f"""
You are NammaSevai AI, a government welfare scheme discovery assistant for Tamil Nadu, India.
Analyze the citizen's query in Tamil, Tanglish, or English:
Query: "{text}"

Extract the citizen's profile accurately into JSON with the following schema:
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
      "field_name": "string",
      "relevance_to_scheme": "string",
      "question_en": "Polite follow-up question in English",
      "question_ta": "எளிமையான தமிழ் தொடர் கேள்வி"
    }}
  ]
}}

Guidelines:
1. Understand colloquial Tamil (e.g. "கல்லூரி படிக்கிறேன்", "2 ஏக்கர் பூமி", "தையல் மெஷின்", "மாதம் 1000") and Tanglish (e.g. "naan college padikiren", "farming dryland").
2. NEVER guess missing mandatory eligibility information. If a student does not specify whether they studied in a Tamil Nadu Government school (needed for Pudhumai Penn and Tamil Pudhalvan), include a polite follow-up question.
3. Return ONLY valid JSON without markdown fences.
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}
        }

        try:
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                return json.loads(raw_text.strip())
            else:
                logger.warning(f"Gemini API returned error {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")

        return None

    def analyze_query(self, text: str, lang: str = "ta") -> Tuple[Dict[str, Any], List[str], List[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Processes citizen query using Gemini API if configured,
        or the deterministic NLP extractor.
        """
        gemini_result = None
        if self.gemini_api_key:
            gemini_result = self.analyze_with_gemini(text, lang)

        config_instruction = self.get_configuration_instruction()

        if gemini_result:
            profile_data = {
                "age": gemini_result.get("age"),
                "gender": gemini_result.get("gender"),
                "occupation": gemini_result.get("occupation"),
                "annual_income": gemini_result.get("annual_income"),
                "state": "Tamil Nadu",
                "district": gemini_result.get("district"),
                "education_level": gemini_result.get("education_level"),
                "school_type": gemini_result.get("school_type"),
                "landholding_acres": gemini_result.get("landholding_acres"),
                "community_category": gemini_result.get("community_category"),
                "disability_status": gemini_result.get("disability_status"),
                "is_widow_or_destitute": gemini_result.get("is_widow_or_destitute"),
                "is_pregnant_or_lactating": gemini_result.get("is_pregnant_or_lactating"),
                "has_tailoring_training": gemini_result.get("has_tailoring_training")
            }
            intents = gemini_result.get("identified_categories", [])
            missing = gemini_result.get("missing_critical_info", [])
            return profile_data, intents, missing, config_instruction

        # Fallback to rule extractor
        profile, intents, missing_objs = self.rule_extractor.extract(text)
        missing = [
            {
                "field_name": m.field_name,
                "relevance_to_scheme": m.relevance_to_scheme,
                "question_en": m.question_en,
                "question_ta": m.question_ta,
                "question_hi": getattr(m, "question_hi", m.question_en),
                "question_ml": getattr(m, "question_ml", m.question_en)
            }
            for m in missing_objs
        ]
        return profile.model_dump(), intents, missing, config_instruction

    def generate_compassionate_response(
        self, 
        query: str, 
        matches: list, 
        missing_info: list, 
        lang: str = "ta"
    ) -> str:
        """
        Generates a respectful, clear citizen-facing summary of findings in the selected language.
        Supports: ta (Tamil), hi (Hindi), ml (Malayalam), tanglish, hinglish, and en (English).
        """
        count = len(matches)
        top_match = matches[0] if count > 0 else None

        if lang == "ta":
            if count == 0:
                return (
                    "உங்கள் விவரங்களுக்கு நேரடி திட்டம் எதுவும் பொருந்தவில்லை. "
                    "தயவுசெய்து உங்கள் படிப்பு, விவசாய நிலம், குடும்ப ஆண்டு வருமானம் அல்லது "
                    "தொழில் போன்ற கூடுதல் விவரங்களை குறிப்பிடுங்கள்."
                )
            scheme_name = top_match.scheme_name_ta or top_match.scheme_name_en
            benefit = top_match.benefit_summary_ta or top_match.benefit_summary_en
            msg = (
                f"உங்கள் நிலையை ஆய்வு செய்து {count} நலத்திட்டங்களை கண்டறிந்துள்ளேன். "
                f"இதில் முக்கிய திட்டம் \"{scheme_name}\" ஆகும் (பலன்: {benefit}). "
            )
            if len(missing_info) > 0:
                first_q = missing_info[0].get("question_ta") or missing_info[0].get("question_en")
                msg += f"உங்கள் தகுதியை முழுமையாக உறுதி செய்ய: {first_q} "
            msg += "தேவையான ஆவணங்களை தயார் செய்து அரசு தளத்தில் அல்லது இ-சேவை மையத்தில் விண்ணப்பிக்கலாம்."
            return msg

        elif lang == "hi":
            if count == 0:
                return (
                    "आपके विवरण के अनुसार कोई प्रत्यक्ष सरकारी योजना मेल नहीं खाती। "
                    "कृपया अपनी शिक्षा, कृषि भूमि, पारिवारिक वार्षिक आय या व्यवसाय का अधिक विवरण दें।"
                )
            scheme_name = getattr(top_match, "scheme_name_hi", None) or top_match.scheme_name_en
            benefit = getattr(top_match, "benefit_summary_hi", None) or top_match.benefit_summary_en
            msg = (
                f"आपकी स्थिति का विश्लेषण करने के बाद मुझे {count} उपयुक्त कल्याणकारी योजनाएं मिली हैं। "
                f"इनमें प्रमुख योजना \"{scheme_name}\" है (लाभ: {benefit})। "
            )
            if len(missing_info) > 0:
                first_q = missing_info[0].get("question_hi") or missing_info[0].get("question_en")
                msg += f"आपकी पात्रता की पुष्टि के लिए: {first_q} "
            msg += "कृपया आवश्यक दस्तावेज़ तैयार रखें और आधिकारिक पोर्टल या ई-सेवा केंद्र पर आवेदन करें।"
            return msg

        elif lang == "ml":
            if count == 0:
                return (
                    "നിങ്ങൾ നൽകിയ വിവരങ്ങൾക്ക് അനുയോജ്യമായ പദ്ധതികൾ ഒന്നും കണ്ടെത്താനായില്ല. "
                    "ദയവായി വിദ്യാഭ്യാസം, കൃഷിഭൂമി, വാർഷിക വരുമാനം അല്ലെങ്കിൽ തൊഴിൽ വിവരങ്ങൾ നൽകുക."
                )
            scheme_name = getattr(top_match, "scheme_name_ml", None) or top_match.scheme_name_en
            benefit = getattr(top_match, "benefit_summary_ml", None) or top_match.benefit_summary_en
            msg = (
                f"നിങ്ങളുടെ സാഹചര്യം പരിശോധിച്ച് {count} ക്ഷേമപദ്ധതികൾ കണ്ടെത്തിയിട്ടുണ്ട്. "
                f"ഇതിൽ പ്രധാനപ്പെട്ടത് \"{scheme_name}\" ആണ് (ആനുകൂല്യം: {benefit}). "
            )
            if len(missing_info) > 0:
                first_q = missing_info[0].get("question_ml") or missing_info[0].get("question_en")
                msg += f"യോഗ്യത പൂർണ്ണമായി സ്ഥിരീകരിക്കാൻ: {first_q} "
            msg += "രേഖകൾ തയ്യാറാക്കി ഔദ്യോഗിക പോർട്ടൽ വഴി അപേക്ഷ സമർപ്പിക്കാം."
            return msg

        elif lang == "tanglish":
            if count == 0:
                return (
                    "Unga details-kku direct scheme edhuvum match aagala. "
                    "Unga education, land, family annual income, or occupation pathi innum konjam sollunga."
                )
            scheme_name = top_match.scheme_name_ta or top_match.scheme_name_en
            benefit = top_match.benefit_summary_ta or top_match.benefit_summary_en
            msg = (
                f"Unga situation-ah analyze panni {count} welfare schemes match pannirukken. "
                f"Idhula main scheme \"{scheme_name}\" (Benefit: {benefit}). "
            )
            if len(missing_info) > 0:
                first_q = missing_info[0].get("question_ta") or missing_info[0].get("question_en")
                msg += f"Eligibility confirm panna: {first_q} "
            msg += "Thevaiyaana documents ready panni official portal or e-Sevai-la apply pannalaam."
            return msg

        elif lang == "hinglish":
            if count == 0:
                return (
                    "Aapki details ke matching koi direct welfare scheme nahi mili. "
                    "Please apni education, agriculture land, annual income ya occupation ki aur details batayein."
                )
            scheme_name = getattr(top_match, "scheme_name_hi", None) or top_match.scheme_name_en
            benefit = getattr(top_match, "benefit_summary_hi", None) or top_match.benefit_summary_en
            msg = (
                f"Aapki profile analyze karke {count} matching welfare schemes identify hui hain. "
                f"Inmein top scheme \"{scheme_name}\" hai (Benefit: {benefit}). "
            )
            if len(missing_info) > 0:
                first_q = missing_info[0].get("question_hi") or missing_info[0].get("question_en")
                msg += f"Eligibility confirm karne ke liye: {first_q} "
            msg += "Zaroori documents checklist check karke official portal ya e-Sevai center par apply karein."
            return msg

        else:
            if count == 0:
                return (
                    "We could not find an exact welfare scheme match for your description. "
                    "Please describe your education, landholding, annual income or occupation."
                )
            scheme_name = top_match.scheme_name_en
            benefit = top_match.benefit_summary_en
            msg = (
                f"Based on your profile, I identified {count} potential welfare scheme(s). "
                f"The top recommendation is \"{scheme_name}\" providing {benefit}. "
            )
            if len(missing_info) > 0:
                first_q = missing_info[0].get("question_en")
                msg += f"To confirm your eligibility: {first_q} "
            msg += "Please review the required documents checklist below before applying."
            return msg

ai_service = AIService()
