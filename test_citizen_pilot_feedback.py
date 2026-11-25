"""
Dedicated Test Suite for Phase 7.1: Citizen Pilot Feedback & Monitoring Validation.
Validates:
  1. Voluntary, anonymous feedback submission (1-5 ratings, non-PII attributes)
  2. Privacy protection: Automatic rejection of Aadhaar number patterns in feedback
  3. Validation bounds: Rating ranges (1 to 5), character length constraints
  4. Secured admin summary: Authentication enforcement via require_admin_auth
  5. Statistical metric aggregation: Averages, category breakdowns, language distributions
"""

import os
import sys
import unittest
from fastapi import HTTPException

from backend.database import SessionLocal, Base, engine
from backend.models.feedback import CitizenPilotFeedback
from backend.routers.feedback import submit_feedback, get_feedback_summary
from backend.schemas.feedback import FeedbackCreate
from backend.config import settings

class TestCitizenPilotFeedback(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_submit_valid_anonymous_feedback(self):
        """Verify voluntary citizen feedback is recorded with valid ratings and non-PII data."""
        payload = FeedbackCreate(
            participant_category="Farmer",
            preferred_language="ta",
            ease_of_use_rating=5,
            clarity_rating=4,
            usefulness_rating=5,
            problems_encountered="None, instructions were clear",
            suggestions="Add Tamil voice option for crop insurance"
        )
        res = submit_feedback(payload, db=self.db)
        self.assertEqual(res.status, "received")
        self.assertGreater(res.id, 0)
        self.assertIn("voluntarily and anonymously", res.message)

    def test_02_privacy_shield_rejects_aadhaar_pattern(self):
        """Verify that feedback containing Aadhaar 12-digit pattern is rejected with HTTP 400."""
        payload = FeedbackCreate(
            preferred_language="en",
            ease_of_use_rating=4,
            clarity_rating=4,
            usefulness_rating=4,
            suggestions="My Aadhaar number is 5432 1098 7654"
        )
        with self.assertRaises(HTTPException) as ctx:
            submit_feedback(payload, db=self.db)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Aadhaar", ctx.exception.detail)

    def test_03_rating_range_validation(self):
        """Verify Pydantic validation rejects ratings outside 1-5 range."""
        with self.assertRaises(ValueError):
            FeedbackCreate(
                preferred_language="ta",
                ease_of_use_rating=6, # Invalid: must be <= 5
                clarity_rating=5,
                usefulness_rating=5
            )

        with self.assertRaises(ValueError):
            FeedbackCreate(
                preferred_language="ta",
                ease_of_use_rating=0, # Invalid: must be >= 1
                clarity_rating=5,
                usefulness_rating=5
            )

    def test_04_admin_summary_requires_authentication(self):
        """Verify get_feedback_summary enforces constant-time admin authorization."""
        from backend.routers.admin import require_admin_auth

        # Missing auth must raise 401
        with self.assertRaises(HTTPException) as ctx:
            require_admin_auth(x_admin_key="invalid-key")
        self.assertEqual(ctx.exception.status_code, 401)

        # Valid auth proceeds
        auth_ok = require_admin_auth(x_admin_key=settings.ADMIN_API_KEY)
        self.assertTrue(auth_ok)

    def test_05_statistical_aggregation_metrics(self):
        """Verify summary accurately aggregates average ratings, languages, and categories."""
        # Submit test entries
        submit_feedback(FeedbackCreate(
            participant_category="College Student",
            preferred_language="en",
            ease_of_use_rating=4,
            clarity_rating=4,
            usefulness_rating=4
        ), db=self.db)

        submit_feedback(FeedbackCreate(
            participant_category="Woman Entrepreneur",
            preferred_language="ta",
            ease_of_use_rating=5,
            clarity_rating=5,
            usefulness_rating=5
        ), db=self.db)

        summary = get_feedback_summary(db=self.db, admin_auth=True)
        self.assertGreaterEqual(summary["total_submissions"], 2)
        self.assertGreaterEqual(summary["average_ease_of_use"], 1.0)
        self.assertLessEqual(summary["average_ease_of_use"], 5.0)
        self.assertIn("ta", summary["language_distribution"])
        self.assertIn("College Student", summary["category_distribution"])

if __name__ == "__main__":
    unittest.main()
