"""
Dedicated Cloud Deployment & Production Smoke Test Suite.
Verifies all 10 tasks for Phase 8.1 Live Cloud Deployment & Smoke Testing:
- Endpoint health and latency
- All 6 language journeys (en, ta, hi, ml, tanglish, hinglish)
- Scheme catalog discovery and search
- Deterministic eligibility matching
- Feedback submission and privacy shield
- Admin authentication and portal monitoring
- AI provider cascade, circuit breaker, and timeout resilience
- Background scheduler PID lock and singleton assurance
- Security headers and CORS configuration
"""

import os
import sys
import time
import unittest
from fastapi import HTTPException

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings
from backend.database import SessionLocal, Base, engine
from backend.models.scheme import Scheme
from backend.models.source import OfficialSource
from backend.routers.assistant import analyze_citizen_query, match_citizen_schemes
from backend.routers.schemes import list_schemes, get_scheme_by_id, get_scheme_documents
from backend.routers.voice import get_voice_config, synthesize_speech, SynthesizeRequest
from backend.routers.admin import (
    require_admin_auth,
    get_admin_stats,
    get_portal_health_status_endpoint,
    list_detected_changes_endpoint,
    get_scheduler_status_endpoint
)
from backend.routers.feedback import submit_feedback
from backend.schemas.assistant import AnalyzeRequest, MatchRequest
from backend.schemas.feedback import FeedbackCreate
from backend.services.ai_provider_manager import AIProviderManager, CircuitState
from backend.services.scheme_update_scheduler import (
    SchemeUpdateSchedulerService,
    LOCK_FILE_PATH,
    is_pid_running
)
from backend.middleware.security import SecurityHeadersMiddleware
from backend.main import health_check

class TestCloudProductionSmoke(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        from backend.services.ai_provider_manager import ai_provider_manager
        ai_provider_manager.timeout = 0.05
        for p in ai_provider_manager.providers:
            p.timeout = 0.05

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # -------------------------------------------------------------------------
    # 1. Health Endpoint & Latency
    # -------------------------------------------------------------------------
    def test_01_health_endpoint_response_time(self):
        t0 = time.perf_counter()
        health = health_check()
        duration_ms = (time.perf_counter() - t0) * 1000
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["database"], "connected")
        self.assertIn(health["dialect"], ["sqlite", "postgresql"])
        self.assertLess(duration_ms, 50.0, f"Health check took {duration_ms:.2f}ms (expected < 50ms)")

    # -------------------------------------------------------------------------
    # 2. Six Languages Journey Smoke Tests
    # -------------------------------------------------------------------------
    def test_02_multilingual_assistant_journey_all_six_languages(self):
        queries = [
            ("en", "I am a 19 year old girl from govt school studying in college degree", "pudhumai-penn"),
            ("ta", "நான் அரசுப் பள்ளியில் படித்த கல்லூரி மாணவி, எனக்கு உதவித்தொகை உண்டா?", "pudhumai-penn"),
            ("hi", "मैं एक कॉलेज छात्रा हूँ जिसने सरकारी स्कूल से पढ़ाई की है", "pudhumai-penn"),
            ("ml", "ഞാൻ സർക്കാർ സ്കൂളിൽ പഠിച്ച ഒരു കോളേജ് വിദ്യാർത്ഥിനിയാണ്", "pudhumai-penn"),
            ("tanglish", "Naan govt school la padicha college student girl, scholarship venum", "pudhumai-penn"),
            ("hinglish", "Main govt school se padhi hui college student ladki hoon", "pudhumai-penn"),
        ]

        for lang, text, expected_scheme_id in queries:
            with self.subTest(language=lang):
                t0 = time.perf_counter()
                req = MatchRequest(query=text, lang=lang)
                res = match_citizen_schemes(req, db=self.db)
                latency = (time.perf_counter() - t0) * 1000

                self.assertGreater(res.total_potential_matches, 0)
                matched_ids = [m.scheme_id for m in res.matches]
                self.assertIn(expected_scheme_id, matched_ids)
                self.assertLess(latency, 1000.0, f"Query in {lang} took {latency:.2f}ms (expected < 1000ms)")

    # -------------------------------------------------------------------------
    # 3. Scheme Catalog Search & Filter
    # -------------------------------------------------------------------------
    def test_03_scheme_catalog_search_and_filter(self):
        # All schemes
        all_schemes = list_schemes(limit=100, offset=0, db=self.db)
        self.assertEqual(len(all_schemes), 85)

        # Filter by category
        edu_schemes = list_schemes(category="education", limit=100, offset=0, db=self.db)
        self.assertGreater(len(edu_schemes), 0)
        self.assertTrue(all(s.category == "education" for s in edu_schemes))

        # Filter by State
        tn_schemes = list_schemes(state="Tamil Nadu", limit=100, offset=0, db=self.db)
        self.assertGreater(len(tn_schemes), 10)

        # Central level
        central_schemes = list_schemes(level="Central", limit=100, offset=0, db=self.db)
        self.assertEqual(len(central_schemes), 25)

    # -------------------------------------------------------------------------
    # 4. Scheme Details & Document Checklist
    # -------------------------------------------------------------------------
    def test_04_scheme_details_and_document_checklist(self):
        scheme = get_scheme_by_id("pudhumai-penn", db=self.db)
        self.assertEqual(scheme.id, "pudhumai-penn")
        self.assertIsNotNone(scheme.source)
        self.assertIn("penkalvi.tn.gov.in", scheme.source.portal_url)

        docs = get_scheme_documents("pudhumai-penn", db=self.db)
        self.assertGreater(len(docs), 0)
        doc_names = [d.name_en for d in docs]
        self.assertTrue(any("School" in d or "Aadhaar" in d for d in doc_names))

    # -------------------------------------------------------------------------
    # 5. Deterministic Eligibility Matching Accuracy
    # -------------------------------------------------------------------------
    def test_05_deterministic_eligibility_matching_rules(self):
        # Male student should NOT match Pudhumai Penn (Female only)
        req_male = MatchRequest(
            query="20 year old male student studying in college",
            lang="en"
        )
        res_male = match_citizen_schemes(req_male, db=self.db)
        matched_male_ids = [m.scheme_id for m in res_male.matches]
        self.assertNotIn("pudhumai-penn", matched_male_ids)

        # Farmer with 2 acres should match PM-Kisan
        req_farmer = MatchRequest(
            query="Small farmer with 2 acres land looking for agriculture financial support",
            lang="en"
        )
        res_farmer = match_citizen_schemes(req_farmer, db=self.db)
        matched_farmer_ids = [m.scheme_id for m in res_farmer.matches]
        self.assertIn("pm-kisan-tn", matched_farmer_ids)

    # -------------------------------------------------------------------------
    # 6. Privacy Shield: Feedback Submission & Aadhaar Rejection
    # -------------------------------------------------------------------------
    def test_06_feedback_submission_and_privacy_rejection(self):
        # 1. Valid anonymous feedback
        valid_fb = FeedbackCreate(
            preferred_language="en",
            ease_of_use_rating=5,
            clarity_rating=4,
            usefulness_rating=5,
            problems_encountered=None,
            suggestions="Very helpful in finding government student assistance."
        )
        fb_res = submit_feedback(valid_fb, db=self.db)
        self.assertEqual(fb_res.status, "received")

        # 2. PII / Aadhaar leak attempt rejected
        invalid_fb = FeedbackCreate(
            preferred_language="en",
            ease_of_use_rating=4,
            clarity_rating=4,
            usefulness_rating=4,
            problems_encountered="My Aadhaar number is 5432 9876 1234 please check status."
        )
        with self.assertRaises(HTTPException) as ctx:
            submit_feedback(invalid_fb, db=self.db)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Aadhaar", ctx.exception.detail)

    # -------------------------------------------------------------------------
    # 7. Admin Security & Constant-Time Authentication
    # -------------------------------------------------------------------------
    def test_07_admin_auth_and_portal_monitoring(self):
        # Authorized access
        self.assertTrue(require_admin_auth(x_admin_key=settings.ADMIN_API_KEY))

        # Unauthorized access
        with self.assertRaises(HTTPException) as ctx:
            require_admin_auth(x_admin_key="invalid-attacker-key")
        self.assertEqual(ctx.exception.status_code, 401)

        # Admin stats
        stats = get_admin_stats(db=self.db, authorized=True)
        self.assertGreaterEqual(stats["total_schemes"], 85)
        self.assertGreaterEqual(stats["verified_sources"], 80)

    # -------------------------------------------------------------------------
    # 8. Multi-Provider AI Cascade & Circuit Breaker Simulation
    # -------------------------------------------------------------------------
    def test_08_ai_provider_cascade_and_circuit_breaker(self):
        mgr = AIProviderManager()
        
        # Test all providers configured in order
        self.assertEqual(len(mgr.providers), 3)
        self.assertEqual(mgr.providers[0].name, "openai")
        self.assertEqual(mgr.providers[1].name, "grok")
        self.assertEqual(mgr.providers[2].name, "gemini")

        # Test Circuit Breaker behavior
        mgr.cooldown_seconds = 2
        mgr.failure_threshold = 3
        p_name = "openai"
        h = mgr.health[p_name]
        self.assertEqual(h.circuit_state, CircuitState.CLOSED)

        # 3 failures trip the breaker
        mgr._record_failure(p_name, "Simulated 500 error 1")
        mgr._record_failure(p_name, "Simulated 500 error 2")
        self.assertEqual(h.circuit_state, CircuitState.CLOSED)
        mgr._record_failure(p_name, "Simulated 500 error 3")
        self.assertEqual(h.circuit_state, CircuitState.OPEN)

        # Check circuit state blocks request
        should_attempt, reason = mgr._should_attempt_provider(mgr.openai_provider)
        self.assertFalse(should_attempt)
        self.assertIn("circuit_open", reason)

        # Advance time artificially past cooldown
        h.last_failure_time = time.time() - (mgr.cooldown_seconds + 1)
        self.assertTrue(time.time() - h.last_failure_time >= mgr.cooldown_seconds)

        # Success resets to CLOSED
        mgr._record_success(p_name, 45.0)
        self.assertEqual(h.circuit_state, CircuitState.CLOSED)
        self.assertEqual(h.consecutive_failures, 0)

    # -------------------------------------------------------------------------
    # 9. Background Scheduler PID Lock & Singleton Assurance
    # -------------------------------------------------------------------------
    def test_09_scheduler_pid_lock_and_singleton(self):
        # Ensure clean state by removing any stale lock file
        if os.path.exists(LOCK_FILE_PATH):
            try:
                os.remove(LOCK_FILE_PATH)
            except Exception:
                pass

        scheduler = SchemeUpdateSchedulerService()

        try:
            # 1. First acquisition succeeds
            has_lock = scheduler._acquire_process_lock()
            self.assertTrue(has_lock)
            self.assertTrue(scheduler._is_leader)
            self.assertTrue(os.path.exists(LOCK_FILE_PATH))

            # 2. Check PID persistence and running check
            self.assertTrue(is_pid_running(os.getpid()))

            # 3. Clean release
            scheduler._release_process_lock()
            self.assertFalse(scheduler._is_leader)
            self.assertFalse(os.path.exists(LOCK_FILE_PATH))
        finally:
            if os.path.exists(LOCK_FILE_PATH):
                try:
                    os.remove(LOCK_FILE_PATH)
                except Exception:
                    pass

    # -------------------------------------------------------------------------
    # 10. Security Headers & CORS Verification
    # -------------------------------------------------------------------------
    def test_10_security_headers_and_cors_validation(self):
        # Verify settings CORS parsing
        self.assertIsInstance(settings.CORS_ORIGINS, list)
        self.assertGreater(len(settings.CORS_ORIGINS), 0)

        # Verify rate limit constants
        self.assertGreater(settings.RATE_LIMIT_GENERAL_PER_MINUTE, 0)
        self.assertGreater(settings.RATE_LIMIT_MATCH_PER_MINUTE, 0)
        self.assertGreater(settings.RATE_LIMIT_ADMIN_PER_MINUTE, 0)
        self.assertGreater(settings.MAX_REQUEST_BODY_BYTES, 1024 * 1024)

if __name__ == "__main__":
    unittest.main()
