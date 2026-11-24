import unittest
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, Base, engine
from backend.seeds.seed_data import seed_database
from backend.routers.assistant import match_citizen_schemes
from backend.schemas.assistant import MatchRequest
from backend.models.scheme import Scheme

class TestCompleteLocalization(unittest.TestCase):
    """
    Automated verification suite ensuring complete, end-to-end language localization
    across all 6 supported languages:
    - English (en)
    - Tamil (ta)
    - Hindi (hi)
    - Malayalam (ml)
    - Tanglish (tanglish)
    - Hinglish (hinglish)
    """

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()
        cls.db = SessionLocal()

        with open("static/js/i18n.js", "r", encoding="utf-8") as f:
            cls.i18n_content = f.read()

        with open("static/js/schemesData.js", "r", encoding="utf-8") as f:
            cls.schemes_content = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_i18n_language_blocks_and_keys_parity(self):
        """Verify all 6 languages have 100% key parity in i18n.js."""
        langs = ["en", "ta", "hi", "ml", "tanglish", "hinglish"]
        lang_keys = {}

        for lang in langs:
            # Matches language block with optional trailing comma, closing brace, or semicolon
            match = re.search(rf"\b{lang}:\s*\{{(.*?)\n\s*\}}(?:\s*,|\s*\}}|\s*;|$)", self.i18n_content, re.DOTALL)
            self.assertIsNotNone(match, f"Language block '{lang}' not found in i18n.js")
            block = match.group(1)
            keys = set(re.findall(r"^\s*([a-zA-Z0-9_]+)\s*:", block, re.MULTILINE))
            lang_keys[lang] = keys
            self.assertGreaterEqual(len(keys), 280, f"Language '{lang}' has only {len(keys)} keys")

        # Compare parity against 'en'
        en_keys = lang_keys["en"]
        for lang in ["ta", "hi", "ml", "tanglish", "hinglish"]:
            diff = en_keys - lang_keys[lang]
            self.assertEqual(len(diff), 0, f"Language '{lang}' is missing keys: {diff}")

    def test_schemes_data_all_14_schemes_translated(self):
        """Verify all 14 authentic schemes have multi-lingual fields in schemesData.js."""
        expected_schemes = [
            "pudhumai-penn",
            "kmut-magalir",
            "cmchis-health",
            "sewing-machine-welfare",
            "pm-kisan-tn",
            "naan-mudhalvan",
            "oap-senior-pension",
            "differently-abled-welfare",
            "muthulakshmi-maternity",
            "aabcs-scst-entrepreneur",
            "tamil-pudhalvan",
            "kalaignar-kanavu-illam",
            "pmegp-msme-business",
            "nsp-post-matric-scholarship"
        ]

        for s_id in expected_schemes:
            self.assertIn(f'"id": "{s_id}"', self.schemes_content, f"Scheme {s_id} missing from schemesData.js")

        # Check that Hindi and Malayalam translations exist in schemesData.js
        for s_id in expected_schemes:
            idx = self.schemes_content.find(f'"id": "{s_id}"')
            self.assertNotEqual(idx, -1)
            block = self.schemes_content[idx:idx+4000]
            self.assertIn('"name_hi":', block, f"Scheme {s_id} missing name_hi")
            self.assertIn('"name_ml":', block, f"Scheme {s_id} missing name_ml")
            self.assertIn('"department_hi":', block, f"Scheme {s_id} missing department_hi")
            self.assertIn('"department_ml":', block, f"Scheme {s_id} missing department_ml")
            self.assertIn('"benefit_summary_hi":', block, f"Scheme {s_id} missing benefit_summary_hi")
            self.assertIn('"benefit_summary_ml":', block, f"Scheme {s_id} missing benefit_summary_ml")

    def test_components_use_i18n_without_binary_is_ta(self):
        """Verify frontend components do not use `const isTa = state.lang === 'ta';` to dictate language."""
        components = [
            "static/js/components/landingPage.js",
            "static/js/components/assistantPage.js",
            "static/js/components/resultsPage.js",
            "static/js/components/detailsPage.js",
            "static/js/components/checklistPage.js",
            "static/js/components/adminPage.js"
        ]

        for comp_path in components:
            with open(comp_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertNotIn("const isTa = state.lang === 'ta';", content,
                             f"{comp_path} still contains binary `const isTa = state.lang === 'ta';`")

    def test_backend_assistant_match_all_6_languages(self):
        """Verify match_citizen_schemes generates authentic compassionate responses in all 6 languages."""
        test_queries = [
            ("en", "I am a college girl studying in government school with low family income"),
            ("ta", "நான் அரசுப் பள்ளியில் படித்த கல்லூரி மாணவி குடும்ப வருமானம் குறைவு"),
            ("hi", "मैं सरकारी स्कूल से पढ़ी कॉलेज की छात्रा हूँ और पारिवारिक आय कम है"),
            ("ml", "ഞാൻ സർക്കാർ സ്കൂളിൽ പഠിച്ച കോളേജ് വിദ്യാർത്ഥിനിയാണ് കുടുംബ വരുമാനം കുറവാണ്"),
            ("tanglish", "naan govt school-la padicha college student family income romba kammi"),
            ("hinglish", "main govt school se padhi college student hoon family income kam hai")
        ]

        for lang, query in test_queries:
            req = MatchRequest(query=query, lang=lang)
            res = match_citizen_schemes(req, db=self.db)
            
            self.assertGreaterEqual(res.total_potential_matches, 1, f"No matches found for {lang} query: {query}")
            
            # Verify compassionate response text
            resp_text = res.compassionate_response
            self.assertIsNotNone(resp_text, f"compassionate_response is None for lang: {lang}")
            self.assertGreater(len(resp_text), 20)

            # Check language authenticity in response
            if lang == "ta":
                self.assertTrue(any(w in resp_text for w in ["நலத்திட்டங்கள்", "கண்டறிந்துள்ளேன்", "திட்டம்"]))
            elif lang == "hi":
                self.assertTrue(any(w in resp_text for w in ["कल्याणकारी", "योजनाएं", "पात्रता"]))
            elif lang == "ml":
                self.assertTrue(any(w in resp_text for w in ["ക്ഷേമപദ്ധതികൾ", "കണ്ടെത്തിയിട്ടുണ്ട്", "പദ്ധതി"]))
            elif lang == "tanglish":
                self.assertTrue(any(w in resp_text for w in ["analyze panni", "welfare schemes", "match pannirukken"]))
            elif lang == "hinglish":
                self.assertTrue(any(w in resp_text for w in ["analyze karke", "matching", "identify hui hain"]))
            elif lang == "en":
                self.assertTrue("welfare scheme" in resp_text)

    def test_pmegp_and_nsp_authentic_records(self):
        """Verify PMEGP and NSP schemes have verified URLs and correct government ministries."""
        schemes = self.db.query(Scheme).all()
        scheme_map = {s.id: s for s in schemes}

        # Check PMEGP
        self.assertIn("pmegp-msme-business", scheme_map)
        pmegp = scheme_map["pmegp-msme-business"]
        portal = pmegp.source.portal_url if pmegp.source else ""
        self.assertIn("kviconline", portal.lower())
        self.assertIn("msme", pmegp.department.lower())

        # Check NSP
        self.assertIn("nsp-post-matric-scholarship", scheme_map)
        nsp = scheme_map["nsp-post-matric-scholarship"]
        portal_nsp = nsp.source.portal_url if nsp.source else ""
        self.assertIn("scholarships.gov.in", portal_nsp.lower())

if __name__ == "__main__":
    unittest.main()
