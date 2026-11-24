import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.seeds.seed_data import seed_database
from backend.routers.voice import get_voice_config
from backend.routers.assistant import match_citizen_schemes
from backend.routers.schemes import list_schemes, get_scheme_by_id
from backend.schemas.assistant import MatchRequest, ExtractedUserProfile
from backend.services.extractor import CitizenInfoExtractor
from backend.services.matcher import SchemeMatcherService
from backend.models.scheme import Scheme

class TestMultilingualEnhancements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()
        cls.extractor = CitizenInfoExtractor()
        cls.matcher = SchemeMatcherService()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_hindi_query_extraction_and_matching(self):
        query = "मैं एक छात्र हूँ और कॉलेज में पढ़ता हूँ। परिवार की वार्षिक आय ₹1,50,000 है।"
        req = MatchRequest(query=query, lang="hi")
        res = match_citizen_schemes(req, db=self.db)
        
        # Verify detected profile
        self.assertIsNotNone(res.extracted_profile)
        self.assertEqual(res.extracted_profile.occupation, "student")
        self.assertEqual(res.extracted_profile.annual_income, 150000)

        # Verify matches returned
        self.assertGreater(len(res.matches), 0)
        
        # Verify coverage_type & application_url exist
        first_match = res.matches[0]
        self.assertIsNotNone(first_match.coverage_type)
        self.assertIsNotNone(first_match.application_url)
        self.assertTrue(len(first_match.coverage_type) > 0)
        self.assertIsNotNone(first_match.eligibility_explanation_hi)

    def test_02_malayalam_query_extraction_and_matching(self):
        query = "ഞാൻ ഒരു കോളേജ് വിദ്യാർത്ഥിയാണ്. എന്റെ കുടുംബ വാർഷിക വരുമാനം ₹1,80,000 ആണ്."
        req = MatchRequest(query=query, lang="ml")
        res = match_citizen_schemes(req, db=self.db)
        
        self.assertIsNotNone(res.extracted_profile)
        self.assertEqual(res.extracted_profile.occupation, "student")
        self.assertEqual(res.extracted_profile.annual_income, 180000)
        self.assertGreater(len(res.matches), 0)
        self.assertIsNotNone(res.matches[0].eligibility_explanation_ml)

    def test_03_hinglish_and_tanglish_extraction(self):
        # Hinglish
        h_profile, _, _ = self.extractor.extract("Meri age 24 hai, new startup business start karna chahta hoon.")
        self.assertEqual(h_profile.age, 24)
        self.assertIn(h_profile.occupation, ["business", "self_employed", "entrepreneur"])

        # Tanglish
        t_profile, _, _ = self.extractor.extract("Enakku age 19, naan college student, family income 1.2 lakhs.")
        self.assertEqual(t_profile.age, 19)
        self.assertEqual(t_profile.occupation, "student")
        self.assertEqual(t_profile.annual_income, 120000)

    def test_04_profile_memory_and_correction(self):
        # Initial profile with age 19
        initial_profile = ExtractedUserProfile(
            age=19,
            occupation="student",
            gender="male"
        )
        # Citizen makes a correction: "Actually my age is 20, and annual income is 100000"
        req = MatchRequest(
            query="Actually my age is 20, annual income 100000",
            lang="en",
            profile=initial_profile
        )
        res = match_citizen_schemes(req, db=self.db)
        updated_profile = res.extracted_profile
        
        # Verify correction took effect
        self.assertEqual(updated_profile.age, 20)
        self.assertEqual(updated_profile.annual_income, 100000)
        # Previous unmentioned fields preserved
        self.assertEqual(updated_profile.occupation, "student")
        self.assertEqual(updated_profile.gender, "male")

    def test_05_new_authentic_schemes_in_db(self):
        # PMEGP Scheme
        pmegp = self.db.query(Scheme).filter(Scheme.id == "pmegp-msme-business").first()
        self.assertIsNotNone(pmegp)
        self.assertEqual(pmegp.category, "business")
        self.assertIn("kviconline", pmegp.source.portal_url)

        # NSP Post Matric Scheme
        nsp = self.db.query(Scheme).filter(Scheme.id == "nsp-post-matric-scholarship").first()
        self.assertIsNotNone(nsp)
        self.assertEqual(nsp.category, "education")
        self.assertIn("scholarships.gov.in", nsp.source.portal_url)

    def test_06_schemes_list_coverage_type(self):
        schemes = list_schemes(db=self.db)
        self.assertGreaterEqual(len(schemes), 14)
        
        # Central scheme
        central_schemes = [s for s in schemes if "pmegp" in s.id or "nsp" in s.id or "pm-" in s.id]
        self.assertGreater(len(central_schemes), 0)
        for s in central_schemes:
            self.assertEqual(s.coverage_type, "Central Government / Centrally Sponsored")
            self.assertIsNotNone(s.application_url)

        # State scheme
        state_schemes = [s for s in schemes if s.id == "pudhumai-penn"]
        self.assertEqual(len(state_schemes), 1)
        self.assertEqual(state_schemes[0].coverage_type, "State Government (Tamil Nadu)")

    def test_07_voice_config_supported_languages(self):
        config = get_voice_config()
        supported = config.get("supported_languages", [])
        self.assertIn("ta", supported)
        self.assertIn("en", supported)
        self.assertIn("hi", supported)
        self.assertIn("ml", supported)
        self.assertIn("tanglish", supported)
        self.assertIn("hinglish", supported)

if __name__ == "__main__":
    unittest.main()
