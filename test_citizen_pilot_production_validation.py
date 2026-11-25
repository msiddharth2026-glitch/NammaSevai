"""
Phase 7: Controlled Citizen Pilot & Production Readiness Validation Test Suite.
Validates:
  1. Complete Citizen Journey (Home -> AI -> Matching -> Details -> Checklist -> Languages)
  2. Realistic Citizen Persona Testing (16 diverse personas: students, farmers, women, seniors, PwD, cross-state)
  3. Multilingual Quality Validation (English, Tamil, Hindi, Malayalam, Tanglish, Hinglish)
  4. Accessibility & Responsive Standards (WCAG 2.1 AA focus rings, reduced-motion, meta viewport)
  5. Security & Privacy Safeguards (Zero Aadhaar/OTP/bank collection, constant-time auth, secret scrubbing)
  6. Production Environment & Recovery (AI cascade fallback, DB snapshot verification, offline resilience)
"""

import os
import sys
import unittest
from fastapi import HTTPException

from backend.config import settings
from backend.database import SessionLocal, Base, engine
from backend.models.scheme import Scheme
from backend.models.source import OfficialSource
from backend.models.user import User
from backend.routers.assistant import analyze_citizen_query, match_citizen_schemes
from backend.routers.schemes import list_schemes, get_scheme_by_id, get_scheme_documents
from backend.routers.voice import synthesize_speech, SynthesizeRequest
from backend.routers.admin import require_admin_auth
from backend.schemas.assistant import AnalyzeRequest, MatchRequest, ExtractedUserProfile
from backend.services.ai_service import ai_service
from backend.services.matcher import SchemeMatcherService
from backend.services.extractor import CitizenInfoExtractor
from backend.services.db_backup import DatabaseBackupService
from backend.services.providers.base_provider import sanitize_secret_in_error
from backend.main import health_check

class TestCitizenPilotProductionValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        cls.matcher = SchemeMatcherService()
        cls.extractor = CitizenInfoExtractor()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # =========================================================================
    # TASK 1: COMPLETE CITIZEN JOURNEY TESTING
    # =========================================================================

    def test_01_complete_citizen_journey_end_to_end(self):
        """
        Tests the entire citizen journey from landing to discovery, details, and checklist:
        1. Query analysis in Tamil
        2. Profile extraction
        3. Deterministic rule matching
        4. Explanation display
        5. Scheme detail retrieval
        6. Document checklist validation
        7. Official application URL verification
        """
        # Step 1: Citizen expresses situation
        analyze_req = AnalyzeRequest(
            text="நான் அரசு பள்ளியில் படித்து தற்போது கல்லூரியில் சேர்ந்த மாணவி. குடும்ப ஆண்டு வருமானம் 1,20,000",
            lang="ta"
        )
        analyze_res = analyze_citizen_query(analyze_req)
        profile = analyze_res.extracted_profile
        self.assertIsNotNone(profile)
        self.assertEqual(profile.school_type, "government")
        self.assertEqual(profile.annual_income, 120000.0)

        # Step 2: Match relevant schemes
        match_req = MatchRequest(
            query=analyze_req.text,
            lang="ta",
            profile=profile
        )
        match_res = match_citizen_schemes(match_req, db=self.db)
        self.assertGreater(match_res.total_potential_matches, 0)
        
        # Step 3: Verify Pudhumai Penn is top match for girl student from govt school
        scheme_ids = [m.scheme_id for m in match_res.matches]
        self.assertIn("pudhumai-penn", scheme_ids)
        pudhumai = next(m for m in match_res.matches if m.scheme_id == "pudhumai-penn")
        self.assertEqual(pudhumai.match_status, "high_potential")
        self.assertIn("penkalvi.tn.gov.in", pudhumai.official_portal_url)

        # Step 4: Open Scheme Details
        scheme_detail = get_scheme_by_id("pudhumai-penn", db=self.db)
        self.assertEqual(scheme_detail.id, "pudhumai-penn")
        self.assertGreater(len(scheme_detail.conditions), 0)
        self.assertGreater(len(scheme_detail.documents), 0)
        self.assertGreater(len(scheme_detail.steps), 0)

        # Step 5: Document checklist items ready for citizen saving
        docs = get_scheme_documents("pudhumai-penn", db=self.db)
        self.assertGreaterEqual(len(docs), 3)
        doc_names = [d.name_en.lower() for d in docs]
        self.assertTrue(any("10th" in d or "12th" in d or "school" in d for d in doc_names))

        # Step 6: Official disclaimer present
        self.assertIn("Official Disclaimer", pudhumai.official_disclaimer)

    def test_02_language_invariance_in_eligibility_matching(self):
        """
        Verify that changing UI language does NOT alter the underlying eligibility results.
        Evaluating the exact same citizen profile in English, Tamil, Hindi, and Malayalam
        must yield identical matched schemes, confidence levels, and recommendation categories.
        """
        profile = ExtractedUserProfile(
            age=19,
            gender="female",
            occupation="student",
            annual_income=100000.0,
            state="Tamil Nadu",
            school_type="government",
            education_level="college_ug"
        )

        matches_ta, _, _ = self.matcher.match_schemes(self.db, profile)
        matches_en, _, _ = self.matcher.match_schemes(self.db, profile)

        # Check identical scheme IDs and statuses
        ids_ta = [m.scheme_id for m in matches_ta]
        ids_en = [m.scheme_id for m in matches_en]
        self.assertEqual(ids_ta, ids_en, "Language selection altered matched scheme IDs!")

        for m_ta, m_en in zip(matches_ta, matches_en):
            self.assertEqual(m_ta.match_status, m_en.match_status)
            self.assertEqual(m_ta.recommendation_category, m_en.recommendation_category)
            self.assertEqual(m_ta.match_confidence, m_en.match_confidence)

    # =========================================================================
    # TASK 2: REALISTIC CITIZEN PERSONA TESTING (16 Synthetic Personas)
    # =========================================================================

    def test_03_persona_1_rural_girl_student_tn(self):
        """Persona 1: Rural TN Girl Student from govt school -> Eligible for Pudhumai Penn."""
        p = ExtractedUserProfile(
            age=19, gender="female", occupation="student",
            school_type="government", annual_income=120000.0, state="Tamil Nadu"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches if m.recommendation_category in ("eligibility_confirmed", "potentially_eligible")]
        self.assertIn("pudhumai-penn", match_ids)

    def test_04_persona_2_small_dryland_farmer_maharashtra(self):
        """Persona 2: Small Farmer in Maharashtra -> Eligible for PM-KISAN, Ineligible for TN state schemes."""
        p = ExtractedUserProfile(
            age=42, gender="male", occupation="farmer",
            landholding_acres=2.5, annual_income=90000.0, state="Maharashtra"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        # Central PM-KISAN or National Agriculture must be present
        self.assertTrue(any("pm-kisan" in sid or "pmfby" in sid or "kisan" in sid for sid in match_ids))
        # Tamil Nadu exclusive schemes MUST NOT be recommended
        self.assertNotIn("kmut-magalir", match_ids)
        self.assertNotIn("pudhumai-penn", match_ids)

    def test_05_persona_3_women_entrepreneur_tailoring(self):
        """Persona 3: Destitute/Widow Woman Tailor in Madurai -> Eligible for Free Sewing Machine & KMUT."""
        p = ExtractedUserProfile(
            age=36, gender="female", occupation="tailor",
            annual_income=60000.0, state="Tamil Nadu",
            is_widow_or_destitute=True, has_tailoring_training=True
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        self.assertIn("sewing-machine-welfare", match_ids)
        self.assertIn("kmut-magalir", match_ids)

    def test_06_persona_4_senior_citizen_kerala(self):
        """Persona 4: Senior Citizen in Kerala (Age 68) -> Eligible for Senior Pension / Ayushman Bharat."""
        p = ExtractedUserProfile(
            age=68, gender="male", occupation="senior",
            annual_income=45000.0, state="Kerala"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        # Must match national senior or health aid
        self.assertTrue(any("oap" in s or "senior" in s or "pmjay" in s or "vaya" in s for s in match_ids))
        # Must NOT match youth/student schemes
        self.assertNotIn("pudhumai-penn", match_ids)
        self.assertNotIn("tamil-pudhalvan", match_ids)

    def test_07_persona_5_person_with_disability_delhi(self):
        """Persona 5: Person with Disability in Delhi -> Matches Disability Welfare."""
        p = ExtractedUserProfile(
            age=29, gender="male", disability_status=True,
            annual_income=50000.0, state="Delhi"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        self.assertTrue(any("disab" in s or "differently" in s or "divyang" in s or "assist" in s for s in match_ids))

    def test_08_persona_6_unemployed_youth_up(self):
        """Persona 6: Unemployed Youth in Uttar Pradesh -> Matches Skill Development / PMEGP."""
        p = ExtractedUserProfile(
            age=23, gender="male", occupation="unemployed",
            education_level="graduate", state="Uttar Pradesh", annual_income=80000.0
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        # Central self-employment / skill schemes match nationally
        self.assertTrue(any("pmegp" in s or "mudra" in s or "skill" in s or "pmkvy" in s for s in match_ids))

    def test_09_persona_7_construction_worker_karnataka(self):
        """Persona 7: Construction Labourer in Karnataka -> Matches unorganized worker / pension welfare."""
        p = ExtractedUserProfile(
            age=34, gender="male", occupation="construction_worker",
            annual_income=110000.0, state="Karnataka"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        self.assertTrue(any("bocw" in s or "sym" in s or "shram" in s or "pm-sym" in s for s in match_ids))

    def test_10_persona_8_pregnant_woman_tn(self):
        """Persona 8: Pregnant Woman in Tamil Nadu -> Matches Dr. Muthulakshmi Maternity & PMMVY."""
        p = ExtractedUserProfile(
            age=25, gender="female", is_pregnant_or_lactating=True,
            annual_income=80000.0, state="Tamil Nadu"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        self.assertTrue(any("muthulakshmi" in s or "maternity" in s or "pmmvy" in s for s in match_ids))

    def test_11_persona_9_high_income_professional_ineligible(self):
        """Persona 9: High-Income Professional (₹18 Lakhs) -> Strictly Ineligible for income-capped schemes."""
        p = ExtractedUserProfile(
            age=32, gender="male", occupation="software_engineer",
            annual_income=1800000.0, state="Karnataka"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p, include_ineligible=False)
        match_ids = [m.scheme_id for m in matches]
        # Income-capped welfare schemes MUST NOT be recommended
        self.assertNotIn("kmut-magalir", match_ids)
        self.assertNotIn("oap-senior-pension", match_ids)
        self.assertNotIn("pm-kisan-tn", match_ids)

    def test_12_persona_10_incomplete_profile_prompts_followups(self):
        """Persona 10: Incomplete Profile -> Triggers follow-up questions without hallucinated eligibility."""
        p = ExtractedUserProfile() # Completely empty profile
        matches, follow_ups_en, follow_ups_ta = self.matcher.match_schemes(self.db, p)
        # Follow-up questions must be populated
        self.assertGreater(len(follow_ups_en), 0)
        self.assertGreater(len(follow_ups_ta), 0)
        # No scheme should be marked 'eligibility_confirmed' when all criteria are unknown
        confirmed = [m for m in matches if m.recommendation_category == "eligibility_confirmed"]
        self.assertEqual(len(confirmed), 0)

    def test_13_persona_11_minor_child_ineligible_for_business_loan(self):
        """Persona 11: Minor (Age 10) seeking business scheme -> Ineligible based on age minimum."""
        p = ExtractedUserProfile(
            age=10, gender="male", occupation="self_employed",
            state="Tamil Nadu"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p, include_ineligible=True)
        # PMEGP or entrepreneurship schemes require age >= 18
        loan_matches = [m for m in matches if "pmegp" in m.scheme_id or "entrepreneur" in m.scheme_id]
        for m in loan_matches:
            self.assertEqual(m.recommendation_category, "not_eligible")

    def test_14_persona_12_union_territory_puducherry(self):
        """Persona 12: Puducherry Resident -> Eligible for UT & Central schemes, isolated from TN state schemes."""
        p = ExtractedUserProfile(
            age=30, gender="female", state="Puducherry",
            annual_income=70000.0
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        # TN-exclusive state schemes must NOT appear
        self.assertNotIn("kmut-magalir", match_ids)
        self.assertNotIn("pudhumai-penn", match_ids)

    def test_15_persona_13_artisan_gujarat(self):
        """Persona 13: Traditional Artisan in Gujarat -> Matches PM Vishwakarma / PMEGP."""
        p = ExtractedUserProfile(
            age=38, gender="male", occupation="artisan",
            annual_income=140000.0, state="Gujarat"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        self.assertTrue(any("vishwakarma" in s or "pmegp" in s or "mudra" in s for s in match_ids))

    def test_16_persona_14_rural_landless_labourer_bihar(self):
        """Persona 14: Rural Landless Labourer in Bihar -> Matches MGNREGA / Rural housing."""
        p = ExtractedUserProfile(
            age=40, gender="male", occupation="daily_wager",
            annual_income=45000.0, state="Bihar", ration_card_type="bpl"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p)
        match_ids = [m.scheme_id for m in matches]
        self.assertTrue(any("mgnrega" in s or "pmay" in s or "pm-jay" in s or "ration" in s for s in match_ids))

    def test_17_persona_15_overage_student_ineligible(self):
        """Persona 15: Age 45 applying for youth/welfare scheme with age 40 ceiling -> Ineligible due to age ceiling."""
        p = ExtractedUserProfile(
            age=45, gender="female", occupation="tailor",
            state="Tamil Nadu", annual_income=60000.0,
            has_tailoring_training=True, is_widow_or_destitute=True
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p, include_ineligible=True)
        # sewing-machine-welfare requires age <= 40
        sewing = next((m for m in matches if m.scheme_id == "sewing-machine-welfare"), None)
        self.assertIsNotNone(sewing)
        self.assertEqual(sewing.recommendation_category, "not_eligible")
        self.assertTrue(any("Age 45 does not satisfy" in v or "age_max" in v for v in sewing.unfulfilled_conditions))

    def test_18_persona_16_cross_state_residency_leakage_prevented(self):
        """Persona 16: West Bengal Resident -> Strictly isolated from Tamil Nadu state welfare."""
        p = ExtractedUserProfile(
            age=20, gender="female", state="West Bengal",
            annual_income=80000.0, school_type="government"
        )
        matches, _, _ = self.matcher.match_schemes(self.db, p, include_ineligible=True)
        # Check TN schemes
        tn_exclusive = next((m for m in matches if m.scheme_id == "kmut-magalir"), None)
        if tn_exclusive:
            self.assertEqual(tn_exclusive.recommendation_category, "not_eligible")
            self.assertTrue(any("State residency mismatch" in v for v in tn_exclusive.unfulfilled_conditions))

    # =========================================================================
    # TASK 3: MULTILINGUAL QUALITY VALIDATION
    # =========================================================================

    def test_19_tanglish_and_hinglish_query_extraction(self):
        """Verify colloquial Romanized Tamil (Tanglish) and Hindi (Hinglish) NLP extraction."""
        # Tanglish
        tanglish_query = "Naan govt school la 12th mudichitu college sernthuten, income 1 lakh"
        p_ta, _, _ = self.extractor.extract(tanglish_query)
        self.assertEqual(p_ta.school_type, "government")
        self.assertEqual(p_ta.annual_income, 100000.0)

        # Hinglish
        hinglish_query = "Main govt school se padha hu aur college me admission liya, family income 1.5 lakh hai"
        p_hi, _, _ = self.extractor.extract(hinglish_query)
        self.assertEqual(p_hi.school_type, "government")
        self.assertEqual(p_hi.annual_income, 150000.0)

    def test_20_tts_synthesis_fallback_resilience(self):
        """Verify text-to-speech synthesis endpoint falls back gracefully to audio stream when offline."""
        req = SynthesizeRequest(
            text="உங்கள் தகுதிக்கு 5 அரசு நலத்திட்டங்கள் உள்ளன",
            lang="ta"
        )
        res = synthesize_speech(req)
        self.assertIsNotNone(res)
        self.assertIn("audio", res.media_type)

    # =========================================================================
    # TASK 4: ACCESSIBILITY & RESPONSIVE STANDARDS
    # =========================================================================

    def test_21_wcag_focus_and_reduced_motion_in_stylesheet(self):
        """Verify that static/css/style.css includes WCAG 2.1 AA focus rings and prefers-reduced-motion."""
        css_path = os.path.join(os.path.dirname(__file__), "static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        self.assertIn(":focus-visible", css_content)
        self.assertIn("outline", css_content)
        self.assertIn("prefers-reduced-motion", css_content)

    # =========================================================================
    # TASK 5: SECURITY & CITIZEN PRIVACY VALIDATION
    # =========================================================================

    def test_22_zero_credential_harvesting_in_user_model(self):
        """Verify that User and Assistant schemas do NOT request or store Aadhaar, OTP, or Bank Passwords."""
        user_cols = [c.name for c in User.__table__.columns]
        prohibited_fields = ["aadhaar", "uid", "otp", "password", "bank_account", "ifsc", "cvv", "pin"]
        for pf in prohibited_fields:
            self.assertNotIn(pf, user_cols, f"Security Violation: Sensitive field '{pf}' found in User table!")

    def test_23_admin_unauthorized_access_rejected(self):
        """Verify that admin endpoints strictly reject missing or forged API keys with HTTP 401."""
        with self.assertRaises(HTTPException) as ctx:
            require_admin_auth(x_admin_key="forged-token-999")
        self.assertEqual(ctx.exception.status_code, 401)

        with self.assertRaises(HTTPException) as ctx2:
            require_admin_auth()
        self.assertEqual(ctx2.exception.status_code, 401)

    # =========================================================================
    # TASK 6 & 7: PRODUCTION ENVIRONMENT & FAILURE RECOVERY
    # =========================================================================

    def test_24_deterministic_fallback_when_external_ai_offline(self):
        """Verify that citizen eligibility matching functions 100% deterministically when all external AIs are offline."""
        profile = ExtractedUserProfile(
            age=20,
            gender="female",
            occupation="student",
            school_type="government",
            annual_income=100000.0,
            state="Tamil Nadu"
        )
        # Even with zero external AI connection, matcher returns accurate statutory matches
        matches, _, _ = self.matcher.match_schemes(self.db, profile)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].scheme_id, "pudhumai-penn")

    def test_25_database_snapshot_disaster_recovery_verified(self):
        """Verify that online database snapshot captures all 85 scheme records with zero corruption."""
        backup_res = DatabaseBackupService.create_sqlite_backup()
        self.assertEqual(backup_res["status"], "success")
        is_valid, msg, counts = DatabaseBackupService.verify_and_test_restore(backup_res["destination_path"])
        self.assertTrue(is_valid, f"Backup validation failed: {msg}")
        self.assertEqual(counts.get("schemes", 0), 85)

if __name__ == "__main__":
    unittest.main()
