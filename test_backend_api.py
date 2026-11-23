import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import engine, Base
from backend.seeds.seed_data import seed_database

class TestNammaSevaiBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.client = TestClient(app)

    def test_01_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)

    def test_02_get_schemes_list(self):
        res = self.client.get("/api/schemes")
        self.assertEqual(res.status_code, 200)
        schemes = res.json()
        self.assertIsInstance(schemes, list)
        self.assertGreater(len(schemes), 0)
        
        # Check first scheme structure
        s = schemes[0]
        self.assertIn("id", s)
        self.assertIn("name", s)
        self.assertIn("name_ta", s)
        self.assertIn("benefit_amount", s)
        self.assertIn("source_verification_status", s)

    def test_03_get_schemes_filtered_by_category(self):
        res = self.client.get("/api/schemes?category=education")
        self.assertEqual(res.status_code, 200)
        schemes = res.json()
        self.assertTrue(all(s["category"] == "education" for s in schemes))

    def test_04_get_scheme_by_id(self):
        res = self.client.get("/api/schemes/pudhumai-penn")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], "pudhumai-penn")
        self.assertIn("conditions", data)
        self.assertIn("documents", data)
        self.assertIn("steps", data)
        self.assertIn("source", data)
        self.assertGreater(len(data["conditions"]), 0)
        self.assertGreater(len(data["documents"]), 0)
        self.assertGreater(len(data["steps"]), 0)
        self.assertEqual(data["source"]["verification_status"], "verified")

    def test_05_get_scheme_not_found(self):
        res = self.client.get("/api/schemes/non-existent-scheme-999")
        self.assertEqual(res.status_code, 404)

    def test_06_get_scheme_documents(self):
        res = self.client.get("/api/schemes/pudhumai-penn/documents")
        self.assertEqual(res.status_code, 200)
        docs = res.json()
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)
        doc = docs[0]
        self.assertIn("name_en", doc)
        self.assertIn("name_ta", doc)
        self.assertIn("is_mandatory", doc)

    def test_07_assistant_analyze_tamil_query(self):
        query = "நான் அரசுப் பள்ளியில் படித்து தற்போது கல்லூரியில் சேர்ந்த மாணவி, எனக்கு உதவித்தொகை உண்டா?"
        res = self.client.post("/api/assistant/analyze", json={"text": query, "lang": "ta"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        profile = data["extracted_profile"]
        self.assertEqual(profile["gender"], "female")
        self.assertEqual(profile["occupation"], "student")
        self.assertEqual(profile["school_type"], "government")
        self.assertIn("education", data["identified_categories"])

    def test_08_assistant_analyze_missing_critical_info(self):
        # Query says student but omits school type (govt vs private)
        query = "I am a college student girl looking for scholarships in Madurai."
        res = self.client.post("/api/assistant/analyze", json={"text": query, "lang": "en"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        profile = data["extracted_profile"]
        self.assertEqual(profile["gender"], "female")
        self.assertEqual(profile["occupation"], "student")
        self.assertEqual(profile["district"], "Madurai")
        self.assertIsNone(profile["school_type"])
        
        # Follow-up questions must be present
        self.assertGreater(len(data["missing_critical_info"]), 0)
        missing_fields = [m["field_name"] for m in data["missing_critical_info"]]
        self.assertIn("school_type", missing_fields)
        self.assertGreater(len(data["follow_up_questions_en"]), 0)
        self.assertGreater(len(data["follow_up_questions_ta"]), 0)

    def test_09_assistant_match_structured_schemes(self):
        # Profile for a female govt school student in college
        req = {
            "query": "19 year old girl from govt school studying in college degree",
            "lang": "en"
        }
        res = self.client.post("/api/assistant/match", json=req)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_potential_matches"], 0)
        
        # Pudhumai Penn should be top match
        top_match = data["matches"][0]
        self.assertEqual(top_match["scheme_id"], "pudhumai-penn")
        self.assertIn(top_match["match_status"], ["high_potential", "potential_match"])
        self.assertGreaterEqual(top_match["match_confidence"], 70.0)
        self.assertIn("₹1,000 / month", top_match["benefit_amount"])
        self.assertGreater(len(top_match["required_documents"]), 0)
        self.assertGreater(len(top_match["application_steps"]), 0)
        self.assertIn("penkalvi.tn.gov.in", top_match["official_portal_url"])
        self.assertIn("disclaimer", data)
        self.assertIn("disclaimer_ta", data)

    def test_10_assistant_match_farmer_query(self):
        req = {
            "query": "நான் 2 ஏக்கர் நிலம் வைத்துள்ள விவசாயி, எனக்கு உழவர் உதவி கிடைக்குமா?",
            "lang": "ta"
        }
        res = self.client.post("/api/assistant/match", json=req)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_potential_matches"], 0)
        matched_ids = [m["scheme_id"] for m in data["matches"]]
        self.assertIn("pm-kisan-tn", matched_ids)

    def test_11_admin_create_and_delete_scheme(self):
        new_scheme_payload = {
            "id": "tn-sports-scholarship",
            "name": "Tamil Nadu Champions Sports Scholarship",
            "name_ta": "தமிழ்நாடு சாம்பியன்ஸ் விளையாட்டு உதவித்தொகை",
            "department": "Youth Welfare and Sports Development Department",
            "department_ta": "இளைஞர் நலன் மற்றும் விளையாட்டு மேம்பாட்டுத் துறை",
            "category": "education",
            "benefit_amount": "₹25,000 / year",
            "benefit_summary": "Financial support for national sports medalists",
            "benefit_summary_ta": "தேசிய அளவிலான விளையாட்டு வீரர்களுக்கு ஆண்டு நிதி உதவி",
            "description": "Scheme to encourage young athletic talent from rural Tamil Nadu.",
            "description_ta": "கிராமப்புற விளையாட்டு வீரர்களை ஊக்குவிக்கும் திட்டம்.",
            "is_active": True,
            "conditions": [
                {
                    "field_name": "age_max",
                    "operator": "lte",
                    "expected_value": "25",
                    "is_mandatory": True,
                    "description_en": "Age must be below 25 years",
                    "description_ta": "25 வயதுக்குட்பட்டவராக இருக்க வேண்டும்"
                }
            ],
            "documents": [
                {
                    "name_en": "National Sports Certificate",
                    "name_ta": "விளையாட்டு சான்றிதழ்",
                    "is_mandatory": True,
                    "issuing_authority_en": "Sports Development Authority of Tamil Nadu"
                }
            ],
            "steps": [
                {
                    "step_number": 1,
                    "mode": "online",
                    "title_en": "Online Portal Application",
                    "title_ta": "இணையதள விண்ணப்பம்",
                    "description_en": "Submit tournament certificates on SDAT portal.",
                    "description_ta": "SDAT இணையதளத்தில் சான்றிதழ்களை பதிவேற்றவும்."
                }
            ],
            "source": {
                "source_name": "SDAT Official Portal",
                "portal_url": "https://sdat.tn.gov.in",
                "verified_date": "2026-11-23",
                "verification_status": "verified"
            }
        }

        # 1. POST create
        res = self.client.post("/api/admin/schemes", json=new_scheme_payload)
        self.assertEqual(res.status_code, 201)
        created = res.json()
        self.assertEqual(created["id"], "tn-sports-scholarship")

        # 2. GET verify creation
        res = self.client.get("/api/schemes/tn-sports-scholarship")
        self.assertEqual(res.status_code, 200)

        # 3. DELETE clean up
        res = self.client.delete("/api/admin/schemes/tn-sports-scholarship")
        self.assertEqual(res.status_code, 200)

        # 4. GET verify deletion
        res = self.client.get("/api/schemes/tn-sports-scholarship")
        self.assertEqual(res.status_code, 404)

    def test_12_admin_stats(self):
        res = self.client.get("/api/admin/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_schemes", data)
        self.assertIn("verified_sources", data)
        self.assertGreater(data["total_schemes"], 0)

if __name__ == "__main__":
    unittest.main()
