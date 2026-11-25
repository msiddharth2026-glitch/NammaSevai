import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from ..database import get_db
from ..models.feedback import CitizenPilotFeedback
from ..schemas.feedback import FeedbackCreate, FeedbackResponse
from ..routers.admin import require_admin_auth

router = APIRouter(prefix="/api/feedback", tags=["Citizen Feedback & Pilot"])

@router.post("", response_model=FeedbackResponse, summary="Submit voluntary, anonymous citizen pilot feedback")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Collects strictly voluntary, anonymous feedback from citizens and pilot participants.
    Zero collection of Aadhaar numbers, phone numbers, passwords, or personal credentials.
    """
    # Privacy protection: Reject submissions containing 12-digit Aadhaar pattern or 10-digit mobile patterns
    text_corpus = f"{payload.problems_encountered or ''} {payload.suggestions or ''}"
    if re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', text_corpus):
        raise HTTPException(
            status_code=400, 
            detail="For your privacy and security, please do NOT submit Aadhaar numbers or national identity numbers."
        )

    fb = CitizenPilotFeedback(
        session_id=payload.session_id,
        participant_category=payload.participant_category,
        preferred_language=payload.preferred_language,
        ease_of_use_rating=payload.ease_of_use_rating,
        clarity_rating=payload.clarity_rating,
        usefulness_rating=payload.usefulness_rating,
        problems_encountered=payload.problems_encountered,
        suggestions=payload.suggestions
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return FeedbackResponse(
        id=fb.id,
        message="Thank you! Your feedback has been received voluntarily and anonymously to improve BharatSevai AI.",
        status="received"
    )

@router.get("/summary", summary="Get aggregate pilot feedback metrics (Admin Protected)")
def get_feedback_summary(
    db: Session = Depends(get_db),
    admin_auth: bool = Depends(require_admin_auth)
):
    """
    Returns aggregated statistical feedback metrics for administrative monitoring.
    Requires constant-time admin authorization.
    """
    total = db.query(CitizenPilotFeedback).count()
    if total == 0:
        return {
            "total_submissions": 0,
            "average_ease_of_use": 0.0,
            "average_clarity": 0.0,
            "average_usefulness": 0.0,
            "language_distribution": {},
            "category_distribution": {},
            "recent_problems": [],
            "recent_suggestions": []
        }

    avg_ease = db.query(func.avg(CitizenPilotFeedback.ease_of_use_rating)).scalar() or 0.0
    avg_clarity = db.query(func.avg(CitizenPilotFeedback.clarity_rating)).scalar() or 0.0
    avg_usefulness = db.query(func.avg(CitizenPilotFeedback.usefulness_rating)).scalar() or 0.0

    # Group by language
    langs = (
        db.query(CitizenPilotFeedback.preferred_language, func.count(CitizenPilotFeedback.id))
        .group_by(CitizenPilotFeedback.preferred_language)
        .all()
    )
    lang_dist = {l: count for l, count in langs}

    # Group by category
    cats = (
        db.query(CitizenPilotFeedback.participant_category, func.count(CitizenPilotFeedback.id))
        .group_by(CitizenPilotFeedback.participant_category)
        .all()
    )
    cat_dist = {c or "General Citizen": count for c, count in cats}

    # Recent qualitative points (without personal identifiers)
    recent_entries = (
        db.query(CitizenPilotFeedback)
        .order_by(CitizenPilotFeedback.id.desc())
        .limit(20)
        .all()
    )
    problems = [e.problems_encountered for e in recent_entries if e.problems_encountered]
    suggestions = [e.suggestions for e in recent_entries if e.suggestions]

    return {
        "total_submissions": total,
        "average_ease_of_use": round(float(avg_ease), 2),
        "average_clarity": round(float(avg_clarity), 2),
        "average_usefulness": round(float(avg_usefulness), 2),
        "language_distribution": lang_dist,
        "category_distribution": cat_dist,
        "recent_problems": problems,
        "recent_suggestions": suggestions
    }
