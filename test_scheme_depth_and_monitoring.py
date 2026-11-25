"""
Unit & Integration Tests for National Scheme Depth, Data Verification,
and Automated Official Portal Health Monitoring.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from backend.database import SessionLocal
from backend.models.scheme import Scheme
from backend.models.source import OfficialSource
from backend.models.condition import EligibilityCondition
from backend.models.document import RequiredDocument
from backend.services.portal_health_monitor import check_url_health, PortalHealthMonitorService
from backend.routers.admin import (
    require_admin_auth,
    get_portal_health_status_endpoint,
    get_portal_health_schemes_endpoint
)
from backend.data.geography import INDIAN_STATES, INDIAN_UNION_TERRITORIES

class TestSchemeDepthAndMonitoring(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_total_schemes_count_and_preservation(self):
        """Verify that all existing 67 schemes were preserved and expanded to >= 85 schemes."""
        schemes = self.db.query(Scheme).all()
        self.assertGreaterEqual(len(schemes), 85, f"Expected at least 85 schemes, found {len(schemes)}")
        
        # Verify original Tamil Nadu anchor schemes are intact
        tn_anchors = ["pudhumai-penn", "kmut-magalir", "cmchis-health", "naan-mudhalvan"]
        scheme_ids = [s.id for s in schemes]
        for aid in tn_anchors:
            self.assertIn(aid, scheme_ids, f"Anchor scheme {aid} was deleted or lost")

    def test_02_priority_states_depth_coverage(self):
        """Verify Priority 1 and Priority 2 states have deepened scheme coverage across sectors."""
        schemes = self.db.query(Scheme).all()
        
        # Priority 1 states must have at least 3 schemes each
        priority_1 = {
            "Uttar Pradesh": 3,
            "Bihar": 3,
            "Maharashtra": 3,
            "West Bengal": 3
        }
        for state, min_count in priority_1.items():
            count = sum(1 for s in schemes if s.state == state and s.level == "State")
            self.assertGreaterEqual(
                count, min_count,
                f"State {state} has {count} schemes, expected at least {min_count}"
            )

        # Priority 2 states must have at least 2 schemes each
        priority_2 = {
            "Arunachal Pradesh": 2,
            "Sikkim": 2,
            "Nagaland": 2,
            "Himachal Pradesh": 2
        }
        for state, min_count in priority_2.items():
            count = sum(1 for s in schemes if s.state == state and s.level == "State")
            self.assertGreaterEqual(
                count, min_count,
                f"State {state} has {count} schemes, expected at least {min_count}"
            )

    def test_03_central_schemes_multi_sector_expansion(self):
        """Verify Central Government schemes cover key national priority sectors."""
        schemes = self.db.query(Scheme).filter(Scheme.level == "Central").all()
        self.assertGreaterEqual(len(schemes), 25, f"Expected at least 25 Central schemes, found {len(schemes)}")

        # Verify key flagship schemes are present
        expected_central = [
            "pm-vishwakarma",
            "pm-sym-pension",
            "pm-kisan-maandhan",
            "pm-surya-ghar",
            "standup-india",
            "pm-ujjwala-2",
            "pm-svanidhi-microcredit",
            "ayushman-bharat-pmjay",
            "pmay-gramin-housing",
            "pmfby-crop-insurance"
        ]
        central_ids = [s.id for s in schemes]
        for cid in expected_central:
            self.assertIn(cid, central_ids, f"Central scheme {cid} was not found")

    def test_04_every_scheme_has_structured_conditions(self):
        """Verify that 100% of schemes in the database have structured eligibility conditions."""
        schemes = self.db.query(Scheme).all()
        zero_condition_schemes = []
        for s in schemes:
            if len(s.conditions) == 0:
                zero_condition_schemes.append(s.id)

        self.assertEqual(
            len(zero_condition_schemes), 0,
            f"The following schemes lack structured eligibility conditions: {zero_condition_schemes}"
        )

    def test_05_every_scheme_has_required_documents(self):
        """Verify that 100% of schemes have required documents specified."""
        schemes = self.db.query(Scheme).all()
        zero_doc_schemes = []
        for s in schemes:
            if len(s.documents) == 0:
                zero_doc_schemes.append(s.id)

        self.assertEqual(
            len(zero_doc_schemes), 0,
            f"The following schemes lack required documents: {zero_doc_schemes}"
        )

    def test_06_every_scheme_has_official_source_and_valid_status(self):
        """Verify every scheme has an OfficialSource record with valid classification."""
        valid_statuses = {"Verified", "Partially Verified", "Needs Review", "Inactive or Discontinued", "Source Unavailable"}
        schemes = self.db.query(Scheme).all()

        for s in schemes:
            self.assertIsNotNone(s.source, f"Scheme {s.id} is missing an OfficialSource relation")
            self.assertTrue(s.source.portal_url.startswith("http"), f"Scheme {s.id} has invalid portal URL: {s.source.portal_url}")
            self.assertIn(
                s.source.verification_status, valid_statuses,
                f"Scheme {s.id} has invalid verification_status: {s.source.verification_status}"
            )

    @patch("backend.services.portal_health_monitor.requests.Session")
    def test_07_portal_health_monitor_mock_success(self, mock_session_cls):
        """Verify health check logic detects availability and latency on successful HTTP 200."""
        mock_sess = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.history = []
        mock_resp.url = "https://pmkisan.gov.in"
        mock_sess.get.return_value = mock_resp
        mock_session_cls.return_value = mock_sess

        result = check_url_health("https://pmkisan.gov.in", session=mock_sess)
        self.assertTrue(result["is_available"])
        self.assertEqual(result["http_status"], 200)
        self.assertFalse(result["domain_migration_detected"])
        self.assertIsNone(result["error_message"])

    @patch("backend.services.portal_health_monitor.requests.Session")
    def test_08_portal_health_monitor_detects_domain_migration(self, mock_session_cls):
        """Verify health monitor flags domain migration when redirected to a different host."""
        mock_sess = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.history = [MagicMock(status_code=301)]
        mock_resp.url = "https://newportal.gov.in/services"
        mock_sess.get.return_value = mock_resp
        mock_session_cls.return_value = mock_sess

        result = check_url_health("https://oldportal.gov.in", session=mock_sess)
        self.assertTrue(result["is_available"])
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(result["redirect_url"], "https://newportal.gov.in/services")
        self.assertTrue(result["domain_migration_detected"])

    @patch("backend.services.portal_health_monitor.requests.Session")
    def test_09_strict_separation_of_health_and_content_verification(self, mock_session_cls):
        """
        CRITICAL ARCHITECTURAL TEST:
        Ensure that an HTTP 200 health check response NEVER automatically marks
        a scheme as 'Verified' if it was classified as 'Needs Review' or 'Partially Verified'.
        """
        # Pick or simulate a scheme marked 'Needs Review'
        test_scheme = self.db.query(Scheme).filter(Scheme.source != None).first()
        original_status = test_scheme.source.verification_status

        try:
            test_scheme.source.verification_status = "Needs Review"
            self.db.commit()

            # Mock successful HTTP 200 health check
            mock_sess = MagicMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.history = []
            mock_resp.url = test_scheme.source.portal_url
            mock_sess.get.return_value = mock_resp
            mock_session_cls.return_value = mock_sess

            with patch("backend.services.portal_health_monitor.create_resilient_session", return_value=mock_sess):
                summary = PortalHealthMonitorService.run_health_checks(
                    db=self.db,
                    scheme_ids=[test_scheme.id],
                    max_workers=1
                )

            # Re-read from database
            self.db.refresh(test_scheme.source)
            self.assertEqual(
                test_scheme.source.verification_status, "Needs Review",
                "VIOLATION: Portal health check illegally changed scheme content verification status to Verified!"
            )
            self.assertEqual(test_scheme.source.http_status, 200)
        finally:
            # Restore original status
            test_scheme.source.verification_status = original_status
            self.db.commit()

    def test_10_admin_portal_health_endpoints(self):
        """Verify Admin API portal health monitor status and schemes endpoints."""
        # Test unauthorized rejection
        with self.assertRaises(HTTPException) as ctx:
            require_admin_auth(x_admin_key=None)
        self.assertEqual(ctx.exception.status_code, 401)

        # Test authorized summary retrieval
        summary = get_portal_health_status_endpoint(db=self.db, authorized=True)
        self.assertTrue(hasattr(summary, "total_checked"))
        self.assertTrue(hasattr(summary, "available_count"))
        self.assertTrue(hasattr(summary, "redirects_detected"))
        self.assertTrue(hasattr(summary, "domain_migrations_detected"))
        self.assertTrue(hasattr(summary, "broken_portals"))

        # Test authorized schemes breakdown retrieval
        schemes_list = get_portal_health_schemes_endpoint(db=self.db, authorized=True)
        self.assertIsInstance(schemes_list, list)

if __name__ == "__main__":
    unittest.main()
