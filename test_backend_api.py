import os
import sys
import unittest
from fastapi import HTTPException

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, Base, SessionLocal
from backend.seeds.seed_data import seed_database
from backend.main import health_check
from backend.routers.schemes import list_schemes, get_scheme_by_id, get_scheme_documents
from backend.routers.assistant import analyze_citizen_query, match_citizen_schemes
from backend.routers.admin import create_scheme, delete_scheme, get_admin_stats
from backend.schemas.assistant import AnalyzeRequest, MatchRequest
from backend.schemas.scheme import SchemeCreate

class TestNammaSevaiBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_health_check(self):
        data = health_check()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)

    def test_02_get_schemes_list(self):
        schemes = list_schemes(limit=100, offset=0, db=self.db)
        self.assertIsInstance(schemes, list)
        self.assertGreater(len(schemes), 0)
        s = schemes[0]
        self.assertIsNotNone(s.id)
        self.assertIsNotNone(s.name)
        self.assertIsNotNone(s.name_ta)
        self.assertIsNotNone(s.benefit_amount)

    def test_03_get_schemes_filtered_by_category(self):
        schemes = list_schemes(category="education", limit=100, offset=0, db=self.db)
        self.assertTrue(all(s.category == "education" for s in schemes))

    def test_04_get_scheme_by_id(self):
        data = get_scheme_by_id("pudhumai-penn", db=self.db)
        self.assertEqual(data.id, "pudhumai-penn")
        self.assertGreater(len(data.conditions), 0)
        self.assertGreater(len(data.documents), 0)
        self.assertGreater(len(data.steps), 0)
        self.assertEqual(data.source.verification_status.lower(), "verified")

    def test_05_get_scheme_not_found(self):
        with self.assertRaises(HTTPException) as ctx:
            get_scheme_by_id("non-existent-scheme-999", db=self.db)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_06_get_scheme_documents(self):
        docs = get_scheme_documents("pudhumai-penn", db=self.db)
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)
        doc = docs[0]
        self.assertIsNotNone(doc.name_en)
        self.assertIsNotNone(doc.name_ta)

    def test_07_assistant_analyze_tamil_query(self):
        query = "நான் அரசுப் பள்ளியில் படித்து தற்போது கல்லூரியில் சேர்ந்த மாணவி, எனக்கு உதவித்தொகை உண்டா?"
        data = analyze_citizen_query(AnalyzeRequest(text=query, lang="ta"))
        profile = data.extracted_profile
        self.assertEqual(profile.gender, "female")
        self.assertEqual(profile.occupation, "student")
        self.assertEqual(profile.school_type, "government")
        self.assertIn("education", data.identified_categories)

    def test_08_assistant_analyze_missing_critical_info(self):
        query = "I am a college student girl looking for scholarships in Madurai."
        data = analyze_citizen_query(AnalyzeRequest(text=query, lang="en"))
        profile = data.extracted_profile
        self.assertEqual(profile.gender, "female")
        self.assertEqual(profile.occupation, "student")
        self.assertEqual(profile.district, "Madurai")
        self.assertIsNone(profile.school_type)
        
        self.assertGreater(len(data.missing_critical_info), 0)
        missing_fields = [m.field_name for m in data.missing_critical_info]
        self.assertIn("school_type", missing_fields)
        self.assertGreater(len(data.follow_up_questions_en), 0)
        self.assertGreater(len(data.follow_up_questions_ta), 0)

    def test_09_assistant_match_structured_schemes(self):
        req = MatchRequest(
            query="19 year old girl from govt school studying in college degree",
            lang="en"
        )
        data = match_citizen_schemes(req, db=self.db)
        self.assertGreater(data.total_potential_matches, 0)
        
        top_match = data.matches[0]
        self.assertEqual(top_match.scheme_id, "pudhumai-penn")
        self.assertIn(top_match.match_status, ["high_potential", "potential_match"])
        self.assertGreaterEqual(top_match.match_confidence, 70.0)
        self.assertIn("₹1,000 / month", top_match.benefit_amount)
        self.assertGreater(len(top_match.required_documents), 0)
        self.assertGreater(len(top_match.application_steps), 0)
        self.assertIn("penkalvi.tn.gov.in", top_match.official_portal_url)
        self.assertIsNotNone(data.disclaimer)
        self.assertIsNotNone(data.disclaimer_ta)

    def test_10_assistant_match_farmer_query(self):
        req = MatchRequest(
            query="நான் 2 ஏக்கர் நிலம் வைத்துள்ள விவசாயி, எனக்கு உழவர் உதவி கிடைக்குமா?",
            lang="ta"
        )
        data = match_citizen_schemes(req, db=self.db)
        self.assertGreater(data.total_potential_matches, 0)
        matched_ids = [m.scheme_id for m in data.matches]
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
        scheme_create_obj = SchemeCreate(**new_scheme_payload)

        # 1. create
        created = create_scheme(scheme_create_obj, db=self.db, authorized=True)
        self.assertEqual(created.id, "tn-sports-scholarship")

        # 2. verify creation
        fetched = get_scheme_by_id("tn-sports-scholarship", db=self.db)
        self.assertEqual(fetched.id, "tn-sports-scholarship")

        # 3. delete
        res = delete_scheme("tn-sports-scholarship", db=self.db, authorized=True)
        self.assertIn("deleted successfully", res.get("message", ""))

        # 4. verify deletion
        with self.assertRaises(HTTPException) as ctx:
            get_scheme_by_id("tn-sports-scholarship", db=self.db)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_12_admin_stats(self):
        data = get_admin_stats(db=self.db)
        self.assertIn("total_schemes", data)
        self.assertIn("verified_sources", data)
        self.assertGreater(data["total_schemes"], 0)

if __name__ == "__main__":
    unittest.main()
