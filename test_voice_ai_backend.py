import os
import sys
import unittest
import base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, Base, SessionLocal
from backend.seeds.seed_data import seed_database
from backend.routers.voice import get_voice_config, synthesize_speech, SynthesizeRequest
from backend.routers.assistant import analyze_citizen_query, match_citizen_schemes
from backend.routers.schemes import get_scheme_documents
from backend.routers.admin import create_scheme, toggle_verification_status, delete_scheme
from backend.schemas.assistant import AnalyzeRequest, MatchRequest
from backend.schemas.scheme import SchemeCreate

class TestVoiceAndAIBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_voice_config_endpoint(self):
        data = get_voice_config()
        self.assertTrue(data["voice_recognition_available"])
        self.assertTrue(data["tts_available"])
        self.assertIn("privacy_policy", data)
        self.assertFalse(data["privacy_policy"]["raw_audio_stored"])
        self.assertIn("ta", data["supported_languages"])

    def test_02_tts_synthesize_endpoint(self):
        # Test real Tamil Text-To-Speech generation
        req = SynthesizeRequest(
            text="வணக்கம், உங்களுக்கு தேவையான நலத்திட்டங்கள் கண்டறியப்பட்டுள்ளன.",
            lang="ta"
        )
        res = synthesize_speech(req)
        self.assertEqual(res.media_type, "audio/mpeg")
        self.assertIn("Content-Disposition", res.headers)

    def test_03_assistant_analyze_tanglish(self):
        # Test Tanglish input understanding
        req = AnalyzeRequest(
            text="Naan 2 acres dryland vachirukura vivasaayi, enakku agriculture subsidy venum",
            lang="tanglish"
        )
        data = analyze_citizen_query(req)
        profile = data.extracted_profile
        self.assertEqual(profile.occupation, "farmer")
        self.assertEqual(profile.landholding_acres, 2.0)
        self.assertIn("agriculture", data.identified_categories)

    def test_04_assistant_match_structured_explanation(self):
        # Match for senior citizen
        req = MatchRequest(
            query="65 years old destitute elder person looking for pension",
            lang="en"
        )
        data = match_citizen_schemes(req, db=self.db)
        self.assertGreater(data.total_potential_matches, 0)
        matched_ids = [m.scheme_id for m in data.matches]
        self.assertIn("oap-senior-pension", matched_ids)
        top = next(m for m in data.matches if m.scheme_id == "oap-senior-pension")
        self.assertIn("potential", top.match_status)
        self.assertIn("oap", top.official_portal_url.lower() + top.scheme_id.lower())
        self.assertIsNotNone(data.disclaimer)

    def test_05_schemes_and_documents(self):
        docs = get_scheme_documents("kmut-magalir", db=self.db)
        doc_names = [d.name_en for d in docs]
        self.assertTrue(any("Ration Card" in d for d in doc_names))

    def test_06_admin_lifecycle(self):
        new_scheme_payload = {
            "id": "tn-green-fellowship",
            "name": "Tamil Nadu Green Fellowship Programme",
            "name_ta": "தமிழ்நாடு பசுமை உதவித்தொகை திட்டம்",
            "department": "Environment, Climate Change and Forests Department",
            "department_ta": "சுற்றுச்சூழல், காலநிலை மாற்றம் மற்றும் வனத்துறை",
            "category": "employment",
            "benefit_amount": "₹60,000 / month",
            "benefit_summary": "Fellowship for youth working on climate initiatives",
            "benefit_summary_ta": "இளைஞர்களுக்கான பசுமை சூழல் ஊக்கத்தொகை",
            "description": "Fellowship for postgraduate youth.",
            "description_ta": "முதுகலை பட்டதாரிகளுக்கான திட்டம்.",
            "is_active": True,
            "conditions": [],
            "documents": [],
            "steps": [],
            "source": {
                "source_name": "TN Climate Department",
                "portal_url": "https://environment.tn.gov.in",
                "verified_date": "2026-11-23",
                "verification_status": "verified"
            }
        }
        scheme_create_obj = SchemeCreate(**new_scheme_payload)

        # Create
        created = create_scheme(scheme_create_obj, db=self.db, authorized=True)
        self.assertEqual(created.id, "tn-green-fellowship")

        # Toggle status
        toggled = toggle_verification_status("tn-green-fellowship", db=self.db, authorized=True)
        self.assertIn("verification_status", toggled)

        # Delete
        del_res = delete_scheme("tn-green-fellowship", db=self.db, authorized=True)
        self.assertIn("deleted successfully", del_res.get("message", ""))

if __name__ == "__main__":
    unittest.main()
