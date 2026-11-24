import os
import sys
import unittest
import base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import engine, Base
from backend.seeds.seed_data import seed_database

class TestVoiceAndAIBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.client = TestClient(app, raise_server_exceptions=False)

    def test_01_voice_config_endpoint(self):
        res = self.client.get("/api/voice/config")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["voice_recognition_available"])
        self.assertTrue(data["tts_available"])
        self.assertIn("privacy_policy", data)
        self.assertFalse(data["privacy_policy"]["raw_audio_stored"])
        self.assertIn("ta", data["supported_languages"])

    def test_02_tts_synthesize_endpoint(self):
        # Test real Tamil Text-To-Speech generation
        res = self.client.post("/api/voice/synthesize", json={
            "text": "வணக்கம், உங்களுக்கு தேவையான நலத்திட்டங்கள் கண்டறியப்பட்டுள்ளன.",
            "lang": "ta"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "audio/mpeg")
        self.assertGreater(len(res.content), 100)  # Real MP3 audio stream returned

    def test_03_assistant_analyze_tanglish(self):
        # Test Tanglish input understanding
        res = self.client.post("/api/assistant/analyze", json={
            "text": "Naan 2 acres dryland vachirukura vivasaayi, enakku agriculture subsidy venum",
            "lang": "tanglish"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        profile = data["extracted_profile"]
        self.assertEqual(profile["occupation"], "farmer")
        self.assertEqual(profile["landholding_acres"], 2.0)
        self.assertIn("agriculture", data["identified_categories"])

    def test_04_assistant_match_structured_explanation(self):
        # Match for senior citizen
        res = self.client.post("/api/assistant/match", json={
            "query": "65 years old destitute elder person looking for pension",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_potential_matches"], 0)
        top = data["matches"][0]
        self.assertEqual(top["scheme_id"], "oap-senior-pension")
        self.assertIn("potential", top["match_status"])
        self.assertIn("oap", top["official_portal_url"].lower() + top["scheme_id"].lower())
        self.assertIn("disclaimer", data)

    def test_05_schemes_and_documents(self):
        res = self.client.get("/api/schemes/kmut-magalir/documents")
        self.assertEqual(res.status_code, 200)
        docs = res.json()
        doc_names = [d["name_en"] for d in docs]
        self.assertTrue(any("Ration Card" in d for d in doc_names))

    def test_06_admin_lifecycle(self):
        # Create
        new_scheme = {
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
        headers = {"X-Admin-Key": "nammasevai-admin-secret-2026"}
        res = self.client.post("/api/admin/schemes", json=new_scheme, headers=headers)
        self.assertEqual(res.status_code, 201)

        # Toggle status
        res = self.client.post("/api/admin/schemes/tn-green-fellowship/toggle-status", headers=headers)
        self.assertEqual(res.status_code, 200)

        # Delete
        res = self.client.delete("/api/admin/schemes/tn-green-fellowship", headers=headers)
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
