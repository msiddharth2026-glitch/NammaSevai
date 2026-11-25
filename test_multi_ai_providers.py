import unittest
import time
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from backend.database import SessionLocal, Base, engine
from backend.config import settings
from backend.services.ai_provider_manager import AIProviderManager, CircuitState, ai_provider_manager
from backend.services.providers.base_provider import BaseAIProvider, sanitize_secret_in_error
from backend.services.providers.openai_provider import OpenAIProvider
from backend.services.providers.grok_provider import GrokProvider
from backend.services.providers.gemini_provider import GeminiProvider
from backend.services.ai_service import ai_service
from backend.routers.assistant import (
    analyze_citizen_query,
    match_citizen_schemes,
    get_ai_provider_public_status
)
from backend.routers.admin import (
    get_admin_ai_providers_status,
    reload_ai_providers_config,
    require_admin_auth
)
from backend.schemas.assistant import AnalyzeRequest, MatchRequest, ExtractedUserProfile

class TestMultiAIProviders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        self.mgr = AIProviderManager()
        self.mgr.timeout = 0.05
        for p in self.mgr.providers:
            p.timeout = 0.05
            h = self.mgr.health[p.name]
            h.circuit_state = CircuitState.CLOSED
            h.consecutive_failures = 0
            h.last_failure_time = 0.0
            h.total_calls = 0
            h.success_count = 0
            h.failure_count = 0

    def test_01_priority_order_openai_primary(self):
        """Case 1: When OpenAI succeeds, Grok and Gemini must be skipped."""
        mock_openai_res = {
            "age": 19,
            "gender": "female",
            "occupation": "student",
            "identified_categories": ["education"],
            "missing_critical_info": []
        }
        with patch.object(self.mgr.openai_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.openai_provider, 'analyze_query', return_value=mock_openai_res), \
             patch.object(self.mgr.grok_provider, 'analyze_query') as mock_grok, \
             patch.object(self.mgr.gemini_provider, 'analyze_query') as mock_gemini:
            
            result, provider_used, history = self.mgr.analyze_query("I am a 19 year old college girl", "en")
            
            self.assertEqual(provider_used, "openai")
            self.assertEqual(result["occupation"], "student")
            mock_grok.assert_not_called()
            mock_gemini.assert_not_called()
            self.assertEqual(self.mgr.health["openai"].success_count, 1)

    def test_02_fallback_openai_to_grok(self):
        """Case 2: When OpenAI fails (e.g. 401/429), it must cascade to Grok."""
        mock_grok_res = {
            "age": 30,
            "gender": "male",
            "occupation": "farmer",
            "identified_categories": ["agriculture"],
            "missing_critical_info": []
        }
        with patch.object(self.mgr.openai_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.openai_provider, 'analyze_query', side_effect=RuntimeError("OpenAI 401 Unauthorized")), \
             patch.object(self.mgr.grok_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.grok_provider, 'analyze_query', return_value=mock_grok_res), \
             patch.object(self.mgr.gemini_provider, 'analyze_query') as mock_gemini:

            result, provider_used, history = self.mgr.analyze_query("I am a farmer with 2 acres", "en")

            self.assertEqual(provider_used, "grok")
            self.assertEqual(result["occupation"], "farmer")
            mock_gemini.assert_not_called()
            self.assertEqual(self.mgr.health["openai"].failure_count, 1)
            self.assertEqual(self.mgr.health["grok"].success_count, 1)

    def test_03_fallback_openai_and_grok_to_gemini(self):
        """Case 3: When OpenAI and Grok fail, it must cascade to Gemini."""
        mock_gemini_res = {
            "age": 25,
            "gender": "female",
            "occupation": "tailor",
            "identified_categories": ["women"],
            "missing_critical_info": []
        }
        with patch.object(self.mgr.openai_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.openai_provider, 'analyze_query', side_effect=RuntimeError("OpenAI 500")), \
             patch.object(self.mgr.grok_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.grok_provider, 'analyze_query', side_effect=RuntimeError("Grok 429 Rate Limit")), \
             patch.object(self.mgr.gemini_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.gemini_provider, 'analyze_query', return_value=mock_gemini_res):

            result, provider_used, history = self.mgr.analyze_query("தையல் பயிற்சி முடித்துள்ளேன்", "ta")

            self.assertEqual(provider_used, "gemini")
            self.assertEqual(result["occupation"], "tailor")
            self.assertEqual(self.mgr.health["openai"].failure_count, 1)
            self.assertEqual(self.mgr.health["grok"].failure_count, 1)
            self.assertEqual(self.mgr.health["gemini"].success_count, 1)

    def test_04_fallback_all_providers_to_rule_engine(self):
        """Case 4: When all LLMs fail, deterministic rule extractor must take over safely."""
        with patch.object(self.mgr.openai_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.openai_provider, 'analyze_query', side_effect=RuntimeError("OpenAI Down")), \
             patch.object(self.mgr.grok_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.grok_provider, 'analyze_query', side_effect=RuntimeError("Grok Down")), \
             patch.object(self.mgr.gemini_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.gemini_provider, 'analyze_query', side_effect=RuntimeError("Gemini Down")):

            result, provider_used, history = self.mgr.analyze_query("college student girl in government school", "en")

            self.assertEqual(provider_used, "rule_engine")
            self.assertIsNone(result)
            self.assertEqual(len(history), 3)

    def test_05_circuit_breaker_tripping_and_bypass(self):
        """Tests that 3 consecutive failures trip the circuit to OPEN, skipping further network calls."""
        with patch.object(self.mgr.openai_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.openai_provider, 'analyze_query', side_effect=RuntimeError("Failed")), \
             patch.object(self.mgr.grok_provider, 'is_configured', return_value=False), \
             patch.object(self.mgr.gemini_provider, 'is_configured', return_value=False):

            # 3 failures to trigger circuit breaker
            for _ in range(3):
                self.mgr.analyze_query("test query", "en")

            h = self.mgr.health["openai"]
            self.assertEqual(h.consecutive_failures, 3)
            self.assertEqual(h.circuit_state, CircuitState.OPEN)

            # 4th call should immediately skip OpenAI without calling analyze_query
            with patch.object(self.mgr.openai_provider, 'analyze_query') as mock_call:
                self.mgr.analyze_query("test query 4", "en")
                mock_call.assert_not_called()

    def test_06_circuit_breaker_cooldown_and_recovery(self):
        """Tests that after cooldown expires, state moves to HALF_OPEN and recovers on success."""
        h = self.mgr.health["openai"]
        h.circuit_state = CircuitState.OPEN
        h.consecutive_failures = 3
        # Fast-forward time past cooldown
        h.last_failure_time = time.time() - (self.mgr.cooldown_seconds + 5)

        mock_success = {"occupation": "student", "identified_categories": []}
        with patch.object(self.mgr.openai_provider, 'is_configured', return_value=True), \
             patch.object(self.mgr.openai_provider, 'analyze_query', return_value=mock_success):

            res, provider_used, _ = self.mgr.analyze_query("recovery query", "en")
            self.assertEqual(provider_used, "openai")
            self.assertEqual(h.circuit_state, CircuitState.CLOSED)
            self.assertEqual(h.consecutive_failures, 0)

    def test_07_end_to_end_assistant_match_operation(self):
        """Tests match_citizen_schemes operates smoothly with provider sequence and deterministic fallback."""
        req = MatchRequest(
            query="I am a female college student in Chennai government college",
            lang="en"
        )
        res = match_citizen_schemes(req, db=self.db)
        self.assertGreater(res.total_potential_matches, 0)
        self.assertIsNotNone(res.active_provider)
        self.assertIsNotNone(res.compassionate_response)
        self.assertGreater(len(res.compassionate_response), 10)

    def test_08_multilingual_queries(self):
        """Tests full language matrix: ta, hi, ml, tanglish, hinglish, en."""
        test_cases = [
            ("நான் கல்லூரி மாணவி", "ta"),
            ("मैं सरकारी कॉलेज में पढ़ने वाली छात्रा हूँ", "hi"),
            ("ഞാൻ സർക്കാർ കോളേജിൽ പഠിക്കുന്ന വിദ്യാർത്ഥിനിയാണ്", "ml"),
            ("naan govt college student girl", "tanglish"),
            ("main govt college ki student ladki hu", "hinglish"),
            ("female student studying in government college", "en")
        ]
        for query, lang in test_cases:
            req = MatchRequest(query=query, lang=lang)
            res = match_citizen_schemes(req, db=self.db)
            self.assertIsNotNone(res.compassionate_response, f"Failed for lang {lang}")
            self.assertTrue(len(res.compassionate_response) > 10, f"Response too short for {lang}")

    def test_09_zero_secret_leakage_in_status(self):
        """Tests that status endpoints never return API keys or credentials."""
        # Public status
        pub_status = get_ai_provider_public_status()
        import json
        pub_json = json.dumps(pub_status)
        self.assertNotIn("sk-proj", pub_json)
        self.assertNotIn("xai-", pub_json)
        self.assertNotIn("Bearer", pub_json)
        self.assertNotIn("AQ.Ab8", pub_json)

        # Admin status
        adm_status = get_admin_ai_providers_status(authorized=True)
        adm_json = json.dumps(adm_status)
        self.assertNotIn("sk-proj", adm_json)
        self.assertNotIn("xai-", adm_json)
        self.assertNotIn("Bearer", adm_json)
        self.assertNotIn("AQ.Ab8", adm_json)

    def test_10_admin_status_unauthorized_rejection(self):
        """Tests that require_admin_auth rejects invalid or missing credentials."""
        with self.assertRaises(HTTPException) as ctx_none:
            require_admin_auth(x_admin_key=None)
        self.assertEqual(ctx_none.exception.status_code, 401)

        with self.assertRaises(HTTPException) as ctx_wrong:
            require_admin_auth(x_admin_key="invalid-wrong-key")
        self.assertEqual(ctx_wrong.exception.status_code, 401)

        # Valid key succeeds
        self.assertTrue(require_admin_auth(x_admin_key=settings.ADMIN_API_KEY))

    def test_11_sanitizer_removes_secrets_from_errors(self):
        """Tests that error sanitizers scrub all keys including dot/hyphen formats."""
        err_with_keys = (
            "Error with sk-proj-1234567890abcdef.extra and "
            "xai-9876543210zyxw.part and Bearer token123 and "
            "key=AQ.MOCK_TEST_DUMMY_GEMINI_KEY_ABC123_XYZ in request URL"
        )
        cleaned = sanitize_secret_in_error(err_with_keys)
        self.assertNotIn("sk-proj-1234567890abcdef", cleaned)
        self.assertNotIn("xai-9876543210zyxw", cleaned)
        self.assertNotIn("token123", cleaned)
        self.assertNotIn("AQ.MOCK_TEST", cleaned)
        self.assertIn("***REDACTED***", cleaned)

    def test_12_profile_continuity_across_turns(self):
        """Tests that user profile information is preserved across conversational turns."""
        req1 = MatchRequest(
            query="I am a 20 year old female student",
            lang="en"
        )
        turn1_res = match_citizen_schemes(req1, db=self.db)
        p1 = turn1_res.extracted_profile
        self.assertEqual(p1.gender, "female")

        # Turn 2: Citizen adds that they studied in a government school
        req2 = MatchRequest(
            query="Yes, I studied in a Tamil Nadu government school",
            profile=p1,
            lang="en"
        )
        turn2_res = match_citizen_schemes(req2, db=self.db)
        p2 = turn2_res.extracted_profile
        self.assertEqual(p2.gender, "female")
        self.assertEqual(p2.school_type, "government")

if __name__ == "__main__":
    unittest.main()
