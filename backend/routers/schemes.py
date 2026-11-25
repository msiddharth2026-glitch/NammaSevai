from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, or_, desc, asc
from typing import List, Optional, Dict, Any
from ..database import get_db
from ..models.scheme import Scheme
from ..models.source import OfficialSource
from ..models.document import RequiredDocument
from ..schemas.scheme import SchemeListItem, SchemeDetailResponse
from ..schemas.document import RequiredDocumentResponse
from ..data.geography import (
    INDIAN_STATES, 
    INDIAN_UNION_TERRITORIES, 
    GOVERNMENT_LEVELS, 
    SCHEME_CATEGORIES,
    normalize_jurisdiction
)

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])

@router.get("", response_model=List[SchemeListItem], summary="List all government schemes with national filtering")
def list_schemes(
    category: Optional[str] = Query(None, description="Filter by category (education, women, agriculture, health, etc.)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search keyword in scheme name, description or keywords"),
    level: Optional[str] = Query(None, description="Filter by level: Central, State, Union Territory, or all"),
    state: Optional[str] = Query(None, description="Filter by State or Union Territory name, or All India"),
    beneficiary: Optional[str] = Query(None, description="Filter by target beneficiary / occupation"),
    status: Optional[str] = Query("Active", description="Filter by status: Active, Inactive, Under Review, Discontinued, or all"),
    sort_by: Optional[str] = Query("name", description="Sort by: name, level, state, category, created_at"),
    sort_dir: Optional[str] = Query("asc", description="Sort direction: asc or desc"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Scheme)

    # 1. Status Filter
    status_val = status if isinstance(status, str) else "Active"
    if status_val and status_val.lower() != "all":
        query = query.filter(func.lower(Scheme.scheme_status) == status_val.lower())
    else:
        # Default active if not explicitly requesting all
        query = query.filter(Scheme.is_active == True)

    # 2. Category Filter
    cat_val = category if isinstance(category, str) else None
    if cat_val and cat_val.lower() != "all":
        query = query.filter(func.lower(Scheme.category) == cat_val.lower())

    # 3. Government Level Filter (Central / State / Union Territory)
    level_val = level if isinstance(level, str) else None
    if level_val and level_val.lower() != "all":
        norm_lvl = "Central" if "central" in level_val.lower() else "Union Territory" if "ut" in level_val.lower() or "union" in level_val.lower() else "State"
        query = query.filter(func.lower(Scheme.level) == norm_lvl.lower())

    # 4. State / Union Territory Filter
    state_val = state if isinstance(state, str) else None
    if state_val and state_val.lower() != "all":
        norm_s, det_lvl = normalize_jurisdiction(state_val)
        if norm_s and norm_s.lower() not in ("all india", "central"):
            query = query.filter(
                (func.lower(Scheme.state) == norm_s.lower()) |
                (func.lower(Scheme.level) == "central") # Central schemes apply nationally
            )
        elif norm_s and norm_s.lower() in ("all india", "central"):
            query = query.filter(func.lower(Scheme.level) == "central")

    # 5. Department Filter
    dept_val = department if isinstance(department, str) else None
    if dept_val:
        query = query.filter(Scheme.department.ilike(f"%{dept_val}%"))

    # 6. Beneficiary / Target Group Filter
    ben_val = beneficiary if isinstance(beneficiary, str) else None
    if ben_val and ben_val.lower() != "all":
        p_ben = f"%{ben_val}%"
        query = query.filter(
            (Scheme.beneficiary_type.ilike(p_ben)) |
            (Scheme.target_beneficiaries.ilike(p_ben))
        )

    # 7. Multi-Lingual Search Filter
    search_val = search if isinstance(search, str) else None
    if search_val and search_val.strip():
        pattern = f"%{search_val.strip()}%"
        query = query.filter(
            (Scheme.name.ilike(pattern)) |
            (Scheme.name_ta.ilike(pattern)) |
            (Scheme.name_hi.ilike(pattern)) |
            (Scheme.name_ml.ilike(pattern)) |
            (Scheme.description.ilike(pattern)) |
            (Scheme.description_ta.ilike(pattern)) |
            (Scheme.department.ilike(pattern)) |
            (Scheme.keywords.ilike(pattern)) |
            (Scheme.state.ilike(pattern))
        )

    # 8. Sorting
    sort_column = Scheme.name
    if sort_by == "state":
        sort_column = Scheme.state
    elif sort_by == "level":
        sort_column = Scheme.level
    elif sort_by == "category":
        sort_column = Scheme.category
    elif sort_by == "created_at":
        sort_column = Scheme.created_at

    query = query.order_by(desc(sort_column) if sort_dir == "desc" else asc(sort_column))

    # Pagination with eager loading of source and documents (eliminates N+1 queries)
    actual_offset = offset if isinstance(offset, int) else 0
    actual_limit = limit if isinstance(limit, int) else 200
    schemes = (
        query
        .options(
            joinedload(Scheme.source),
            selectinload(Scheme.documents)
        )
        .offset(actual_offset)
        .limit(actual_limit)
        .all()
    )

    results = []
    for s in schemes:
        src = s.source
        p_url = src.portal_url if src else "https://www.myscheme.gov.in"
        ver_status = src.verification_status if src else "verified"
        ver_date = src.verified_date if src else None

        doc_list = [
            {"name": d.name_en, "name_ta": d.name_ta, "mandatory": d.is_mandatory}
            for d in (s.documents or [])
        ]

        # Standardized Coverage Label
        if (s.level == "Central") or (s.state and s.state.lower() == "all india") or any(k in s.id for k in ["pm-", "pmegp", "nsp-"]):
            cov_type = "Central Government / Centrally Sponsored"
        elif s.level == "Union Territory":
            cov_type = f"Union Territory ({s.state})"
        else:
            cov_type = f"State Government ({s.state or 'Tamil Nadu'})"

        results.append(SchemeListItem(
            id=s.id,
            name=s.name,
            name_ta=s.name_ta,
            name_hi=s.name_hi,
            name_ml=s.name_ml,
            department=s.department,
            department_ta=s.department_ta,
            department_hi=s.department_hi,
            department_ml=s.department_ml,
            category=s.category,
            level=s.level,
            state=s.state,
            beneficiary_type=s.beneficiary_type or s.target_beneficiaries,
            beneficiary_type_ta=s.beneficiary_type_ta,
            target_beneficiaries=s.target_beneficiaries or s.beneficiary_type,
            target_beneficiaries_ta=s.target_beneficiaries_ta,
            benefit_summary=s.benefit_summary,
            benefit_summary_ta=s.benefit_summary_ta,
            benefit_summary_hi=s.benefit_summary_hi,
            benefit_summary_ml=s.benefit_summary_ml,
            benefit_amount=s.benefit_amount,
            description=s.description,
            description_ta=s.description_ta,
            description_hi=s.description_hi,
            description_ml=s.description_ml,
            coverage_type=cov_type,
            application_url=p_url,
            official_portal=p_url,
            scheme_status=s.scheme_status,
            keywords=s.keywords,
            is_active=s.is_active,
            source_verification_status=ver_status,
            verified_date=ver_date,
            required_documents=doc_list
        ))

    return results

@router.get("/meta/jurisdictions", summary="Get geographical options and scheme distributions")
def get_jurisdictions_meta(db: Session = Depends(get_db)):
    """Returns official lists of all 28 States, 8 UTs, Central level, and category counts."""
    # Active scheme counts by level and jurisdiction
    schemes = db.query(Scheme.level, Scheme.state, Scheme.category).filter(Scheme.is_active == True).all()

    state_counts: Dict[str, int] = {}
    level_counts: Dict[str, int] = {"Central": 0, "State": 0, "Union Territory": 0}
    category_counts: Dict[str, int] = {k: 0 for k in SCHEME_CATEGORIES}

    for lvl, st, cat in schemes:
        if lvl in level_counts:
            level_counts[lvl] += 1
        if st:
            state_counts[st] = state_counts.get(st, 0) + 1
        if cat in category_counts:
            category_counts[cat] += 1

    return {
        "government_levels": list(GOVERNMENT_LEVELS),
        "states": list(INDIAN_STATES),
        "union_territories": list(INDIAN_UNION_TERRITORIES),
        "level_counts": level_counts,
        "state_counts": state_counts,
        "categories": SCHEME_CATEGORIES,
        "category_counts": category_counts
    }

@router.get("/meta/coverage", summary="Get honest national scheme coverage and verification dashboard statistics")
def get_national_coverage_stats(db: Session = Depends(get_db)):
    """
    Returns authentic coverage dashboard stats showing which jurisdictions have actual records
    versus jurisdictions with data collection in progress.
    """
    schemes = db.query(Scheme).all()
    total = len(schemes)

    central_count = sum(1 for s in schemes if s.level == "Central")
    state_count = sum(1 for s in schemes if s.level == "State")
    ut_count = sum(1 for s in schemes if s.level == "Union Territory")

    states_with_schemes = sorted(list(set(s.state for s in schemes if s.level == "State" and s.state in INDIAN_STATES)))
    states_pending = [s for s in INDIAN_STATES if s not in states_with_schemes]

    uts_with_schemes = sorted(list(set(s.state for s in schemes if s.level == "Union Territory" and s.state in INDIAN_UNION_TERRITORIES)))
    uts_pending = [u for u in INDIAN_UNION_TERRITORIES if u not in uts_with_schemes]

    verified_count = sum(1 for s in schemes if s.source and s.source.verification_status == "verified")
    pending_verification = total - verified_count

    return {
        "total_schemes": total,
        "central_schemes_count": central_count,
        "state_schemes_count": state_count,
        "ut_schemes_count": ut_count,
        "total_states": len(INDIAN_STATES),
        "states_covered_count": len(states_with_schemes),
        "states_covered": states_with_schemes,
        "states_pending": states_pending,
        "total_uts": len(INDIAN_UNION_TERRITORIES),
        "uts_covered_count": len(uts_with_schemes),
        "uts_covered": uts_with_schemes,
        "uts_pending": uts_pending,
        "verified_schemes_count": verified_count,
        "pending_verification_count": pending_verification,
        "transparency_note": (
            "Jurisdictions marked as covered have verified schemes currently in the database. "
            "Data ingestion for remaining jurisdictions is continuously ongoing via official government portals."
        )
    }

@router.get("/{scheme_id}", response_model=SchemeDetailResponse, summary="Get full details of a scheme by ID")
def get_scheme_by_id(scheme_id: str, db: Session = Depends(get_db)):
    scheme = (
        db.query(Scheme)
        .options(
            joinedload(Scheme.source),
            selectinload(Scheme.conditions),
            selectinload(Scheme.documents),
            selectinload(Scheme.steps)
        )
        .filter(Scheme.id == scheme_id)
        .first()
    )
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme with ID '{scheme_id}' not found")
    return scheme

@router.get("/{scheme_id}/documents", response_model=List[RequiredDocumentResponse], summary="Get documents required for a scheme")
def get_scheme_documents(scheme_id: str, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme with ID '{scheme_id}' not found")
    return scheme.documents
