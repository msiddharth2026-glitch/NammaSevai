import unittest
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.seeds.seed_data import seed_database
from backend.models.scheme import Scheme
from backend.models.source import OfficialSource
from backend.data.geography import (
    INDIAN_STATES,
    INDIAN_UNION_TERRITORIES,
    GOVERNMENT_LEVELS,
    SCHEME_CATEGORIES,
    normalize_jurisdiction,
    is_valid_state,
    is_valid_ut
)
from backend.routers.schemes import (
    list_schemes,
    get_scheme_by_id,
    get_jurisdictions_meta,
    get_national_coverage_stats
)
from backend.routers.admin import (
    bulk_import_schemes,
    get_admin_stats
)
from backend.schemas.scheme import BulkImportReport
from backend.schemas.assistant import ExtractedUserProfile, MatchRequest
from backend.services.matcher import SchemeMatcherService
from backend.services.extractor import CitizenInfoExtractor
from backend.services.scheme_importer import SchemeImporterService

class TestNationalSchemeExpansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()
        cls.matcher = SchemeMatcherService()
        cls.extractor = CitizenInfoExtractor()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # -------------------------------------------------------------------------
    # 1. Geographic Classification & Normalization
    # -------------------------------------------------------------------------
    def test_01_all_28_states_and_8_uts_defined(self):
        """Verify all 28 Indian States and 8 Union Territories are precisely cataloged."""
        self.assertEqual(len(INDIAN_STATES), 28)
        self.assertEqual(len(INDIAN_UNION_TERRITORIES), 8)
        self.assertEqual(len(GOVERNMENT_LEVELS), 3)

        # Check key states
        self.assertTrue(is_valid_state("Tamil Nadu"))
        self.assertTrue(is_valid_state("Maharashtra"))
        self.assertTrue(is_valid_state("Karnataka"))
        self.assertTrue(is_valid_state("Uttar Pradesh"))
        self.assertTrue(is_valid_state("Bihar"))
        self.assertTrue(is_valid_state("West Bengal"))
        self.assertTrue(is_valid_state("Kerala"))

        # Check key UTs
        self.assertTrue(is_valid_ut("Delhi"))
        self.assertTrue(is_valid_ut("Puducherry"))
        self.assertTrue(is_valid_ut("Chandigarh"))
        self.assertTrue(is_valid_ut("Jammu and Kashmir"))
        self.assertTrue(is_valid_ut("Ladakh"))

        # Test normalization
        name, lvl = normalize_jurisdiction("tn")
        self.assertEqual(name, "Tamil Nadu")
        self.assertEqual(lvl, "State")

        name, lvl = normalize_jurisdiction("nct of delhi")
        self.assertEqual(name, "Delhi")
        self.assertEqual(lvl, "Union Territory")

        name, lvl = normalize_jurisdiction("central government")
        self.assertEqual(name, "All India")
        self.assertEqual(lvl, "Central")

    # -------------------------------------------------------------------------
    # 2. National Scheme Database Representation
    # -------------------------------------------------------------------------
    def test_02_database_has_central_state_and_ut_schemes(self):
        """Verify the database contains authentic Central, State, and UT schemes."""
        schemes = self.db.query(Scheme).filter(Scheme.is_active == True).all()
        self.assertGreaterEqual(len(schemes), 20)

        levels = set(s.level for s in schemes)
        self.assertIn("Central", levels)
        self.assertIn("State", levels)
        self.assertIn("Union Territory", levels)

        central_schemes = [s for s in schemes if s.level == "Central"]
        state_schemes = [s for s in schemes if s.level == "State"]
        ut_schemes = [s for s in schemes if s.level == "Union Territory"]

        self.assertGreaterEqual(len(central_schemes), 5)
        self.assertGreaterEqual(len(state_schemes), 14)
        self.assertGreaterEqual(len(ut_schemes), 1)

        # Verify authentic portal URLs exist for key schemes
        central_ids = [s.id for s in central_schemes]
        self.assertIn("ayushman-bharat-pmjay", central_ids)
        self.assertIn("pmay-urban-housing", central_ids)
        self.assertIn("pm-svanidhi-microcredit", central_ids)
        self.assertIn("atal-pension-yojana", central_ids)

        pmjay = next(s for s in central_schemes if s.id == "ayushman-bharat-pmjay")
        self.assertIn("pmjay.gov.in", pmjay.source.portal_url)

    # -------------------------------------------------------------------------
    # 3. National Scheme Discovery Filtering API
    # -------------------------------------------------------------------------
    def test_03_discovery_filter_by_level(self):
        """Verify filtering schemes by government level (Central vs State vs UT)."""
        central_res = list_schemes(level="Central", db=self.db)
        for s in central_res:
            self.assertEqual(s.level, "Central")

        state_res = list_schemes(level="State", db=self.db)
        for s in state_res:
            self.assertEqual(s.level, "State")

        ut_res = list_schemes(level="Union Territory", db=self.db)
        for s in ut_res:
            self.assertEqual(s.level, "Union Territory")

    def test_04_discovery_filter_by_state(self):
        """Verify filtering by state returns state schemes + national central schemes."""
        mh_res = list_schemes(state="Maharashtra", db=self.db)
        mh_ids = [s.id for s in mh_res]
        self.assertIn("mjpjay-maharashtra", mh_ids)
        self.assertIn("ayushman-bharat-pmjay", mh_ids)
        # Should NOT include Tamil Nadu exclusive schemes
        self.assertNotIn("pudhumai-penn", mh_ids)
        self.assertNotIn("kmut-magalir", mh_ids)

        tn_res = list_schemes(state="Tamil Nadu", db=self.db)
        tn_ids = [s.id for s in tn_res]
        self.assertIn("pudhumai-penn", tn_ids)
        self.assertIn("ayushman-bharat-pmjay", tn_ids)
        # Should NOT include Maharashtra exclusive schemes
        self.assertNotIn("mjpjay-maharashtra", tn_ids)

    def test_05_discovery_sorting(self):
        """Verify sorting schemes by name, level, and state."""
        by_state = list_schemes(sort_by="state", sort_dir="asc", db=self.db)
        states = [s.state for s in by_state if s.state]
        self.assertEqual(states, sorted(states))

    # -------------------------------------------------------------------------
    # 4. Recommendation Engine Geographic Matching Rule
    # -------------------------------------------------------------------------
    def test_06_geographic_matching_state_exclusive(self):
        """
        Verify the core geographic rule:
        - Central schemes apply to citizens in any state / UT.
        - State schemes apply strictly to residents of that state.
        """
        # Citizen residing in Tamil Nadu
        p_tn = ExtractedUserProfile(
            age=20,
            gender="female",
            occupation="student",
            school_type="government",
            annual_income=120000.0,
            state="Tamil Nadu"
        )
        matches_tn, _, _ = self.matcher.match_schemes(self.db, p_tn)
        matched_tn_ids = [m.scheme_id for m in matches_tn]

        # TN resident must get Central + TN schemes
        self.assertIn("pudhumai-penn", matched_tn_ids)
        self.assertIn("ayushman-bharat-pmjay", matched_tn_ids)
        # TN resident MUST NOT get Maharashtra, Karnataka, UP or Delhi exclusive schemes
        self.assertNotIn("mjpjay-maharashtra", matched_tn_ids)
        self.assertNotIn("karnataka-gruha-lakshmi", matched_tn_ids)
        self.assertNotIn("up-kanya-sumangala", matched_tn_ids)
        self.assertNotIn("delhi-ladli", matched_tn_ids)

        # Citizen residing in Maharashtra
        p_mh = ExtractedUserProfile(
            age=35,
            gender="female",
            occupation="self_employed",
            annual_income=150000.0,
            state="Maharashtra"
        )
        matches_mh, _, _ = self.matcher.match_schemes(self.db, p_mh)
        matched_mh_ids = [m.scheme_id for m in matches_mh]

        # MH resident must get Central + MH schemes
        self.assertIn("mjpjay-maharashtra", matched_mh_ids)
        self.assertIn("ayushman-bharat-pmjay", matched_mh_ids)
        # MH resident MUST NOT get Tamil Nadu schemes
        self.assertNotIn("pudhumai-penn", matched_mh_ids)
        self.assertNotIn("kmut-magalir", matched_mh_ids)

    # -------------------------------------------------------------------------
    # 5. Natural Language State & City Extraction
    # -------------------------------------------------------------------------
    def test_07_multilingual_state_and_city_extraction(self):
        """Verify NLP extractor extracts states and major cities across India."""
        # 1. English with Mumbai city
        p1, _, _ = self.extractor.extract("I am a 22-year-old student living in Mumbai looking for scholarships")
        self.assertEqual(p1.state, "Maharashtra")
        self.assertEqual(p1.district, "Mumbai")
        self.assertEqual(p1.age, 22)
        self.assertEqual(p1.occupation, "student")

        # 2. Hindi with Lucknow
        p2, _, _ = self.extractor.extract("लखनऊ में रहने वाली 30 साल की महिला स्वरोजगार सहायता चाहती है")
        self.assertEqual(p2.state, "Uttar Pradesh")
        self.assertEqual(p2.district, "Lucknow")
        self.assertEqual(p2.gender, "female")

        # 3. Tamil with Bengaluru
        p3, _, _ = self.extractor.extract("நான் பெங்களூருவில் வசிக்கும் 28 வயது பெண் தொழில் முனைவோர்")
        self.assertEqual(p3.state, "Karnataka")
        self.assertEqual(p3.district, "Bengaluru")
        self.assertEqual(p3.gender, "female")

        # 4. English with Delhi
        p4, _, _ = self.extractor.extract("Single mother living in New Delhi with annual income 1.5 lakhs")
        self.assertEqual(p4.state, "Delhi")
        self.assertEqual(p4.district, "New Delhi")
        self.assertEqual(p4.annual_income, 150000.0)

        # 5. National behavior: Query with no state or district has state=None and asks for state
        p5, _, missing5 = self.extractor.extract("நான் 12ஆம் வகுப்பு முடித்துள்ளேன் கல்லூரி உதவித்தொகை தேவை")
        self.assertIsNone(p5.state)
        self.assertIn("state", [m.field_name for m in missing5])

    # -------------------------------------------------------------------------
    # 6. Bulk Importer Service & Validation
    # -------------------------------------------------------------------------
    def test_08_bulk_importer_json_validation_and_deduplication(self):
        """Verify the bulk importer validates records, skips duplicates, and returns detailed report."""
        test_batch = [
            {
                "id": "assam-arundhati-gold",
                "name": "Arundhati Gold Scheme",
                "name_ta": "அருந்ததி தங்கம் திட்டம்",
                "name_hi": "अरुंधति स्वर्ण योजना",
                "department": "Revenue and Disaster Management Department",
                "category": "women",
                "level": "State",
                "state": "Assam",
                "benefit_amount": "₹40,000 for gold purchase",
                "official_portal": "https://revenueassam.nic.in",
                "source_name": "Government of Assam",
                "eligibility_criteria": ["Resident of Assam", "Annual income under ₹5 Lakhs"],
                "required_documents": ["Aadhaar Card", "Income Certificate", "Marriage Registration"]
            }
        ]

        # First import: should insert 1 scheme (or count duplicate if run multiple times)
        report = bulk_import_schemes(
            payload={"records": test_batch, "allow_overwrite": False},
            db=self.db,
            authorized=True
        )
        total_p = report.total_processed if hasattr(report, "total_processed") else report["total_processed"]
        imp = report.imported if hasattr(report, "imported") else report["imported"]
        fail = report.failed if hasattr(report, "failed") else report["failed"]
        self.assertEqual(total_p, 1)
        self.assertIn(imp, [0, 1])
        self.assertEqual(fail, 0)

        # Second import with allow_overwrite=False: should detect duplicate
        report2 = bulk_import_schemes(
            payload={"records": test_batch, "allow_overwrite": False},
            db=self.db,
            authorized=True
        )
        dups = report2.duplicates if hasattr(report2, "duplicates") else report2["duplicates"]
        imp2 = report2.imported if hasattr(report2, "imported") else report2["imported"]
        self.assertEqual(dups, 1)
        self.assertEqual(imp2, 0)

    def test_09_bulk_importer_csv(self):
        """Verify the bulk importer parses and imports CSV lines."""
        csv_data = """id,name,level,state,category,department,benefit_amount,official_portal,source_name
punjab-ashirwad,Ashirwad Scheme,State,Punjab,women,Social Justice and Empowerment,₹51000 marriage grant,https://punjab.gov.in,Government of Punjab"""

        report = bulk_import_schemes(
            payload={"csv_content": csv_data, "allow_overwrite": False},
            db=self.db,
            authorized=True
        )
        total_p = report.total_processed if hasattr(report, "total_processed") else report["total_processed"]
        fail = report.failed if hasattr(report, "failed") else report["failed"]
        self.assertEqual(total_p, 1)
        self.assertEqual(fail, 0)

    # -------------------------------------------------------------------------
    # 7. National Coverage and Transparency Stats
    # -------------------------------------------------------------------------
    def test_10_national_coverage_stats_endpoint(self):
        """Verify coverage stats return honest breakdown of covered vs pending jurisdictions."""
        cov = get_national_coverage_stats(db=self.db)
        self.assertGreaterEqual(cov["total_schemes"], 20)
        self.assertEqual(cov["total_states"], 28)
        self.assertEqual(cov["total_uts"], 8)
        self.assertGreaterEqual(cov["states_covered_count"], 4)
        self.assertGreaterEqual(cov["uts_covered_count"], 1)
        self.assertIn("Tamil Nadu", cov["states_covered"])
        self.assertIn("Delhi", cov["uts_covered"])
        self.assertIn("transparency_note", cov)

    def test_11_jurisdictions_meta_endpoint(self):
        """Verify jurisdictions meta endpoint returns all 28 states, 8 UTs, and levels."""
        meta = get_jurisdictions_meta(db=self.db)
        self.assertEqual(len(meta["states"]), 28)
        self.assertEqual(len(meta["union_territories"]), 8)
        self.assertEqual(len(meta["government_levels"]), 3)
        self.assertIn("Central", meta["level_counts"])
        self.assertIn("State", meta["level_counts"])

    def test_12_admin_stats_includes_national_metrics(self):
        """Verify admin stats include national jurisdiction representation."""
        stats = get_admin_stats(db=self.db, authorized=True)
        self.assertIn("central_schemes", stats)
        self.assertIn("state_schemes", stats)
        self.assertIn("ut_schemes", stats)
        self.assertIn("states_represented", stats)
        self.assertIn("uts_represented", stats)
        self.assertGreaterEqual(stats["central_schemes"], 5)
        self.assertGreaterEqual(stats["state_schemes"], 14)

if __name__ == "__main__":
    unittest.main()
