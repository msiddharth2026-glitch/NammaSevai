import os
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from ..config import settings
from .extractor import CitizenInfoExtractor
from .ai_provider_manager import ai_provider_manager

logger = logging.getLogger("nammasevai.ai_service")

class AIService:
    """
    Real Multi-Provider AI Language Understanding & Response Generation for NammaSevai AI.
    Integrates 3 providers with strict priority fallback:
      1. Primary: ChatGPT / OpenAI
      2. Secondary: Grok / xAI
      3. Final LLM: Google Gemini
      4. Safe Fallback: Verified Deterministic Rule Engine
    """

    def __init__(self):
        self.provider_manager = ai_provider_manager
        self.rule_extractor = CitizenInfoExtractor()

    def is_api_configured(self) -> bool:
        """Returns True if at least one generative AI provider key is configured."""
        return any(p.is_configured() for p in self.provider_manager.providers)

    def get_configuration_instruction(self) -> Optional[Dict[str, str]]:
        if not self.is_api_configured():
            return {
                "status": "unconfigured",
                "message_en": "To enable generative AI language reasoning with OpenAI, Grok, or Google Gemini, please configure OPENAI_API_KEY, XAI_API_KEY, or GEMINI_API_KEY in your .env file. The system is currently running on the verified Tamil/Tanglish/Hindi/Malayalam NLP rule matching engine.",
                "message_ta": "OpenAI, Grok அல்லது கூகுள் ஜெமினி AI மொழிப் புரிதலை செயல்படுத்த .env கோப்பில் OPENAI_API_KEY, XAI_API_KEY அல்லது GEMINI_API_KEY ஐ உள்ளிடவும். தற்போது சரிபார்க்கப்பட்ட பலமொழி விதிமுறைப் பொறிமுறை இயங்குகிறது.",
                "env_variable": "OPENAI_API_KEY / XAI_API_KEY / GEMINI_API_KEY",
                "docs_url": "https://platform.openai.com/api-keys"
            }
        return None

    def analyze_with_gemini(self, text: str, lang: str = "ta") -> Optional[Dict[str, Any]]:
        """Direct Gemini call preserved for backward compatibility."""
        try:
            return self.provider_manager.gemini_provider.analyze_query(text, lang)
        except Exception as e:
            logger.warning(f"analyze_with_gemini direct call failed: {e}")
            return None

    def analyze_query(
        self, 
        text: str, 
        lang: str = "ta"
    ) -> Tuple[Dict[str, Any], List[str], List[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Processes citizen query using the multi-provider priority manager:
        OpenAI -> Grok -> Gemini -> Deterministic NLP Rule Engine.
        """
        llm_result, provider_name, fallback_history = self.provider_manager.analyze_query(text, lang)
        config_instruction = self.get_configuration_instruction()

        if llm_result and isinstance(llm_result, dict):
            profile_data = {
                "age": llm_result.get("age"),
                "gender": llm_result.get("gender"),
                "occupation": llm_result.get("occupation"),
                "annual_income": llm_result.get("annual_income"),
                "state": llm_result.get("state"),
                "district": llm_result.get("district"),
                "education_level": llm_result.get("education_level"),
                "school_type": llm_result.get("school_type"),
                "landholding_acres": llm_result.get("landholding_acres"),
                "community_category": llm_result.get("community_category"),
                "disability_status": llm_result.get("disability_status"),
                "is_widow_or_destitute": llm_result.get("is_widow_or_destitute"),
                "is_pregnant_or_lactating": llm_result.get("is_pregnant_or_lactating"),
                "has_tailoring_training": llm_result.get("has_tailoring_training"),
                "marital_status": llm_result.get("marital_status"),
                "ration_card_type": llm_result.get("ration_card_type"),
                "residence_type": llm_result.get("residence_type"),
                "is_student": llm_result.get("is_student"),
                "is_farmer": llm_result.get("is_farmer"),
                "employment_status": llm_result.get("employment_status")
            }
            intents = llm_result.get("identified_categories", [])
            missing = llm_result.get("missing_critical_info", [])
            return profile_data, intents, missing, config_instruction

        # Deterministic Rule Extractor Fallback
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
        lang: str = "ta",
        skip_external_ai: bool = False
    ) -> str:
        """
        Generates a respectful, clear citizen-facing summary of findings in the selected language.
        Tries AI providers in strict sequence (OpenAI -> Grok -> Gemini), and falls back
        to verified deterministic multilingual response templates.
        """
        # 1. Attempt generation with active AI provider unless skipped
        if not skip_external_ai:
            ai_resp, provider_name, fallback_chain = self.provider_manager.generate_response(
                query=query, 
                matches=matches, 
                missing_info=missing_info, 
                lang=lang
            )
            if ai_resp:
                return ai_resp

        # 2. Deterministic Safe Multilingual Fallback
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

    def get_last_provider(self) -> str:
        return self.provider_manager.last_used_provider

    def get_safe_status(self) -> Dict[str, Any]:
        return self.provider_manager.get_safe_status()

ai_service = AIService()
