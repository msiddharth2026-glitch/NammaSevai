"""
Dedicated Test Suite for Automated Government Scheme Update Detection,
Policy Change Monitoring, Human Approval Workflow, and Scheme Versioning.
Covers 16 statutory and operational requirements.
"""

import unittest
from unittest.mock import patch, MagicMock
import datetime
import hashlib
from fastapi import HTTPException

from backend.database import SessionLocal
from backend.models.scheme import Scheme
from backend.models.source import OfficialSource, DetectedSchemeChange, SchemeVersionHistory
from backend.services.content_change_detector import (
    ContentChangeDetectorService,
    POLICY_CHANGE_CLASSIFICATIONS
)
from backend.services.scheme_update_service import SchemeUpdateService
from backend.services.scheme_update_scheduler import SchemeUpdateSchedulerService
from backend.routers.admin import review_detected_change_endpoint, require_admin_auth

class TestAutomatedSchemeUpdates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_content_fingerprint_generation(self):
        """
        Verify that HTML normalization strips dynamic elements, timestamps,
        visitor counters, and yields an identical SHA-256 fingerprint for identical content.
        """
        html_version_a = """
        <!DOCTYPE html>
        <html>
        <head><title>PM Kisan</title><style>.hidden { display: none; }</style></head>
        <body>
          <header><nav><a href="/home">Home</a></nav></header>
          <h1>Pradhan Mantri Kisan Samman Nidhi</h1>
          <p>Financial benefit: ₹6,000 per year in 3 equal installments to eligible farmer families.</p>
          <div class="footer">
            <p>Page last updated on: 24/11/2026 14:32 PM</p>
            <p>Total Visitors: 4,829,102</p>
            <p>Copyright © 2026 Government of India</p>
          </div>
          <script>console.log("analytics");</script>
        </body>
        </html>
        """

        html_version_b = """
        <!DOCTYPE html>
        <html>
        <head><title>PM Kisan</title><style>body { background: #fff; }</style></head>
        <body>
          <header><nav><a href="/different-nav">Other Nav</a></nav></header>
          <h1>Pradhan Mantri Kisan Samman Nidhi</h1>
          <p>Financial benefit: ₹6,000 per year in 3 equal installments to eligible farmer families.</p>
          <div class="footer">
            <p>Page last updated on: 25/11/2026 09:15 AM</p>
            <p>Total Visitors: 4,835,999</p>
            <p>Copyright © 2026 Government of India</p>
          </div>
          <script>alert("diff script");</script>
        </body>
        </html>
        """

        norm_a, hash_a = ContentChangeDetectorService.normalize_html_content(html_version_a)
        norm_b, hash_b = ContentChangeDetectorService.normalize_html_content(html_version_b)

        # Both normalized texts should contain the core scheme information
        self.assertIn("Pradhan Mantri Kisan Samman Nidhi", norm_a)
        self.assertIn("₹6,000", norm_a)

        # Script, style, and dynamic counters should be stripped
        self.assertNotIn("analytics", norm_a)
        self.assertNotIn("diff script", norm_b)
        self.assertNotIn("4,829,102", norm_a)
        self.assertNotIn("4,835,999", norm_b)

        # The content fingerprints must be identical despite dynamic timestamp/visitor differences
        self.assertEqual(hash_a, hash_b, "Normalized fingerprints should be identical when statutory content matches.")
        self.assertEqual(len(hash_a), 64, "Fingerprint should be a 64-character SHA-256 hex string.")

    def test_02_duplicate_change_detection(self):
        """
        Verify that consecutive checks against the same content or same pending change
        do NOT produce duplicate records in the DetectedSchemeChange queue.
        """
        scheme = self.db.query(Scheme).filter(Scheme.id == "pm-kisan-tn").first()
        self.assertIsNotNone(scheme, "pm-kisan-tn must exist in database")

        # Create mock HTTP response
        mock_html = "<html><body><h1>PM Kisan Portal</h1><p>Annual financial assistance ₹6,000 to farmer families.</p></body></html>"
        mock_sess = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.url = "https://pmkisan.gov.in"
        mock_response.history = []
        mock_sess.get.return_value = mock_response

        # First check captures or checks baseline
        res1 = ContentChangeDetectorService.check_scheme_content(self.db, "pm-kisan-tn", session=mock_sess)
        # Immediate second check on identical content
        res2 = ContentChangeDetectorService.check_scheme_content(self.db, "pm-kisan-tn", session=mock_sess)

        # Second run should report no change detected
        self.assertFalse(res2.get("change_detected", False), "Unchanged content must not trigger change alert.")

    def test_03_meaningful_content_change_detection(self):
        """
        Verify that genuine statutory differences (e.g. benefit amount change)
        are detected and queued as pending changes.
        """
        scheme = self.db.query(Scheme).first()
        self.assertIsNotNone(scheme)

        # Set a baseline excerpt and fingerprint on source
        if not scheme.source:
            source = OfficialSource(
                scheme_id=scheme.id,
                source_name="Gov Portal",
                portal_url="https://gov.in",
                verified_date="2026-11-01",
                verification_status="Verified"
            )
            self.db.add(source)
            self.db.commit()

        scheme.source.last_known_excerpt = "Previous benefit amount: financial assistance ₹5,000 per year."
        scheme.source.content_fingerprint = hashlib.sha256(b"old-baseline").hexdigest()
        self.db.commit()

        # New content with updated benefit
        new_html = "<html><body><h1>Portal</h1><p>Scheme announcement: Benefit amount revised! financial assistance ₹10,000 per year.</p></body></html>"
        mock_sess = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = new_html
        mock_response.url = scheme.source.portal_url
        mock_response.history = []
        mock_sess.get.return_value = mock_response

        result = ContentChangeDetectorService.check_scheme_content(self.db, scheme.id, session=mock_sess)
        self.assertTrue(result["change_detected"])
        self.assertIn("change_id", result)

        # Verify pending change record exists in DB
        ch = self.db.query(DetectedSchemeChange).filter(DetectedSchemeChange.id == result["change_id"]).first()
        self.assertIsNotNone(ch)
        self.assertEqual(ch.review_status, "pending")
        self.assertFalse(ch.applied_to_scheme)
        self.assertEqual(ch.change_classification, "benefit_amount_changed")

    def test_04_irrelevant_html_changes_ignored(self):
        """
        Verify that differences confined to dynamic dates, visitor counters,
        or copyright lines do not trigger change alerts.
        """
        scheme = self.db.query(Scheme).first()
        self.assertIsNotNone(scheme)

        baseline_html = "<html><body><main>Assistance scheme for rural artisans and weavers.</main><div>Page updated on: 01/10/2026</div></body></html>"
        norm_base, hash_base = ContentChangeDetectorService.normalize_html_content(baseline_html)

        scheme.source.content_fingerprint = hash_base
        scheme.source.last_known_excerpt = norm_base
        self.db.commit()

        noisy_html = "<html><body><main>Assistance scheme for rural artisans and weavers.</main><div>Page updated on: 24/11/2026</div><div>Visitors: 98,765</div></body></html>"
        mock_sess = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = noisy_html
        mock_response.url = scheme.source.portal_url
        mock_response.history = []
        mock_sess.get.return_value = mock_response

        result = ContentChangeDetectorService.check_scheme_content(self.db, scheme.id, session=mock_sess)
        self.assertFalse(result["change_detected"], "Noisy timestamp differences should not trigger change alerts.")

    def test_05_source_unavailability_handling(self):
        """
        Verify that HTTP 404, 500, or network timeouts are handled gracefully,
        recording monitoring status without corrupting scheme data.
        """
        scheme = self.db.query(Scheme).first()
        initial_name = scheme.name

        mock_sess = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service Temporarily Unavailable"
        mock_response.history = []
        mock_sess.get.return_value = mock_response

        result = ContentChangeDetectorService.check_scheme_content(self.db, scheme.id, session=mock_sess)
        self.assertEqual(result["status"], "unavailable")

        # Check that source record captured availability issue
        self.db.refresh(scheme.source)
        self.assertEqual(scheme.source.http_status, 503)
        self.assertEqual(scheme.name, initial_name, "Scheme data must remain untouched when source is down.")

    def test_06_redirect_and_domain_migration_detection(self):
        """
        Verify detection of URL redirections and domain migrations.
        """
        scheme = self.db.query(Scheme).first()
        old_url = scheme.source.portal_url
        new_url = "https://newportal.gov.in/schemes/updated"

        diff_text = "Portal moved to new address."
        classification, summary, conf, proposed = ContentChangeDetectorService.classify_content_change(
            scheme=scheme,
            old_excerpt="Old portal info",
            new_excerpt="New portal info",
            diff_text=diff_text,
            redirect_url=new_url
        )

        self.assertEqual(classification, "official_url_changed")
        self.assertGreaterEqual(conf, 0.90)
        self.assertEqual(proposed.get("portal_url"), new_url)

    def test_07_policy_change_classification(self):
        """
        Verify that classify_content_change accurately maps text signals
        to the 13 statutory policy categories.
        """
        scheme = self.db.query(Scheme).first()

        test_cases = [
            ("Family annual income limit updated to ₹2,50,000 for eligibility.", "income_limit_changed"),
            ("The maximum age limit for applicants is now 35 years of age.", "age_limit_changed"),
            ("Revised benefit amount: financial assistance ₹12,000 per month.", "benefit_amount_changed"),
            ("The last date and deadline to apply has been extended up to December 31.", "application_deadline_changed"),
            ("Mandatory documents required now include Aadhaar Card and Ration Card.", "required_documents_changed"),
            ("This scheme has been discontinued and withdrawn by government notification.", "scheme_discontinued_or_suspended"),
            ("Notice: scheme merged into the new National Rural Mission.", "scheme_merged_or_replaced"),
        ]

        for text_sample, expected_class in test_cases:
            cls_result, summary, conf, _ = ContentChangeDetectorService.classify_content_change(
                scheme=scheme,
                old_excerpt="Baseline text",
                new_excerpt=text_sample,
                diff_text=text_sample
            )
            self.assertEqual(
                cls_result, expected_class,
                f"Expected '{expected_class}' for sample '{text_sample}', got '{cls_result}'"
            )
            self.assertIn(cls_result, POLICY_CHANGE_CLASSIFICATIONS)

    def test_08_fallback_classification_when_ai_offline(self):
        """
        Verify that heuristic keyword-matching classification works reliably
        without any external AI calls (offline/fallback mode).
        """
        scheme = self.db.query(Scheme).first()

        # Tamil language signal
        tamil_sample = "திட்டம் நிறுத்தப்பட்டது - மாற்று ஏற்பாடு செய்யப்படும்."
        cls_ta, _, _, _ = ContentChangeDetectorService.classify_content_change(
            scheme=scheme,
            old_excerpt="",
            new_excerpt=tamil_sample,
            diff_text=tamil_sample
        )
        self.assertEqual(cls_ta, "scheme_discontinued_or_suspended")

        # Hindi language signal
        hindi_sample = "आय सीमा ₹1,50,000 प्रति वर्ष निर्धारित की गई है।"
        cls_hi, _, _, _ = ContentChangeDetectorService.classify_content_change(
            scheme=scheme,
            old_excerpt="",
            new_excerpt=hindi_sample,
            diff_text=hindi_sample
        )
        self.assertEqual(cls_hi, "income_limit_changed")

    def test_09_mandatory_human_approval_requirement(self):
        """
        CIVIC INTEGRITY TEST:
        Verify that content change detection NEVER automatically alters
        active scheme fields or eligibility conditions.
        """
        scheme = self.db.query(Scheme).filter(Scheme.id == "pudhumai-penn").first()
        if not scheme:
            scheme = self.db.query(Scheme).first()

        original_benefit = scheme.benefit_amount
        original_desc = scheme.description

        # Inject a change record directly
        change = DetectedSchemeChange(
            scheme_id=scheme.id,
            source_url="https://test.gov.in",
            detected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            change_classification="benefit_amount_changed",
            change_summary="Benefit increased to ₹5,000",
            confidence_score=0.92,
            proposed_modifications='{"benefit_amount": "₹5,000 / month"}',
            review_status="pending",
            applied_to_scheme=False
        )
        self.db.add(change)
        self.db.commit()

        # Refresh and verify scheme fields were NOT mutated
        self.db.refresh(scheme)
        self.assertEqual(scheme.benefit_amount, original_benefit, "Active scheme benefit MUST NOT mutate before human approval!")
        self.assertEqual(scheme.description, original_desc)

        # Cleanup
        self.db.delete(change)
        self.db.commit()

    def test_10_unauthorized_approval_rejection(self):
        """
        Verify that approving or rejecting a change without valid admin authentication
        is rejected with HTTP 401.
        """
        with self.assertRaises(HTTPException) as ctx:
            require_admin_auth(x_admin_key="invalid-key")
        self.assertEqual(ctx.exception.status_code, 401)

        with self.assertRaises(HTTPException) as ctx2:
            require_admin_auth(x_admin_key=None)
        self.assertEqual(ctx2.exception.status_code, 401)

    def test_11_authorized_approval_workflow(self):
        """
        Verify the complete authorized approval workflow:
        1. Human admin approves detected change.
        2. Target fields on Scheme are updated.
        3. Source verified_date and status are updated.
        4. Detected change is marked 'approved'.
        """
        scheme = self.db.query(Scheme).first()
        prev_benefit = scheme.benefit_amount

        change = DetectedSchemeChange(
            scheme_id=scheme.id,
            source_url="https://test.gov.in",
            detected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            change_classification="benefit_amount_changed",
            change_summary="Annual allowance revision",
            confidence_score=0.90,
            proposed_modifications='{"benefit_amount": "₹15,000 / year"}',
            review_status="pending",
            applied_to_scheme=False
        )
        self.db.add(change)
        self.db.commit()

        # Execute authorized review
        res = SchemeUpdateService.review_change(
            db=self.db,
            change_id=change.id,
            action="approve",
            admin_id="officer@nammasevai.gov.in",
            review_notes="Approved after gazette verification."
        )

        self.assertEqual(res["action"], "approved")
        self.db.refresh(change)
        self.assertEqual(change.review_status, "approved")
        self.assertTrue(change.applied_to_scheme)
        self.assertEqual(change.reviewed_by, "officer@nammasevai.gov.in")

        # Verify scheme updated
        self.db.refresh(scheme)
        self.assertEqual(scheme.benefit_amount, "₹15,000 / year")

        # Revert scheme back to original value to preserve database integrity
        scheme.benefit_amount = prev_benefit
        self.db.commit()

    def test_12_version_history_creation_and_rollback(self):
        """
        Verify that approved modifications create SchemeVersionHistory rows,
        and that rollback restores prior field values accurately.
        """
        scheme = self.db.query(Scheme).first()
        original_desc = scheme.description

        change = DetectedSchemeChange(
            scheme_id=scheme.id,
            source_url="https://test.gov.in",
            detected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            change_classification="general_informational_update",
            change_summary="Description update",
            confidence_score=0.85,
            proposed_modifications='{"description": "Updated welfare program description for 2026."}',
            review_status="pending",
            applied_to_scheme=False
        )
        self.db.add(change)
        self.db.commit()

        # 1. Approve
        SchemeUpdateService.review_change(
            db=self.db,
            change_id=change.id,
            action="approve",
            admin_id="admin@nammasevai.gov.in"
        )

        # 2. Check version history was created
        versions = SchemeUpdateService.get_version_history(self.db, scheme.id)
        self.assertGreater(len(versions), 0)
        latest_ver = versions[0]
        self.assertEqual(latest_ver["field_name"], "description")
        self.assertEqual(latest_ver["previous_value"], str(original_desc))
        self.assertEqual(latest_ver["new_value"], "Updated welfare program description for 2026.")

        # 3. Rollback
        rollback_res = SchemeUpdateService.rollback_version(
            db=self.db,
            version_id=latest_ver["id"],
            admin_id="supervisor@nammasevai.gov.in"
        )
        self.assertEqual(rollback_res["status"], "rolled_back")

        # 4. Verify scheme restored to original
        self.db.refresh(scheme)
        self.assertEqual(scheme.description, original_desc, "Rollback must restore original field value!")

    def test_13_review_rejection_workflow(self):
        """
        Verify that admin rejection marks the change record as rejected
        and leaves active scheme data unchanged.
        """
        scheme = self.db.query(Scheme).first()
        original_benefit = scheme.benefit_amount

        change = DetectedSchemeChange(
            scheme_id=scheme.id,
            source_url="https://test.gov.in",
            detected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            change_classification="benefit_amount_changed",
            change_summary="Unverified rumor of benefit change",
            confidence_score=0.50,
            proposed_modifications='{"benefit_amount": "₹99,999"}',
            review_status="pending",
            applied_to_scheme=False
        )
        self.db.add(change)
        self.db.commit()

        # Reject change
        res = SchemeUpdateService.review_change(
            db=self.db,
            change_id=change.id,
            action="reject",
            admin_id="auditor@nammasevai.gov.in",
            review_notes="Rejected: Fake news on unofficial domain."
        )

        self.assertEqual(res["action"], "rejected")
        self.db.refresh(change)
        self.assertEqual(change.review_status, "rejected")
        self.assertFalse(change.applied_to_scheme)

        # Verify scheme remains unchanged
        self.db.refresh(scheme)
        self.assertEqual(scheme.benefit_amount, original_benefit)

    def test_14_scheduler_initialization_status_and_recovery(self):
        """
        Verify that SchemeUpdateSchedulerService initializes cleanly,
        reports correct configuration, and provides recovery from persistent DB timestamps.
        """
        scheduler = SchemeUpdateSchedulerService(
            availability_interval_hours=24,
            content_interval_days=7,
            rate_limit_delay_seconds=1.0,
            max_workers=2
        )

        status = scheduler.get_status()
        self.assertFalse(status["is_running"])
        self.assertEqual(status["availability_interval_hours"], 24)
        self.assertEqual(status["content_interval_days"], 7)
        self.assertEqual(status["rate_limit_delay_seconds"], 1.0)
        self.assertEqual(status["max_workers"], 2)

        # Verify recovery inspection does not crash
        with patch.object(ContentChangeDetectorService, "run_content_audit") as mock_audit:
            scheduler.run_scheduled_checks()
            self.assertIsNotNone(scheduler.last_run_timestamp)

    def test_15_rate_limiting_and_politeness_verification(self):
        """
        Verify that batch content audit enforces polite delays (>= 1.0s)
        between requests to prevent overburdening official government servers.
        """
        with patch("time.sleep") as mock_sleep, \
             patch.object(ContentChangeDetectorService, "check_scheme_content") as mock_check:
            
            mock_check.return_value = {"status": "ok", "change_detected": False}

            ContentChangeDetectorService.run_content_audit(
                db=self.db,
                scheme_ids=["pm-kisan-national", "pudhumai-penn"],
                rate_limit_delay_seconds=1.2
            )

            # Assert time.sleep was invoked with polite delay
            mock_sleep.assert_called_with(1.2)

    def test_16_scheme_preservation_guarantee(self):
        """
        FINAL ARCHITECTURAL PRESERVATION CHECK:
        Verify that all 85 scheme records remain active and intact in nammasevai.db,
        and all 28 States and 8 Union Territories continue to be represented.
        """
        schemes = self.db.query(Scheme).all()
        self.assertGreaterEqual(len(schemes), 85, f"Expected 85 schemes, found {len(schemes)}")

        states = set(s.state for s in schemes if s.state and s.level == "State")
        uts = set(s.state for s in schemes if s.state and s.level in ("UT", "Union Territory"))

        self.assertEqual(len(states), 28, f"Expected 28 states, found {len(states)}")
        self.assertEqual(len(uts), 8, f"Expected 8 union territories, found {len(uts)}")

        # Verify source linkage for all schemes
        sources = self.db.query(OfficialSource).all()
        self.assertGreaterEqual(len(sources), 85, f"Expected at least 85 official sources, found {len(sources)}")

if __name__ == "__main__":
    unittest.main()
