from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Scheme
from ..schemas import CitizenQueryRequest, CitizenQueryResponse, MatchedSchemeItem, SchemeResponse

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])

@router.post("/match", response_model=CitizenQueryResponse)
def match_citizen_query(payload: CitizenQueryRequest, db: Session = Depends(get_db)):
    schemes = db.query(Scheme).all()
    q = payload.query.lower()
    lang = payload.lang or "ta"

    matched_items = []
    # Keyword & Intent Matcher
    for s in schemes:
        score = 0
        reasons = []

        if "student" in q or "college" in q or "12th" in q or "மாணவி" in q or "கல்லூரி" in q:
            if s.category == "education":
                score += 50
                reasons.append("Matches education assistance criteria")
        
        if "farmer" in q or "land" in q or "crop" in q or "விவசாயி" in q:
            if s.category == "agriculture":
                score += 60
                reasons.append("Matches agricultural input subsidies")

        if "women" in q or "mother" in q or "தையல்" in q or "பெண்" in q:
            if s.category == "women":
                score += 45
                reasons.append("Matches women empowerment and financial aid")

        if score > 0:
            match_percent = min(score + 30, 98)
            matched_items.append(MatchedSchemeItem(
                scheme=SchemeResponse.from_orm(s),
                match_percent=match_percent,
                status="high" if match_percent >= 80 else "moderate",
                reason="; ".join(reasons) or "General eligibility match"
            ))

    matched_items.sort(key=lambda x: x.match_percent, reverse=True)

    count = len(matched_items)
    response_msg = (
        f"உங்கள் சூழ்நிலையை ஆய்வு செய்து {count} அரசு திட்டங்களை கண்டறிந்துள்ளேன்."
        if lang == "ta" else
        f"Identified {count} matching welfare programs based on your query."
    )

    return CitizenQueryResponse(
        query=payload.query,
        response_message=response_msg,
        matches=matched_items,
        detected_intent={"query_length": len(payload.query), "matched_count": count}
    )
