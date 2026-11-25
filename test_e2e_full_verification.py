import os
import sys
import unittest
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings
from backend.database import SessionLocal, Base, engine
from backend.seeds.seed_data import seed_database
from backend.routers.voice import get_voice_config, synthesize_speech, SynthesizeRequest
from backend.routers.assistant import analyze_citizen_query, match_citizen_schemes
from backend.routers.schemes import list_schemes, get_scheme_by_id, get_scheme_documents
from backend.routers.admin import (
    create_scheme, 
    update_scheme,
    toggle_verification_status, 
    delete_scheme, 
    get_admin_stats,
    require_admin_auth
)
from backend.schemas.assistant import AnalyzeRequest, MatchRequest
from backend.schemas.scheme import SchemeCreate, SchemeUpdate
from backend.services.ai_service import ai_service
from backend.services.tts_service import tts_service
from backend.main import health_check

class TestNammaSevaiFullE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # ---------------------------------------------------------
    # 1. Health & Database Connectivity
    # ---------------------------------------------------------
    def test_01_health_and_database_dialect(self):
        """Verify health check reports connected database and dialect."""
        res = health_check()
        self.assertEqual(res["status"], "healthy")
        self.assertEqual(res["app"], settings.APP_NAME)
        self.assertEqual(res["database"], "connected")
        self.assertIn(res["dialect"], ["sqlite", "postgresql"])

    # ---------------------------------------------------------
    # 2. Scheme Catalog & Document Checklist
    # ---------------------------------------------------------
    def test_02_all_twelve_schemes_present(self):
        """Verify all 12 authentic Tamil Nadu welfare schemes are in database."""
        schemes = list_schemes(limit=100, offset=0, db=self.db)
        self.assertGreaterEqual(len(schemes), 12)
        scheme_ids = [s.id for s in schemes]
        
        expected_ids = [
            "pudhumai-penn",
            "kmut-magalir",
            "cmchis-health",
            "sewing-machine-welfare",
            "pm-kisan-tn",
            "naan-mudhalvan",
            "muthulakshmi-maternity",
            "oap-senior-pension",
            "differently-abled-welfare",
            "aabcs-scst-entrepreneur",
            "tamil-pudhalvan",
            "kalaignar-kanavu-illam"
        ]
        for sid in expected_ids:
            self.assertIn(sid, scheme_ids, f"Expected scheme {sid} was not found in catalog")

    def test_03_scheme_category_and_search_filtering(self):
        """Verify category filtering and keyword search."""
        # Category filter: women
        women_schemes = list_schemes(category="women", limit=50, offset=0, db=self.db)
        self.assertGreater(len(women_schemes), 0)
        for s in women_schemes:
            self.assertEqual(s.category, "women")

        # Keyword search: "தையல்" (sewing in Tamil)
        tailor_schemes = list_schemes(search="தையல்", limit=50, offset=0, db=self.db)
        self.assertGreater(len(tailor_schemes), 0)
        self.assertIn("sewing-machine-welfare", [s.id for s in tailor_schemes])

    def test_04_scheme_details_and_required_documents(self):
        """Verify scheme details, criteria, and document checklist."""
        scheme = get_scheme_by_id("pudhumai-penn", db=self.db)
        self.assertEqual(scheme.id, "pudhumai-penn")
        self.assertIn("Moovalur", scheme.name)
        self.assertIn("புதுமைப் பெண்", scheme.name_ta)
        self.assertGreater(len(scheme.conditions), 0)
        self.assertGreater(len(scheme.documents), 0)
        self.assertGreater(len(scheme.steps), 0)
        self.assertIsNotNone(scheme.source)
        self.assertIn("penkalvi.tn.gov.in", scheme.source.portal_url)

        # Document checklist endpoint
        docs = get_scheme_documents("pudhumai-penn", db=self.db)
        self.assertGreaterEqual(len(docs), 4)
        doc_names = [d.name_en for d in docs]
        self.assertIn("Aadhaar Card", doc_names)

    # ---------------------------------------------------------
    # 3. AI Natural Language Understanding & Profile Extraction
    # ---------------------------------------------------------
    def test_05_assistant_tamil_query_extraction(self):
        """Citizen query in colloquial Tamil -> extracted structured profile."""
        req = AnalyzeRequest(
            text="நான் அரசுப் பள்ளியில் படித்து தற்போது கல்லூரியில் சேர்ந்த மாணவி, எனக்கு உதவித்தொகை உண்டா?",
            lang="ta"
        )
        res = analyze_citizen_query(req)
        p = res.extracted_profile
        self.assertEqual(p.gender, "female")
        self.assertEqual(p.occupation, "student")
        self.assertEqual(p.school_type, "government")
        self.assertIn("education", res.identified_categories)

    def test_06_assistant_tanglish_query_extraction(self):
        """Citizen query in Tanglish -> extracted structured profile."""
        req = AnalyzeRequest(
            text="naan 2 acres dryland vachirukura vivasaayi, enakku agriculture subsidy venum",
            lang="tanglish"
        )
        res = analyze_citizen_query(req)
        p = res.extracted_profile
        self.assertEqual(p.occupation, "farmer")
        self.assertEqual(p.landholding_acres, 2.0)
        self.assertIn("agriculture", res.identified_categories)

    def test_07_assistant_english_query_extraction(self):
        """Citizen query in English -> extracted structured profile."""
        req = AnalyzeRequest(
            text="I am a destitute widow with tailoring training certificate looking for self-employment help.",
            lang="en"
        )
        res = analyze_citizen_query(req)
        p = res.extracted_profile
        self.assertEqual(p.gender, "female")
        self.assertTrue(p.is_widow_or_destitute)
        self.assertTrue(p.has_tailoring_training)
        self.assertIn("women", res.identified_categories)

    def test_08_assistant_missing_critical_info_detection(self):
        """Essential criteria missing -> generates targeted follow-up questions."""
        req = AnalyzeRequest(
            text="I am a college girl looking for monthly education allowance.",
            lang="en"
        )
        res = analyze_citizen_query(req)
        p = res.extracted_profile
        self.assertEqual(p.gender, "female")
        self.assertEqual(p.occupation, "student")
        self.assertIsNone(p.school_type)

        # school_type must be flagged as missing for Pudhumai Penn
        missing_names = [m.field_name for m in res.missing_critical_info]
        self.assertIn("school_type", missing_names)
        self.assertGreater(len(res.follow_up_questions_en), 0)
        self.assertGreater(len(res.follow_up_questions_ta), 0)

    # ---------------------------------------------------------
    # 4. Scheme Matching with Structured Eligibility Rules
    # ---------------------------------------------------------
    def test_09_scheme_matching_pudhumai_penn(self):
        """Structured rule matching for Pudhumai Penn."""
        req = MatchRequest(
            query="19 year old girl from govt school studying in college degree in Chennai",
            lang="en"
        )
        res = match_citizen_schemes(req, db=self.db)
        self.assertGreater(res.total_potential_matches, 0)
        top = res.matches[0]
        self.assertEqual(top.scheme_id, "pudhumai-penn")
        self.assertEqual(top.match_status, "high_potential")
        self.assertGreaterEqual(top.match_confidence, 85.0)
        self.assertIn("penkalvi.tn.gov.in", top.official_portal_url)

    def test_10_scheme_matching_tamil_pudhalvan(self):
        """Structured rule matching for Tamil Pudhalvan (boys higher education)."""
        req = MatchRequest(
            query="நான் அரசு பள்ளியில் படித்து தற்போது பாலிடெக்னிக் கல்லூரியில் படிக்கும் மாணவன்",
            lang="ta"
        )
        res = match_citizen_schemes(req, db=self.db)
        matched_ids = [m.scheme_id for m in res.matches]
        self.assertIn("tamil-pudhalvan", matched_ids)

    def test_11_scheme_matching_free_sewing_machine(self):
        """Structured rule matching for Free Sewing Machine Scheme."""
        req = MatchRequest(
            query="நான் விதவை பெண், 6 மாத தையல் பயிற்சி முடித்துள்ளேன், ஆண்டு வருமானம் ₹50,000",
            lang="ta"
        )
        res = match_citizen_schemes(req, db=self.db)
        matched_ids = [m.scheme_id for m in res.matches]
        self.assertIn("sewing-machine-welfare", matched_ids)

    # ---------------------------------------------------------
    # 5. Voice Features & Ephemeral Audio Handling
    # ---------------------------------------------------------
    def test_12_voice_config_and_privacy_policy(self):
        """Verify voice endpoints provide ephemeral guarantees and setup instructions."""
        cfg = get_voice_config()
        self.assertTrue(cfg["voice_recognition_available"])
        self.assertTrue(cfg["tts_available"])
        self.assertIn("ta", cfg["supported_languages"])
        self.assertIn("en", cfg["supported_languages"])
        self.assertIn("tanglish", cfg["supported_languages"])
        # Privacy policy guarantees
        self.assertTrue(cfg["privacy_policy"]["consent_required"])
        self.assertFalse(cfg["privacy_policy"]["raw_audio_stored"])

    def test_13_tts_audio_synthesis_tamil_and_english(self):
        """Verify TTS synthesis generates playable MP3 stream."""
        # Tamil TTS
        req_ta = SynthesizeRequest(text="உங்கள் தகுதி சரிபார்க்கப்பட்டது.", lang="ta")
        res_ta = synthesize_speech(req_ta)
        self.assertEqual(res_ta.media_type, "audio/mpeg")

        # English TTS
        req_en = SynthesizeRequest(text="Your welfare scheme results are ready.", lang="en")
        res_en = synthesize_speech(req_en)
        self.assertEqual(res_en.media_type, "audio/mpeg")

    # ---------------------------------------------------------
    # 6. Admin Authentication & CRUD Operations
    # ---------------------------------------------------------
    def test_14_admin_auth_rejection(self):
        """Admin mutation endpoints must reject requests with invalid or missing key."""
        # Missing key
        with self.assertRaises(HTTPException) as ctx:
            require_admin_auth(x_admin_key=None)
        self.assertEqual(ctx.exception.status_code, 401)

        # Incorrect key
        with self.assertRaises(HTTPException) as ctx:
            require_admin_auth(x_admin_key="wrong-admin-key")
        self.assertEqual(ctx.exception.status_code, 401)

        # Valid key
        auth_success = require_admin_auth(x_admin_key=settings.ADMIN_API_KEY)
        self.assertTrue(auth_success)

    def test_15_admin_crud_lifecycle(self):
        """Admin scheme create, update, status toggle, and delete lifecycle."""
        test_scheme_id = "test-solar-pump-scheme"
        
        # 1. Create
        payload = SchemeCreate(
            id=test_scheme_id,
            name="Tamil Nadu Solar Agricultural Pump Subsidy",
            name_ta="சூரிய மின் சக்தி விவசாய பம்புசெட் மானிய திட்டம்",
            department="Agriculture and Farmers Welfare Department",
            department_ta="வேளாண்மை மற்றும் உழவர் நலத்துறை",
            category="agriculture",
            benefit_amount="70% Subsidy",
            benefit_summary="70% government subsidy for off-grid solar water pumps",
            benefit_summary_ta="70% மானியத்தில் சோலார் பாசன பம்புசெட் அமைத்தல்",
            description="Promotion of solar irrigation pumps for small and marginal farmers.",
            description_ta="விவசாயிகளுக்கு இலவச மின்சாரத்துடன் சோலார் பம்புசெட் அமைக்கும் திட்டம்.",
            is_active=True,
            conditions=[],
            documents=[],
            steps=[]
        )
        created = create_scheme(payload, db=self.db, authorized=True)
        self.assertEqual(created.id, test_scheme_id)

        # 2. Update
        update_payload = SchemeUpdate(
            benefit_amount="75% Subsidy"
        )
        updated = update_scheme(test_scheme_id, update_payload, db=self.db, authorized=True)
        self.assertEqual(updated.benefit_amount, "75% Subsidy")

        # 3. Toggle Status
        toggled = toggle_verification_status(test_scheme_id, db=self.db, authorized=True)
        self.assertIn("verification_status", toggled)

        # 4. Delete
        del_res = delete_scheme(test_scheme_id, db=self.db, authorized=True)
        self.assertIn("deleted successfully", del_res["message"])

        # 5. Stats
        stats = get_admin_stats(db=self.db)
        self.assertGreaterEqual(stats["total_schemes"], 12)
        self.assertGreaterEqual(stats["active_categories"], 5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
