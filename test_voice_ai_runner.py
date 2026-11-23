import os
import sys
import unittest
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.seeds.seed_data import seed_database
from backend.routers.voice import get_voice_config, synthesize_speech, transcribe_base64, SynthesizeRequest, Base64AudioRequest
from backend.routers.assistant import analyze_citizen_query, match_citizen_schemes
from backend.routers.schemes import list_schemes, get_scheme_by_id, get_scheme_documents
from backend.routers.admin import create_scheme, toggle_verification_status, delete_scheme, get_admin_stats
from backend.schemas.assistant import AnalyzeRequest, MatchRequest
from backend.schemas.scheme import SchemeCreate
from backend.services.ai_service import ai_service
from backend.services.tts_service import tts_service

class TestVoiceAndAIRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_voice_config_and_privacy(self):
        """Test voice configuration and privacy settings."""
        cfg = get_voice_config()
        self.assertTrue(cfg["voice_recognition_available"])
        self.assertTrue(cfg["tts_available"])
        self.assertIn("ta", cfg["supported_languages"])
        self.assertIn("en", cfg["supported_languages"])
        self.assertIn("tanglish", cfg["supported_languages"])
        self.assertFalse(cfg["privacy_policy"]["raw_audio_stored"])
        self.assertTrue(cfg["privacy_policy"]["consent_required"])

    def test_02_voice_tts_synthesis(self):
        """Test speech audio synthesis in Tamil."""
        # Test TTS service directly
        audio_bytes = tts_service.synthesize("வணக்கம், உங்களுக்கு தேவையான நலத்திட்டங்கள் கண்டறியப்பட்டுள்ளன.", lang="ta")
        self.assertIsNotNone(audio_bytes)
        self.assertGreater(len(audio_bytes), 100)

        # Test endpoint response
        req = SynthesizeRequest(text="வணக்கம், உங்களுக்கு தேவையான நலத்திட்டங்கள் கண்டறியப்பட்டுள்ளன.", lang="ta")
        res = synthesize_speech(req)
        self.assertEqual(res.media_type, "audio/mpeg")
        self.assertIn("Content-Disposition", res.headers)

    def test_03_assistant_analyze_tamil(self):
        """Test natural language understanding for Tamil sentence."""
        req = AnalyzeRequest(text="நான் அரசுப் பள்ளியில் படித்து தற்போது கல்லூரியில் சேர்ந்த மாணவி, எனக்கு உதவித்தொகை உண்டா?", lang="ta")
        res = analyze_citizen_query(req)
        p = res.extracted_profile
        self.assertEqual(p.gender, "female")
        self.assertEqual(p.occupation, "student")
        self.assertEqual(p.school_type, "government")
        self.assertIn("education", res.identified_categories)

    def test_04_assistant_analyze_tanglish(self):
        """Test natural language understanding for Tanglish sentence."""
        req = AnalyzeRequest(text="Naan 2 acres dryland vachirukura vivasaayi, enakku agriculture subsidy venum", lang="tanglish")
        res = analyze_citizen_query(req)
        p = res.extracted_profile
        self.assertEqual(p.occupation, "farmer")
        self.assertEqual(p.landholding_acres, 2.0)
        self.assertIn("agriculture", res.identified_categories)

    def test_05_assistant_missing_critical_info(self):
        """Test follow-up question generation when essential information is missing."""
        req = AnalyzeRequest(text="I am a college student girl looking for scholarships in Madurai.", lang="en")
        res = analyze_citizen_query(req)
        p = res.extracted_profile
        self.assertEqual(p.gender, "female")
        self.assertEqual(p.occupation, "student")
        self.assertEqual(p.district, "Madurai")
        self.assertIsNone(p.school_type)
        # Must ask whether student studied in Tamil Nadu Government school
        missing_fields = [m.field_name for m in res.missing_critical_info]
        self.assertIn("school_type", missing_fields)
        self.assertGreater(len(res.follow_up_questions_en), 0)
        self.assertGreater(len(res.follow_up_questions_ta), 0)

    def test_06_scheme_matching_structured_rules(self):
        """Test matching schemes using structured eligibility conditions."""
        req = MatchRequest(query="19 year old girl from govt school studying in college degree", lang="en")
        res = match_citizen_schemes(req, db=self.db)
        self.assertGreater(res.total_potential_matches, 0)
        top = res.matches[0]
        self.assertEqual(top.scheme_id, "pudhumai-penn")
        self.assertEqual(top.match_status, "high_potential")
        self.assertGreaterEqual(top.match_confidence, 90.0)
        self.assertIn("₹1,000 / month", top.benefit_amount)
        self.assertGreater(len(top.required_documents), 0)
        self.assertGreater(len(top.application_steps), 0)
        self.assertIn("penkalvi.tn.gov.in", top.official_portal_url)
        self.assertIn("Notice", res.disclaimer)
        self.assertIn("குறிப்பு", res.disclaimer_ta)

    def test_07_schemes_list_and_details(self):
        """Test GET /api/schemes and GET /api/schemes/{id}."""
        schemes = list_schemes(db=self.db)
        self.assertGreater(len(schemes), 0)
        s = get_scheme_by_id("kmut-magalir", db=self.db)
        self.assertEqual(s.id, "kmut-magalir")
        self.assertGreater(len(s.conditions), 0)
        self.assertGreater(len(s.documents), 0)
        self.assertGreater(len(s.steps), 0)
        self.assertIsNotNone(s.source)
        # Test documents endpoint
        docs = get_scheme_documents("kmut-magalir", db=self.db)
        self.assertGreater(len(docs), 0)

    def test_08_admin_lifecycle(self):
        """Test POST /api/admin/schemes, toggle-status, and DELETE."""
        payload = SchemeCreate(
            id="test-sports-scheme",
            name="Tamil Nadu Sports Talent Scholarship",
            name_ta="விளையாட்டு உதவித்தொகை திட்டம்",
            department="Sports Department",
            department_ta="விளையாட்டுத்துறை",
            category="education",
            benefit_amount="₹10,000 / year",
            benefit_summary="Annual aid for sports students",
            benefit_summary_ta="விளையாட்டு மாணவர்களுக்கு ஆண்டு உதவி",
            description="Scheme for athletic youth.",
            description_ta="விளையாட்டு வீரர்களுக்கான திட்டம்.",
            is_active=True,
            conditions=[],
            documents=[],
            steps=[]
        )
        created = create_scheme(payload, db=self.db, authorized=True)
        self.assertEqual(created.id, "test-sports-scheme")

        # Toggle status
        toggled = toggle_verification_status("test-sports-scheme", db=self.db, authorized=True)
        self.assertIn("verification_status", toggled)

        # Delete
        del_res = delete_scheme("test-sports-scheme", db=self.db, authorized=True)
        self.assertIn("deleted successfully", del_res["message"])

        # Stats
        stats = get_admin_stats(db=self.db)
        self.assertGreater(stats["total_schemes"], 0)

    def test_09_gemini_api_integration_check(self):
        """Test Gemini API integration status and instruction fallback."""
        configured = ai_service.is_api_configured()
        instructions = ai_service.get_configuration_instruction()
        if not configured:
            self.assertIsNotNone(instructions)
            self.assertEqual(instructions["status"], "unconfigured")
            self.assertIn("GEMINI_API_KEY", instructions["env_variable"])
            self.assertIn("aistudio.google.com", instructions["docs_url"])
        else:
            self.assertIsNone(instructions)

if __name__ == "__main__":
    unittest.main()
