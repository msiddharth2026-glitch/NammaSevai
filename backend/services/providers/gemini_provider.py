import json
import logging
import requests
from typing import Dict, Any, Optional
from .base_provider import BaseAIProvider, ANALYSIS_PROMPT_TEMPLATE, sanitize_json_text, sanitize_secret_in_error

logger = logging.getLogger("nammasevai.providers.gemini")

class GeminiProvider(BaseAIProvider):
    """
    Final AI Fallback Provider: Google Gemini
    Invoked when OpenAI and Grok are unavailable or fail.
    Uses Google Generative Language REST API with gemini-1.5-flash or configured model.
    """

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", timeout: int = 8):
        super().__init__(
            name="gemini",
            display_name="Google Gemini",
            priority=3,
            model=model or "gemini-1.5-flash",
            api_key=api_key,
            timeout=timeout
        )

    def analyze_query(self, text: str, lang: str = "ta") -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None

        prompt = ANALYSIS_PROMPT_TEMPLATE.format(text=text, lang=lang)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}
        }

        try:
            res = requests.post(url, json=payload, timeout=self.timeout)
            if res.status_code == 200:
                candidates = res.json().get("candidates", [])
                if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                    raw_text = candidates[0]["content"]["parts"][0]["text"].strip()
                    return json.loads(sanitize_json_text(raw_text))
                return None
            else:
                err_text = sanitize_secret_in_error(res.text[:200])
                logger.warning(f"Gemini API returned status {res.status_code}: {err_text}")
                raise RuntimeError(f"Gemini HTTP {res.status_code}: {err_text}")
        except Exception as e:
            cleaned_err = sanitize_secret_in_error(str(e))
            logger.error(f"Gemini analyze_query failed: {cleaned_err}")
            raise

    def generate_response(self, query: str, matches: list, missing_info: list, lang: str = "ta") -> Optional[str]:
        if not self.is_configured():
            return None

        count = len(matches)
        top_schemes_summary = ""
        for i, m in enumerate(matches[:3]):
            name = getattr(m, f"scheme_name_{lang}", None) or m.scheme_name_en
            ben = getattr(m, f"benefit_summary_{lang}", None) or m.benefit_summary_en
            top_schemes_summary += f"{i+1}. {name}: {ben}\n"

        missing_text = ""
        if missing_info:
            first_q = missing_info[0].get(f"question_{lang}") or missing_info[0].get("question_en", "")
            missing_text = f"Follow-up question to clarify eligibility: {first_q}"

        prompt = f"""
Citizen Query: "{query}"
Target Language: "{lang}" (ta=Tamil, hi=Hindi, ml=Malayalam, tanglish=Tamil in Latin script, hinglish=Hindi in Latin script, en=English)
Total Potential Schemes Matched: {count}
Top Recommended Schemes:
{top_schemes_summary or "No direct matching scheme found."}

{missing_text}

Task:
Draft a compassionate, respectful 2-3 sentence response in the exact target language ({lang}).
Inform the citizen about how many schemes were found, mention the top scheme and its benefit, mention the follow-up question if present, and advise them to verify documents and apply via the official government portal or local e-Sevai center.
Do not use markdown formatting.
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 512}
        }

        try:
            res = requests.post(url, json=payload, timeout=self.timeout)
            if res.status_code == 200:
                candidates = res.json().get("candidates", [])
                if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                    return candidates[0]["content"]["parts"][0]["text"].strip()
                return None
            else:
                err_text = sanitize_secret_in_error(res.text[:200])
                logger.warning(f"Gemini generate_response returned status {res.status_code}: {err_text}")
                raise RuntimeError(f"Gemini HTTP {res.status_code}: {err_text}")
        except Exception as e:
            cleaned_err = sanitize_secret_in_error(str(e))
            logger.error(f"Gemini generate_response failed: {cleaned_err}")
            raise
