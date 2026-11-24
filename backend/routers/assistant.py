from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.assistant import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    MatchRequest, 
    MatchResponse,
    ExtractedUserProfile,
    MissingInformationItem
)
from ..services.ai_service import ai_service
from ..services.matcher import SchemeMatcherService

router = APIRouter(prefix="/api/assistant", tags=["Citizen Assistant"])

matcher = SchemeMatcherService()

@router.post("/analyze", response_model=AnalyzeResponse, summary="Extract citizen profile and detect missing information")
def analyze_citizen_query(payload: AnalyzeRequest):
    """
    Analyzes citizen voice or typed text in Tamil, Tanglish, or English.
    Extracts age, occupation, income, district, education, voluntary attributes.
    Detects missing essential criteria and generates targeted follow-up questions.
    Uses Google Gemini API when configured, or verified Tamil/Tanglish NLP engine.
    """
    profile_dict, intents, missing_raw, config_instruction = ai_service.analyze_query(
        text=payload.text, 
        lang=payload.lang or "ta"
    )
    
    profile = ExtractedUserProfile(**profile_dict)
    missing_items = [
        MissingInformationItem(
            field_name=m["field_name"],
            relevance_to_scheme=m["relevance_to_scheme"],
            question_en=m["question_en"],
            question_ta=m["question_ta"],
            question_hi=m.get("question_hi"),
            question_ml=m.get("question_ml")
        )
        for m in missing_raw
    ]

    follow_ups_en = [item.question_en for item in missing_items]
    follow_ups_ta = [item.question_ta for item in missing_items]
    follow_ups_hi = [item.question_hi for item in missing_items if item.question_hi]
    follow_ups_ml = [item.question_ml for item in missing_items if item.question_ml]

    return AnalyzeResponse(
        original_text=payload.text,
        language=payload.lang or "ta",
        extracted_profile=profile,
        identified_categories=intents,
        missing_critical_info=missing_items,
        follow_up_questions_en=follow_ups_en,
        follow_up_questions_ta=follow_ups_ta,
        follow_up_questions_hi=follow_ups_hi,
        follow_up_questions_ml=follow_ups_ml
    )

@router.post("/match", response_model=MatchResponse, summary="Match schemes using structured eligibility conditions")
def match_citizen_schemes(payload: MatchRequest, db: Session = Depends(get_db)):
    """
    Evaluates candidate schemes against citizen profile using structured rules.
    Returns potential matches, explanations, required documents, application steps,
    official sources, and follow-up questions for unverified conditions.
    """
    profile = payload.profile
    missing_raw = []

    # If query text was provided, analyze it
    if payload.query:
        profile_dict, intents, missing_raw, config_instruction = ai_service.analyze_query(
            text=payload.query, 
            lang=payload.lang or "ta"
        )
        if not profile:
            profile = ExtractedUserProfile(**profile_dict)
        else:
            # Merge extracted fields into existing profile, allowing citizen corrections
            for k, v in profile_dict.items():
                if v is not None:
                    setattr(profile, k, v)

    if not profile:
        profile = ExtractedUserProfile()

    matches, follow_ups_en, follow_ups_ta = matcher.match_schemes(
        db=db,
        profile=profile,
        category=payload.category
    )

    follow_ups_hi = []
    follow_ups_ml = []

    # Append prompt follow-ups from extractor missing items ONLY if still unsupplied
    for m in missing_raw:
        fn = m.get("field_name")
        if fn and getattr(profile, fn, None) is not None:
            continue
        if m["question_en"] not in follow_ups_en:
            follow_ups_en.append(m["question_en"])
        if m["question_ta"] not in follow_ups_ta:
            follow_ups_ta.append(m["question_ta"])
        if m.get("question_hi") and m["question_hi"] not in follow_ups_hi:
            follow_ups_hi.append(m["question_hi"])
        if m.get("question_ml") and m["question_ml"] not in follow_ups_ml:
            follow_ups_ml.append(m["question_ml"])

    # Generate compassionate response text
    lang = payload.lang or "ta"
    response_msg = ai_service.generate_compassionate_response(
        query=payload.query or "",
        matches=matches,
        missing_info=missing_raw,
        lang=lang
    )

    return MatchResponse(
        total_potential_matches=len(matches),
        matches=matches,
        extracted_profile=profile,
        follow_up_questions_en=follow_ups_en,
        follow_up_questions_ta=follow_ups_ta,
        follow_up_questions_hi=follow_ups_hi,
        follow_up_questions_ml=follow_ups_ml,
        compassionate_response=response_msg
    )
