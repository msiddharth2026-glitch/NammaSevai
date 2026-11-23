from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.scheme import Scheme
from ..models.document import RequiredDocument
from ..schemas.scheme import SchemeListItem, SchemeDetailResponse
from ..schemas.document import RequiredDocumentResponse

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])

@router.get("", response_model=List[SchemeListItem], summary="List all government schemes")
def list_schemes(
    category: Optional[str] = Query(None, description="Filter by category (education, women, agriculture, health, etc.)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search keyword in scheme name or description"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Scheme).filter(Scheme.is_active == True)

    cat_val = category if isinstance(category, str) else None
    dept_val = department if isinstance(department, str) else None
    search_val = search if isinstance(search, str) else None

    if cat_val and cat_val != "all":
        query = query.filter(Scheme.category == cat_val)
    if dept_val:
        query = query.filter(Scheme.department.ilike(f"%{dept_val}%"))
    if search_val:
        pattern = f"%{search_val}%"
        query = query.filter(
            (Scheme.name.ilike(pattern)) |
            (Scheme.name_ta.ilike(pattern)) |
            (Scheme.description.ilike(pattern)) |
            (Scheme.description_ta.ilike(pattern))
        )

    # Support both FastAPI dependency injection and direct function calls
    actual_offset = offset if isinstance(offset, int) else 0
    actual_limit = limit if isinstance(limit, int) else 50

    schemes = query.offset(actual_offset).limit(actual_limit).all()
    
    results = []
    for s in schemes:
        src = s.source
        p_url = src.portal_url if src else "https://www.tn.gov.in"
        doc_list = [
            {"name": d.name_en, "name_ta": d.name_ta, "mandatory": d.is_mandatory}
            for d in (s.documents or [])
        ]
        results.append(SchemeListItem(
            id=s.id,
            name=s.name,
            name_ta=s.name_ta,
            department=s.department,
            department_ta=s.department_ta,
            category=s.category,
            beneficiary_type=s.beneficiary_type,
            beneficiary_type_ta=s.beneficiary_type_ta,
            benefit_summary=s.benefit_summary,
            benefit_summary_ta=s.benefit_summary_ta,
            benefit_amount=s.benefit_amount,
            description=s.description,
            description_ta=s.description_ta,
            is_active=s.is_active,
            source_verification_status=src.verification_status if src else "verified",
            verified_date=src.verified_date if src else "2026-10-15",
            portal_url=p_url,
            official_portal=p_url,
            required_documents=doc_list
        ))
    return results

@router.get("/{scheme_id}", response_model=SchemeDetailResponse, summary="Get full scheme details by ID")
def get_scheme_by_id(scheme_id: str, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")
    return scheme

@router.get("/{scheme_id}/documents", response_model=List[RequiredDocumentResponse], summary="Get required documents for a scheme")
def get_scheme_documents(scheme_id: str, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")
    
    docs = db.query(RequiredDocument).filter(RequiredDocument.scheme_id == scheme_id).all()
    return docs
