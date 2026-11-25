import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status, Body, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from ..database import get_db
from ..config import settings
from ..models.scheme import Scheme
from ..models.condition import EligibilityCondition
from ..models.document import RequiredDocument
from ..models.step import ApplicationStep
from ..models.source import OfficialSource
from ..schemas.scheme import SchemeCreate, SchemeDetailResponse, SchemeUpdate, BulkImportReport
from ..services.scheme_importer import SchemeImporterService
from ..data.geography import INDIAN_STATES, INDIAN_UNION_TERRITORIES

logger = logging.getLogger("nammasevai.admin_audit")

router = APIRouter(prefix="/api/admin", tags=["Admin Portal"])

def require_admin_auth(
    request: Request = None,
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Constant-time authenticated administrator verification.
    Accepts 'X-Admin-Key', 'X-Admin-Token', or 'Authorization: Bearer <key>'.
    Protects against timing attacks and logs all unauthorized attempts.
    """
    provided_key = None
    if isinstance(x_admin_key, str) and x_admin_key:
        provided_key = x_admin_key
    elif isinstance(x_admin_token, str) and x_admin_token:
        provided_key = x_admin_token
    elif isinstance(authorization, str) and authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            provided_key = parts[1]
        else:
            provided_key = authorization.strip()

    client_ip = request.client.host if (request and request.client) else "unknown"
    path = request.url.path if request else "admin_endpoint"

    if not provided_key:
        logger.warning(f"SECURITY AUDIT: Unauthorized admin access attempt from IP {client_ip} on {path} (missing credentials)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access denied: Valid administrator key or bearer token required."
        )

    # Valid keys: configured ADMIN_API_KEY
    is_valid = secrets.compare_digest(provided_key, settings.ADMIN_API_KEY)

    # Development/testing fallback keys when not running in strict production mode
    if not is_valid and settings.APP_ENV != "production":
        dev_keys = ["nammasevai-admin-dev-secret", "nammasevai-admin-secret-2026"]
        is_valid = any(secrets.compare_digest(provided_key, dk) for dk in dev_keys)

    if not is_valid:
        logger.warning(f"SECURITY AUDIT: Invalid admin credentials presented from IP {client_ip} on {path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access denied: Invalid administrator credentials."
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

    # 1. Create Scheme base record with geographical classification
    scheme = Scheme(
        id=payload.id,
        name=payload.name,
        name_ta=payload.name_ta,
        name_hi=payload.name_hi,
        name_ml=payload.name_ml,
        department=payload.department,
        department_ta=payload.department_ta,
        department_hi=payload.department_hi,
        department_ml=payload.department_ml,
        category=payload.category,
        level=payload.level or "State",
        state=payload.state or ("All India" if payload.level == "Central" else "Tamil Nadu"),
        beneficiary_type=payload.beneficiary_type,
        beneficiary_type_ta=payload.beneficiary_type_ta,
        target_beneficiaries=payload.target_beneficiaries or payload.beneficiary_type,
        target_beneficiaries_ta=payload.target_beneficiaries_ta,
        benefit_summary=payload.benefit_summary,
        benefit_summary_ta=payload.benefit_summary_ta,
        benefit_summary_hi=payload.benefit_summary_hi,
        benefit_summary_ml=payload.benefit_summary_ml,
        benefit_amount=payload.benefit_amount,
        description=payload.description,
        description_ta=payload.description_ta,
        description_hi=payload.description_hi,
        description_ml=payload.description_ml,
        keywords=payload.keywords,
        scheme_status=payload.scheme_status or "Active",
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

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if hasattr(scheme, field) and val is not None:
            setattr(scheme, field, val)

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
            source_name="Official Portal of India",
            portal_url="https://www.myscheme.gov.in",
            verified_date="2026-11-24",
            verification_status="verified"
        )
        db.add(src)
    else:
        src.verification_status = "pending_recheck" if src.verification_status == "verified" else "verified"

    db.commit()
    return {"scheme_id": scheme_id, "verification_status": src.verification_status}

@router.post("/schemes/import", response_model=BulkImportReport, summary="Bulk import schemes from JSON or CSV")
def bulk_import_schemes(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    """
    Ingests and validates batch scheme records in JSON list or raw CSV format.
    Ensures duplicate prevention, verification metadata tracking, and returns detailed audit report.
    """
    allow_overwrite = payload.get("allow_overwrite", False)
    records = []

    if "records" in payload and isinstance(payload["records"], list):
        records = payload["records"]
    elif "csv_content" in payload and isinstance(payload["csv_content"], str):
        records = SchemeImporterService.parse_csv_content(payload["csv_content"])
    elif isinstance(payload, list):
        records = payload
    else:
        raise HTTPException(status_code=400, detail="Invalid import payload: Must contain 'records' list or 'csv_content' string.")

    if not records:
        raise HTTPException(status_code=400, detail="No scheme records provided in import payload.")

    report = SchemeImporterService.import_records(
        db=db,
        records=records,
        allow_overwrite=allow_overwrite
    )
    return report

@router.get("/stats", summary="Get admin dashboard overview metrics including national coverage")
def get_admin_stats(
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    schemes = db.query(Scheme).all()
    total_schemes = len(schemes)
    categories = len(set(s.category for s in schemes))
    
    central_count = sum(1 for s in schemes if s.level == "Central")
    state_count = sum(1 for s in schemes if s.level == "State")
    ut_count = sum(1 for s in schemes if s.level == "Union Territory")

    states_represented = len(set(s.state for s in schemes if s.level == "State" and s.state in INDIAN_STATES))
    uts_represented = len(set(s.state for s in schemes if s.level == "Union Territory" and s.state in INDIAN_UNION_TERRITORIES))

    verified_count = sum(1 for s in schemes if s.source and (s.source.verification_status or "").lower() == "verified")
    pending_count = total_schemes - verified_count
    inactive_count = sum(1 for s in schemes if not s.is_active or s.scheme_status == "Inactive")

    return {
        "total_schemes": total_schemes,
        "central_schemes": central_count,
        "state_schemes": state_count,
        "ut_schemes": ut_count,
        "states_represented": states_represented,
        "uts_represented": uts_represented,
        "verified_sources": verified_count,
        "pending_review": pending_count,
        "inactive_schemes": inactive_count,
        "active_categories": categories
    }

@router.post("/portal-monitor/run", summary="Trigger automated official portal health check")
def run_portal_health_check_endpoint(
    scheme_ids: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    """
    Executes automated URL health, latency, redirect, and domain migration checks
    across stored official government portals.
    """
    from ..services.portal_health_monitor import PortalHealthMonitorService
    summary = PortalHealthMonitorService.run_health_checks(db=db, scheme_ids=scheme_ids)
    return summary

@router.get("/portal-monitor/status", summary="Get official portal health summary")
def get_portal_health_status_endpoint(
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    """
    Retrieves latest health monitoring summary, availability rates, redirects, and broken portals.
    """
    from ..services.portal_health_monitor import PortalHealthMonitorService
    return PortalHealthMonitorService.get_latest_summary(db=db)

@router.get("/portal-monitor/schemes", summary="Get scheme-by-scheme portal health details")
def get_portal_health_schemes_endpoint(
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    """Returns portal health and verification details for every individual scheme."""
    from ..services.portal_health_monitor import PortalHealthMonitorService
    summary = PortalHealthMonitorService.get_latest_summary(db=db)
    return summary.broken_portals

@router.get("/ai-providers/status", summary="Get real-time AI provider metrics, priority sequence and circuit status")
def get_admin_ai_providers_status(authorized: bool = Depends(require_admin_auth)):
    """
    Returns detailed health, latency metrics, call counts, failure reasons,
    and circuit breaker states for OpenAI, Grok, Gemini, and Rule Engine.
    Strictly scrubs and suppresses all API keys and authorization tokens.
    """
    from ..services.ai_service import ai_service
    return ai_service.get_safe_status()

@router.post("/ai-providers/reload", summary="Reload AI provider configurations from environment")
def reload_ai_providers_config(authorized: bool = Depends(require_admin_auth)):
    """Hot-reloads configuration and API keys from environment settings."""
    from ..services.ai_provider_manager import ai_provider_manager
    ai_provider_manager.reload_config()
    return {"message": "AI Provider configurations reloaded successfully"}

@router.get("/quality-benchmark", summary="Run recommendation quality & accuracy benchmark")
def get_quality_benchmark_endpoint(
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    """
    Executes the citizen profile recommendation benchmark across 35 synthetic personas.
    Computes false positive/negative rates, state isolation compliance, mandatory condition compliance,
    and returns transparent quality statistics labeled strictly as synthetic test benchmarks.
    """
    from ..services.profile_benchmark import ProfileBenchmarkService
    return ProfileBenchmarkService.run_benchmark(db=db)

# -----------------------------------------------------------------------------
# Phase 5: Automated Government Scheme Content Monitoring & Policy Change APIs
# -----------------------------------------------------------------------------

@router.get("/content-monitor/summary", summary="Get automated content monitoring summary")
def get_content_monitor_summary_endpoint(
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    from ..services.scheme_update_service import scheme_update_service
    return scheme_update_service.get_monitoring_summary(db=db)

@router.get("/content-monitor/sources", summary="List registered government scheme sources")
def get_content_monitor_sources_endpoint(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    query = db.query(OfficialSource)
    if category and category != "all":
        query = query.filter(OfficialSource.source_category == category)
    sources = query.all()
    return [
        {
            "id": s.id,
            "scheme_id": s.scheme_id,
            "source_name": s.source_name,
            "portal_url": s.portal_url,
            "source_category": s.source_category or "Official Portal",
            "ministry_department": s.ministry_department,
            "assigned_administrator": s.assigned_administrator,
            "verification_status": s.verification_status,
            "monitoring_status": s.monitoring_status or "active",
            "last_content_check": s.last_content_check,
            "last_detected_modification": s.last_detected_modification,
            "content_fingerprint": s.content_fingerprint,
            "content_length": s.content_length
        }
        for s in sources
    ]

@router.post("/content-monitor/run", summary="Trigger automated content change detection audit")
def run_content_monitor_audit_endpoint(
    scheme_ids: Optional[List[str]] = Body(None),
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    from ..services.content_change_detector import ContentChangeDetectorService
    return ContentChangeDetectorService.run_content_audit(db=db, scheme_ids=scheme_ids)

@router.get("/content-monitor/changes", summary="List detected scheme policy changes")
def list_detected_changes_endpoint(
    review_status: Optional[str] = Query(None),
    classification: Optional[str] = Query(None),
    scheme_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    from ..services.scheme_update_service import scheme_update_service
    return scheme_update_service.list_detected_changes(
        db=db, 
        review_status=review_status, 
        classification=classification, 
        scheme_id=scheme_id
    )

@router.get("/content-monitor/changes/{change_id}", summary="Get detected change comparison dossier")
def get_detected_change_detail_endpoint(
    change_id: int,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    from ..services.scheme_update_service import scheme_update_service
    detail = scheme_update_service.get_change_detail(db=db, change_id=change_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Detected change with ID {change_id} not found.")
    return detail

@router.post("/content-monitor/changes/{change_id}/review", summary="Review detected change (Approve/Reject/Request Evidence)")
def review_detected_change_endpoint(
    change_id: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    from ..services.scheme_update_service import scheme_update_service
    action = payload.get("action", "reject")
    admin_id = payload.get("admin_id", "admin@nammasevai.gov.in")
    review_notes = payload.get("review_notes")
    field_overrides = payload.get("field_overrides")

    try:
        return scheme_update_service.review_change(
            db=db,
            change_id=change_id,
            action=action,
            admin_id=admin_id,
            review_notes=review_notes,
            field_overrides=field_overrides
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/schemes/{scheme_id}/version-history", summary="Get scheme version history and audit log")
def get_scheme_version_history_endpoint(
    scheme_id: str,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    from ..services.scheme_update_service import scheme_update_service
    return scheme_update_service.get_version_history(db=db, scheme_id=scheme_id)

@router.post("/version-history/{version_id}/rollback", summary="Rollback approved modification to previous version")
def rollback_version_endpoint(
    version_id: int,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_admin_auth)
):
    from ..services.scheme_update_service import scheme_update_service
    admin_id = payload.get("admin_id", "admin@nammasevai.gov.in")
    try:
        return scheme_update_service.rollback_version(db=db, version_id=version_id, admin_id=admin_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scheduler/status", summary="Get background monitoring scheduler status")
def get_scheduler_status_endpoint(authorized: bool = Depends(require_admin_auth)):
    from ..services.scheme_update_scheduler import scheme_update_scheduler
    return scheme_update_scheduler.get_status()
