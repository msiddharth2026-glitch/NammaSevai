import json
import logging
import requests
from typing import Dict, Any, Optional
from .base_provider import BaseAIProvider, ANALYSIS_PROMPT_TEMPLATE, sanitize_json_text, sanitize_secret_in_error

logger = logging.getLogger("nammasevai.providers.grok")

HOMOGLYPH_MAP = {
    '\u03a7': 'X', '\u0395': 'E', '\u0396': 'Z', '\u039a': 'K', 
    '\u0397': 'H', '\u039f': 'O', '\u03a5': 'Y', '\u0391': 'A',
    '\u0392': 'B', '\u039c': 'M', '\u039d': 'N', '\u03a1': 'P', 
    '\u03a4': 'T'
}

def normalize_key(key: str) -> str:
    """Cleans whitespace and normalizes any Greek/Cyrillic homoglyphs to ASCII Latin."""
    if not key:
        return ""
    cleaned = ''.join(key.split())
    return ''.join(HOMOGLYPH_MAP.get(c, c) for c in cleaned)

class GrokProvider(BaseAIProvider):
    """
    Secondary AI Provider: Grok / xAI
    Invoked automatically when OpenAI is unavailable or fails.
    Uses official xAI chat completions API with grok-beta or configured model.
    """

    def __init__(self, api_key: str, model: str = "grok-beta", timeout: int = 8):
        normalized_key = normalize_key(api_key)
        super().__init__(
            name="grok",
            display_name="xAI / Grok",
            priority=2,
            model=model or "grok-beta",
            api_key=normalized_key,
            timeout=timeout
        )
        self.endpoint = "https://api.x.ai/v1/chat/completions"

    def analyze_query(self, text: str, lang: str = "ta") -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None

        prompt = ANALYSIS_PROMPT_TEMPLATE.format(text=text, lang=lang)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are NammaSevai AI, an expert citizen welfare discovery engine for Tamil Nadu, India. Extract eligibility attributes precisely into JSON. Output ONLY valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }

        try:
            res = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)
            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(sanitize_json_text(content))
            else:
                err_text = sanitize_secret_in_error(res.text[:200])
                logger.warning(f"Grok API returned status {res.status_code}: {err_text}")
                raise RuntimeError(f"Grok HTTP {res.status_code}: {err_text}")
        except Exception as e:
            cleaned_err = sanitize_secret_in_error(str(e))
            logger.error(f"Grok analyze_query failed: {cleaned_err}")
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are NammaSevai AI, a polite, empathetic government assistant helping citizens discover Tamil Nadu welfare schemes."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 512
        }

        try:
            res = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                err_text = sanitize_secret_in_error(res.text[:200])
                logger.warning(f"Grok generate_response returned status {res.status_code}: {err_text}")
                raise RuntimeError(f"Grok HTTP {res.status_code}: {err_text}")
        except Exception as e:
            cleaned_err = sanitize_secret_in_error(str(e))
            logger.error(f"Grok generate_response failed: {cleaned_err}")
            raise
