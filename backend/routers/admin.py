from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from ..database import get_db
from ..config import settings
from ..models.scheme import Scheme
from ..models.condition import EligibilityCondition
from ..models.document import RequiredDocument
from ..models.step import ApplicationStep
from ..models.source import OfficialSource
from ..schemas.scheme import SchemeCreate, SchemeDetailResponse, SchemeUpdate

router = APIRouter(prefix="/api/admin", tags=["Admin Portal"])

def require_admin_auth(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """
    Enforces admin authentication on all scheme mutation endpoints.
    Requires 'X-Admin-Key' header matching configured settings.ADMIN_API_KEY.
    """
    if not x_admin_key or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access denied: Valid 'X-Admin-Key' header required."
        )
    return True

@router.post("/schemes", response_model=SchemeDetailResponse, status_code=status.HTTP_201_CREATED, summary="Create a new government scheme")
def create_scheme(
    payload: SchemeCreate, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    existing = db.query(Scheme).filter(Scheme.id == payload.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Scheme with ID '{payload.id}' already exists."
        )

    # 1. Create Scheme base record
    scheme = Scheme(
        id=payload.id,
        name=payload.name,
        name_ta=payload.name_ta,
        department=payload.department,
        department_ta=payload.department_ta,
        category=payload.category,
        beneficiary_type=payload.beneficiary_type,
        beneficiary_type_ta=payload.beneficiary_type_ta,
        benefit_summary=payload.benefit_summary,
        benefit_summary_ta=payload.benefit_summary_ta,
        benefit_amount=payload.benefit_amount,
        description=payload.description,
        description_ta=payload.description_ta,
        is_active=payload.is_active
    )
    db.add(scheme)
    db.flush()

    # 2. Add conditions
    for cond in payload.conditions:
        db.add(EligibilityCondition(
            scheme_id=scheme.id,
            field_name=cond.field_name,
            operator=cond.operator,
            expected_value=cond.expected_value,
            is_mandatory=cond.is_mandatory,
            description_en=cond.description_en,
            description_ta=cond.description_ta,
            prompt_question_en=cond.prompt_question_en,
            prompt_question_ta=cond.prompt_question_ta
        ))

    # 3. Add documents
    for doc in payload.documents:
        db.add(RequiredDocument(
            scheme_id=scheme.id,
            name_en=doc.name_en,
            name_ta=doc.name_ta,
            is_mandatory=doc.is_mandatory,
            issuing_authority_en=doc.issuing_authority_en,
            issuing_authority_ta=doc.issuing_authority_ta,
            description_en=doc.description_en,
            description_ta=doc.description_ta,
            document_code=doc.document_code
        ))

    # 4. Add steps
    for step in payload.steps:
        db.add(ApplicationStep(
            scheme_id=scheme.id,
            step_number=step.step_number,
            mode=step.mode,
            title_en=step.title_en,
            title_ta=step.title_ta,
            description_en=step.description_en,
            description_ta=step.description_ta,
            portal_url=step.portal_url,
            office_name_en=step.office_name_en,
            office_name_ta=step.office_name_ta
        ))

    # 5. Add official source
    if payload.source:
        db.add(OfficialSource(
            scheme_id=scheme.id,
            source_name=payload.source.source_name,
            portal_url=payload.source.portal_url,
            verified_date=payload.source.verified_date,
            verification_status=payload.source.verification_status,
            helpline_number=payload.source.helpline_number,
            government_order_ref=payload.source.government_order_ref,
            notes=payload.source.notes
        ))

    db.commit()
    db.refresh(scheme)
    return scheme

@router.put("/schemes/{scheme_id}", response_model=SchemeDetailResponse, summary="Update scheme details")
def update_scheme(
    scheme_id: str, 
    payload: SchemeUpdate, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")

    update_dict = payload.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(scheme, k, v)

    db.commit()
    db.refresh(scheme)
    return scheme

@router.delete("/schemes/{scheme_id}", summary="Delete a scheme")
def delete_scheme(
    scheme_id: str, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")
    
    db.delete(scheme)
    db.commit()
    return {"message": f"Scheme '{scheme_id}' deleted successfully"}

@router.post("/schemes/{scheme_id}/toggle-status", summary="Toggle source verification status")
def toggle_verification_status(
    scheme_id: str, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")

    src = scheme.source
    if not src:
        src = OfficialSource(
            scheme_id=scheme.id,
            source_name="Tamil Nadu Government Portal",
            portal_url="https://www.tn.gov.in",
            verified_date="2026-11-23",
            verification_status="verified"
        )
        db.add(src)
    else:
        src.verification_status = "pending_recheck" if src.verification_status == "verified" else "verified"

    db.commit()
    return {"scheme_id": scheme_id, "verification_status": src.verification_status}

@router.get("/stats", summary="Get admin dashboard overview metrics")
def get_admin_stats(
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    schemes = db.query(Scheme).all()
    total_schemes = len(schemes)
    categories = len(set(s.category for s in schemes))
    
    verified_count = sum(1 for s in schemes if s.source and s.source.verification_status == "verified")
    pending_count = total_schemes - verified_count

    return {
        "total_schemes": total_schemes,
        "verified_sources": verified_count,
        "pending_review": pending_count,
        "active_categories": categories
    }
