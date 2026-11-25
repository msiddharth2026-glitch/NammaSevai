import os
import sys
import unittest
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings
from backend.database import SessionLocal, Base, engine
from backend.seeds.seed_data import seed_database
from backend.models.scheme import Scheme
from backend.schemas.assistant import ExtractedUserProfile, MatchRequest
from backend.routers.assistant import match_citizen_schemes
from backend.routers.admin import get_quality_benchmark_endpoint
from backend.services.matcher import matcher
from backend.services.extractor import CitizenInfoExtractor
from backend.services.profile_benchmark import ProfileBenchmarkService

class TestCitizenProfileRecommendations(unittest.TestCase):
    """
    Automated Regression Test Suite for Phase 4:
    Real-World Citizen Profile Testing & Scheme Recommendation Accuracy.
    Tests:
      - 100% State-Specific Scheme Isolation (Zero leakage between jurisdictions)
      - Central Scheme Pan-India Accessibility
      - Mandatory Criteria Enforcement (Age, Income, Gender, Landholding)
      - Incomplete Profile Follow-Up Generation
      - Multi-Scheme Ranking & Explainability
      - Multilingual Recommendation Consistency across 6 Languages
      - Edge-Case & Invalid Input Handling
      - Synthetic Quality Benchmark Execution
    """

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()
        cls.extractor = CitizenInfoExtractor()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # -------------------------------------------------------------------------
    # 1. State-Specific Scheme Isolation (Zero Cross-State Leakage)
    # -------------------------------------------------------------------------
    def test_01_state_specific_scheme_isolation(self):
        """Verify schemes exclusive to one State are never recommended to residents of another State."""
        # Citizen residing in Uttar Pradesh
        up_profile = ExtractedUserProfile(
            age=19,
            gender="female",
            state="Uttar Pradesh",
            district="Lucknow",
            school_type="government",
            education_level="college_ug"
        )
        matches, _, _ = matcher.match_schemes(db=self.db, profile=up_profile)
        matched_ids = [m.scheme_id for m in matches]

        # Tamil Nadu exclusive schemes must NEVER be recommended to UP resident
        self.assertNotIn("pudhumai-penn", matched_ids)
        self.assertNotIn("kmut-magalir", matched_ids)
        self.assertNotIn("cmchis-health", matched_ids)

        # West Bengal exclusive schemes must NEVER be recommended to UP resident
        self.assertNotIn("wb-lakshmir-bhandar", matched_ids)

        # Every state scheme recommended must match citizen's state
        for m in matches:
            if "State Government" in (m.coverage_type or ""):
                self.assertIn("Uttar Pradesh", m.coverage_type)

    def test_02_central_scheme_pan_india_accessibility(self):
        """Verify Central Government schemes are accessible to eligible citizens across diverse States."""
        test_states = ["Uttar Pradesh", "Maharashtra", "Bihar", "Tamil Nadu", "Kerala", "Assam", "Sikkim"]
        for st in test_states:
            student_profile = ExtractedUserProfile(
                age=20,
                gender="female",
                state=st,
                education_level="college_ug",
                occupation="student",
                is_student=True,
                annual_income=150000.0
            )
            matches, _, _ = matcher.match_schemes(db=self.db, profile=student_profile)
            matched_ids = [m.scheme_id for m in matches]
            # National Scholarship Portal (NSP) must be accessible pan-India
            self.assertIn(
                "nsp-post-matric-scholarship", 
                matched_ids, 
                f"NSP Post-Matric Scholarship should match in state {st}"
            )

    # -------------------------------------------------------------------------
    # 2. Mandatory Threshold Enforcement (Income, Age, Gender, Land)
    # -------------------------------------------------------------------------
    def test_03_mandatory_income_threshold_enforcement(self):
        """Verify citizens with income exceeding statutory ceilings are strictly rejected."""
        # High income individual (₹12 Lakhs) applying for Free Sewing Machine (ceiling ₹72,000)
        affluent_profile = ExtractedUserProfile(
            age=30,
            gender="female",
            state="Tamil Nadu",
            annual_income=1200000.0,
            has_tailoring_training=True
        )
        matches, _, _ = matcher.match_schemes(db=self.db, profile=affluent_profile)
        matched_ids = [m.scheme_id for m in matches]
        self.assertNotIn("sewing-machine-welfare", matched_ids)

        # Direct evaluation must explicitly label as not_eligible
        scheme = self.db.query(Scheme).filter(Scheme.id == "sewing-machine-welfare").first()
        res = matcher.evaluate_scheme_for_profile(scheme, affluent_profile)
        self.assertEqual(res.recommendation_category, "not_eligible")
        self.assertGreater(len(res.unfulfilled_conditions), 0)

    def test_04_mandatory_age_boundary_enforcement(self):
        """Verify strict enforcement of minimum age and maximum age entry limits."""
        # 1. Age ceiling violation: 65-year-old applying for PM-SYM unorganized pension (max entry age 40)
        senior_profile = ExtractedUserProfile(
            age=65,
            gender="male",
            state="Maharashtra",
            annual_income=100000.0,
            occupation="unorganized"
        )
        matches, _, _ = matcher.match_schemes(db=self.db, profile=senior_profile)
        self.assertNotIn("pm-sym-pension", [m.scheme_id for m in matches])

        # 2. Age floor violation: 14-year-old minor applying for Stand-Up India (min age 18)
        minor_profile = ExtractedUserProfile(
            age=14,
            gender="female",
            state="Karnataka",
            community_category="SC"
        )
        matches_minor, _, _ = matcher.match_schemes(db=self.db, profile=minor_profile)
        self.assertNotIn("standup-india", [m.scheme_id for m in matches_minor])

    def test_05_gender_specific_scheme_matching(self):
        """Verify gender-restricted welfare schemes reject applicants of incompatible gender."""
        # Male applicant inquiring about KMUT (women heads of family only)
        male_profile = ExtractedUserProfile(
            age=40,
            gender="male",
            state="Tamil Nadu",
            annual_income=180000.0
        )
        matches, _, _ = matcher.match_schemes(db=self.db, profile=male_profile)
        matched_ids = [m.scheme_id for m in matches]
        self.assertNotIn("kmut-magalir", matched_ids)
        self.assertNotIn("muthulakshmi-maternity", matched_ids)

        # Female applicant meets gender requirement
        female_profile = ExtractedUserProfile(
            age=40,
            gender="female",
            state="Tamil Nadu",
            annual_income=180000.0
        )
        matches_female, _, _ = matcher.match_schemes(db=self.db, profile=female_profile)
        self.assertIn("kmut-magalir", [m.scheme_id for m in matches_female])

    def test_06_landholding_ceiling_enforcement(self):
        """Verify landholding ceilings are strictly checked for small/marginal farmer schemes."""
        # Large landholder (15 acres) applying for PM-Kisan Maandhan (max 5 acres / 2 hectares)
        large_farmer = ExtractedUserProfile(
            age=35,
            gender="male",
            state="Punjab",
            occupation="farmer",
            is_farmer=True,
            landholding_acres=15.0
        )
        matches, _, _ = matcher.match_schemes(db=self.db, profile=large_farmer)
        self.assertNotIn("pm-kisan-maandhan", [m.scheme_id for m in matches])

    # -------------------------------------------------------------------------
    # 3. Incomplete Profile & Follow-Up Handling
    # -------------------------------------------------------------------------
    def test_07_incomplete_profile_follow_up_generation(self):
        """Verify missing essential attributes generate clear, non-assuming follow-up questions."""
        # Student missing school type (government vs private) and gender
        incomplete_student = "I am a 19 year old college student studying degree in Madurai."
        prof, intents, missing = self.extractor.extract(incomplete_student)
        missing_names = [m.field_name for m in missing]
        self.assertIn("school_type", missing_names)
        self.assertIn("gender", missing_names)

        # Matcher also generates localized follow-up questions
        matches, follow_ups_en, follow_ups_ta = matcher.match_schemes(db=self.db, profile=prof)
        self.assertGreater(len(follow_ups_en), 0)
        self.assertGreater(len(follow_ups_ta), 0)

    def test_08_unstated_jurisdiction_prompt(self):
        """Verify queries without stated State/UT prompt for jurisdiction without assuming default."""
        unstated_query = "I am an 18 year old girl student looking for higher education scholarships."
        prof, _, _ = self.extractor.extract(unstated_query)
        self.assertIsNone(prof.state)

        matches, follow_ups_en, follow_ups_ta = matcher.match_schemes(db=self.db, profile=prof)
        # Must prompt for state jurisdiction
        has_state_prompt = any("State or Union Territory" in q for q in follow_ups_en)
        self.assertTrue(has_state_prompt, "Should prompt for State or Union Territory")

    # -------------------------------------------------------------------------
    # 4. Multi-Scheme Ranking & Explainability
    # -------------------------------------------------------------------------
    def test_09_multi_scheme_ranking_accuracy(self):
        """Verify schemes are ranked by match status (high_potential first) and specificity."""
        # Female govt school college student in Tamil Nadu
        profile = ExtractedUserProfile(
            age=19,
            gender="female",
            state="Tamil Nadu",
            district="Madurai",
            school_type="government",
            education_level="college_ug",
            occupation="student",
            is_student=True
        )
        matches, _, _ = matcher.match_schemes(db=self.db, profile=profile)
        self.assertGreater(len(matches), 1)

        # Pudhumai Penn should be top match
        top = matches[0]
        self.assertEqual(top.scheme_id, "pudhumai-penn")
        self.assertEqual(top.match_status, "high_potential")
        self.assertGreaterEqual(top.match_confidence, 90.0)

    def test_10_explainable_match_results_and_disclaimer(self):
        """Verify recommendations include satisfied conditions, unverified items, and official disclaimer."""
        profile = ExtractedUserProfile(
            age=19,
            gender="female",
            state="Tamil Nadu",
            school_type="government",
            education_level="college_ug",
            occupation="student",
            is_student=True
        )
        matches, _, _ = matcher.match_schemes(db=self.db, profile=profile)
        top = matches[0]

        # Verify structured explainability attributes
        self.assertIn(top.recommendation_category, ["eligibility_confirmed", "potentially_eligible"])
        self.assertGreater(len(top.fulfilled_conditions), 0)
        self.assertIsNotNone(top.official_portal_url)
        self.assertIsNotNone(top.official_disclaimer)
        self.assertIn("does not constitute government approval", top.official_disclaimer)

    # -------------------------------------------------------------------------
    # 5. Edge-Cases & Input Robustness
    # -------------------------------------------------------------------------
    def test_11_edge_cases_and_invalid_inputs(self):
        """Verify system handles negative income, extreme age (>120), and conflicting inputs gracefully."""
        # 1. Negative income input
        neg_profile = ExtractedUserProfile(
            age=30,
            gender="female",
            state="Tamil Nadu",
            annual_income=-50000.0,
            has_tailoring_training=True
        )
        scheme = self.db.query(Scheme).filter(Scheme.id == "sewing-machine-welfare").first()
        res = matcher.evaluate_scheme_for_profile(scheme, neg_profile)
        self.assertEqual(res.recommendation_category, "not_eligible")

        # 2. Extreme impossible age (150 years old)
        ext_profile = ExtractedUserProfile(
            age=150,
            gender="male",
            state="Tamil Nadu",
            occupation="senior"
        )
        scheme_oap = self.db.query(Scheme).filter(Scheme.id == "oap-senior-pension").first()
        res_oap = matcher.evaluate_scheme_for_profile(scheme_oap, ext_profile)
        self.assertEqual(res_oap.recommendation_category, "not_eligible")

    # -------------------------------------------------------------------------
    # 6. Multilingual Consistency Across 6 Languages
    # -------------------------------------------------------------------------
    def test_12_multilingual_recommendation_consistency(self):
        """Verify identical profile queries in English, Tamil, Hindi, Malayalam, Tanglish, and Hinglish yield consistent matches."""
        queries = {
            "en": "19 year old girl from govt school studying college in Madurai",
            "ta": "மதுரையில் அரசுப் பள்ளியில் படித்து கல்லூரியில் பயிலும் 19 வயது மாணவி",
            "hi": "मदुरै में सरकारी स्कूल से पढ़कर कॉलेज में पढ़ने वाली 19 साल की छात्रा",
            "ml": "മധുരയിൽ സർക്കാർ സ്കൂളിൽ പഠിച്ച് കോളേജിൽ പഠിക്കുന്ന 19 വയസ്സുള്ള വിദ്യാർത്ഥിനി",
            "tanglish": "Madurai la govt school padichitu college padikira 19 vayasu girl",
            "hinglish": "Madurai mein govt school se padhkar college mein padhne wali 19 saal ki ladki"
        }

        top_schemes = {}
        for lang, text in queries.items():
            req = MatchRequest(query=text, lang=lang)
            res = match_citizen_schemes(req, db=self.db)
            self.assertGreater(res.total_potential_matches, 0)
            top_schemes[lang] = res.matches[0].scheme_id

        # Pudhumai Penn must consistently be the #1 recommendation across all 6 languages
        for lang, scheme_id in top_schemes.items():
            self.assertEqual(
                scheme_id, 
                "pudhumai-penn", 
                f"Language '{lang}' recommended '{scheme_id}' instead of 'pudhumai-penn'"
            )

    # -------------------------------------------------------------------------
    # 7. Synthetic Benchmark Suite Execution & Admin Endpoint
    # -------------------------------------------------------------------------
    def test_13_synthetic_benchmark_runner_full_pass(self):
        """Verify standard 35-persona synthetic benchmark runner passes with 100% state isolation and compliance."""
        report = ProfileBenchmarkService.run_benchmark(db=self.db)
        self.assertEqual(report["benchmark_type"], "SYNTHETIC_TEST_BENCHMARK")
        self.assertEqual(report["total_profiles_tested"], 35)
        self.assertGreaterEqual(report["overall_accuracy_percentage"], 95.0)
        self.assertEqual(report["false_positive_count"], 0)
        self.assertEqual(report["state_matching_accuracy_percentage"], 100.0)
        self.assertEqual(report["mandatory_eligibility_compliance_percentage"], 100.0)
        self.assertEqual(report["multilingual_consistency_rate_percentage"], 100.0)

    def test_14_admin_quality_benchmark_endpoint(self):
        """Verify GET /api/admin/quality-benchmark returns complete benchmark report."""
        report = get_quality_benchmark_endpoint(db=self.db, authorized=True)
        self.assertIn("benchmark_type", report)
        self.assertIn("total_profiles_tested", report)
        self.assertIn("state_matching_accuracy_percentage", report)
        self.assertIn("synthetic personas", report["notice"])

if __name__ == "__main__":
    unittest.main()
