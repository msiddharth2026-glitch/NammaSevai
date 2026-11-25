import json
import logging
import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.source import OfficialSource, DetectedSchemeChange, SchemeVersionHistory
from ..models.scheme import Scheme

logger = logging.getLogger("nammasevai.scheme_update_service")

class SchemeUpdateService:
    """
    Manages the Human Administrator Approval Workflow, Scheme Versioning,
    and Rollback Mechanism for detected government scheme updates.

    MANDATORY CIVIC GUARANTEE:
    No automated script, web scraper, or AI model can directly alter
    active statutory eligibility conditions or scheme records.
    Every modification strictly requires an authenticated human administrator decision.
    """

    @classmethod
    def get_monitoring_summary(cls, db: Session) -> Dict[str, Any]:
        """
        Retrieves real-time aggregated metrics for the Admin Monitoring Dashboard.
        """
        total_sources = db.query(OfficialSource).count()
        checked_sources = db.query(OfficialSource).filter(OfficialSource.last_content_check.isnot(None)).count()
        unavailable_sources = db.query(OfficialSource).filter(
            (OfficialSource.verification_status == "Source Unavailable") |
            (OfficialSource.http_status >= 400)
        ).count()
        
        pending_reviews = db.query(DetectedSchemeChange).filter(DetectedSchemeChange.review_status == "pending").count()
        approved_count = db.query(DetectedSchemeChange).filter(DetectedSchemeChange.review_status == "approved").count()
        rejected_count = db.query(DetectedSchemeChange).filter(DetectedSchemeChange.review_status == "rejected").count()
        evidence_req_count = db.query(DetectedSchemeChange).filter(DetectedSchemeChange.review_status == "evidence_requested").count()
        total_changes = db.query(DetectedSchemeChange).count()

        latest_change = db.query(DetectedSchemeChange).order_by(desc(DetectedSchemeChange.detected_at)).first()
        last_run = latest_change.detected_at if latest_change else "Not Yet Run"

        # Calculate next scheduled run (weekly default for content, daily for network)
        next_run = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime("%Y-%m-%d 02:00:00 UTC")

        return {
            "total_registered_sources": total_sources,
            "sources_checked": checked_sources,
            "sources_unavailable": unavailable_sources,
            "new_content_changes_detected": total_changes,
            "pending_administrator_reviews": pending_reviews,
            "approved_updates": approved_count,
            "rejected_updates": rejected_count,
            "evidence_requested_updates": evidence_req_count,
            "last_monitoring_run": last_run,
            "next_scheduled_run": next_run
        }

    @classmethod
    def list_detected_changes(
        cls, 
        db: Session, 
        review_status: Optional[str] = None,
        classification: Optional[str] = None,
        scheme_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lists detected scheme changes with optional filtering for the Admin Review Queue.
        """
        query = db.query(DetectedSchemeChange)
        if review_status and review_status != "all":
            query = query.filter(DetectedSchemeChange.review_status == review_status)
        if classification and classification != "all":
            query = query.filter(DetectedSchemeChange.change_classification == classification)
        if scheme_id:
            query = query.filter(DetectedSchemeChange.scheme_id == scheme_id)

        changes = query.order_by(desc(DetectedSchemeChange.detected_at)).all()
        results = []

        for ch in changes:
            scheme = ch.scheme
            results.append({
                "id": ch.id,
                "scheme_id": ch.scheme_id,
                "scheme_name": scheme.name if scheme else ch.scheme_id,
                "scheme_category": scheme.category if scheme else "Unknown",
                "scheme_state": scheme.state if scheme else "All India",
                "source_url": ch.source_url,
                "detected_at": ch.detected_at,
                "change_classification": ch.change_classification,
                "change_summary": ch.change_summary,
                "confidence_score": ch.confidence_score,
                "review_status": ch.review_status,
                "reviewed_by": ch.reviewed_by,
                "reviewed_at": ch.reviewed_at,
                "applied_to_scheme": ch.applied_to_scheme
            })

        return results

    @classmethod
    def get_change_detail(cls, db: Session, change_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed comparison dossier for a detected change including excerpts, diff, and proposed changes.
        """
        ch = db.query(DetectedSchemeChange).filter(DetectedSchemeChange.id == change_id).first()
        if not ch:
            return None

        scheme = ch.scheme
        proposed = {}
        if ch.proposed_modifications:
            try:
                proposed = json.loads(ch.proposed_modifications)
            except Exception:
                pass

        return {
            "id": ch.id,
            "scheme_id": ch.scheme_id,
            "scheme_name": scheme.name if scheme else ch.scheme_id,
            "scheme_department": scheme.department if scheme else "",
            "source_url": ch.source_url,
            "detected_at": ch.detected_at,
            "change_classification": ch.change_classification,
            "change_summary": ch.change_summary,
            "confidence_score": ch.confidence_score,
            "previous_excerpt": ch.previous_excerpt or "(No baseline excerpt previously stored)",
            "new_excerpt": ch.new_excerpt or "(Empty text)",
            "supporting_evidence": ch.supporting_evidence or "Direct text comparison",
            "proposed_modifications": proposed,
            "review_status": ch.review_status,
            "reviewed_by": ch.reviewed_by,
            "reviewed_at": ch.reviewed_at,
            "review_notes": ch.review_notes,
            "applied_to_scheme": ch.applied_to_scheme
        }

    @classmethod
    def review_change(
        cls, 
        db: Session, 
        change_id: int, 
        action: str, 
        admin_id: str,
        review_notes: Optional[str] = None,
        field_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mandatory Human Approval Action.
        Allowed actions: 'approve', 'reject', 'request_evidence'.
        
        When approved:
          - Every affected scheme attribute records a SchemeVersionHistory row.
          - Scheme record is updated with audited values.
          - OfficialSource verification status and baseline are refreshed.
        """
        change = db.query(DetectedSchemeChange).filter(DetectedSchemeChange.id == change_id).first()
        if not change:
            raise ValueError(f"Detected change with ID {change_id} not found.")

        scheme = db.query(Scheme).filter(Scheme.id == change.scheme_id).first()
        if not scheme:
            raise ValueError(f"Scheme with ID {change.scheme_id} not found.")

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        action_clean = action.strip().lower()

        if action_clean not in ("approve", "reject", "request_evidence"):
            raise ValueError(f"Invalid review action '{action}'. Must be 'approve', 'reject', or 'request_evidence'.")

        if action_clean == "reject":
            change.review_status = "rejected"
            change.reviewed_by = admin_id
            change.reviewed_at = now_iso
            change.review_notes = review_notes or "Rejected by administrator after gazette verification."
            
            # Reset monitoring status on source
            if scheme.source:
                scheme.source.monitoring_status = "active"

            db.commit()
            return {
                "change_id": change_id,
                "scheme_id": change.scheme_id,
                "action": "rejected",
                "message": "Change rejected. No modifications were made to scheme records."
            }

        if action_clean == "request_evidence":
            change.review_status = "evidence_requested"
            change.reviewed_by = admin_id
            change.reviewed_at = now_iso
            change.review_notes = review_notes or "Further official gazette or government order evidence requested."
            db.commit()
            return {
                "change_id": change_id,
                "scheme_id": change.scheme_id,
                "action": "evidence_requested",
                "message": "Status updated to evidence requested. Scheme data remains unmodified."
            }

        # -------------------------------------------------------------
        # Action == 'approve'
        # -------------------------------------------------------------
        # Determine fields to modify
        mods_to_apply = {}
        if field_overrides:
            mods_to_apply = field_overrides
        elif change.proposed_modifications:
            try:
                mods_to_apply = json.loads(change.proposed_modifications)
            except Exception:
                mods_to_apply = {}

        recorded_versions = []

        # Audit and update each modified attribute
        for field_name, new_val in mods_to_apply.items():
            if hasattr(scheme, field_name):
                prev_val = getattr(scheme, field_name)
                # Save version history
                ver = SchemeVersionHistory(
                    scheme_id=scheme.id,
                    change_id=change.id,
                    field_name=field_name,
                    previous_value=str(prev_val) if prev_val is not None else None,
                    new_value=str(new_val) if new_val is not None else None,
                    admin_id=admin_id,
                    approval_timestamp=now_iso,
                    evidence_source=change.source_url,
                    reason_for_modification=change.change_summary
                )
                db.add(ver)
                recorded_versions.append(field_name)

                # Apply update
                setattr(scheme, field_name, new_val)

        # Update OfficialSource metadata
        if scheme.source:
            source = scheme.source
            source.verified_date = datetime.date.today().isoformat()
            source.verification_status = "Verified"
            source.monitoring_status = "active"
            source.last_known_excerpt = change.new_excerpt

        change.review_status = "approved"
        change.applied_to_scheme = True
        change.reviewed_by = admin_id
        change.reviewed_at = now_iso
        change.review_notes = review_notes or "Approved by authorized administrator with supporting official evidence."

        db.commit()

        return {
            "change_id": change_id,
            "scheme_id": scheme.id,
            "action": "approved",
            "modified_fields": recorded_versions,
            "message": f"Successfully applied {len(recorded_versions)} audited modification(s) to scheme '{scheme.id}'. Version history recorded."
        }

    @classmethod
    def get_version_history(cls, db: Session, scheme_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves complete audit trail of approved versions for a scheme.
        """
        versions = db.query(SchemeVersionHistory).filter(
            SchemeVersionHistory.scheme_id == scheme_id
        ).order_by(desc(SchemeVersionHistory.approval_timestamp)).all()

        results = []
        for v in versions:
            results.append({
                "id": v.id,
                "scheme_id": v.scheme_id,
                "change_id": v.change_id,
                "field_name": v.field_name,
                "previous_value": v.previous_value,
                "new_value": v.new_value,
                "admin_id": v.admin_id,
                "approval_timestamp": v.approval_timestamp,
                "evidence_source": v.evidence_source,
                "reason_for_modification": v.reason_for_modification,
                "is_rolled_back": v.is_rolled_back,
                "rolled_back_at": v.rolled_back_at,
                "rolled_back_by": v.rolled_back_by
            })
        return results

    @classmethod
    def rollback_version(cls, db: Session, version_id: int, admin_id: str) -> Dict[str, Any]:
        """
        Rollback mechanism for erroneous administrative updates.
        Reverts the modified field on the Scheme record back to its previous_value.
        """
        version = db.query(SchemeVersionHistory).filter(SchemeVersionHistory.id == version_id).first()
        if not version:
            raise ValueError(f"Version history record with ID {version_id} not found.")

        if version.is_rolled_back:
            return {
                "version_id": version_id,
                "scheme_id": version.scheme_id,
                "status": "already_rolled_back",
                "message": f"Version {version_id} was already rolled back on {version.rolled_back_at}."
            }

        scheme = db.query(Scheme).filter(Scheme.id == version.scheme_id).first()
        if not scheme:
            raise ValueError(f"Scheme with ID {version.scheme_id} not found.")

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        field_name = version.field_name
        prev_val = version.previous_value

        # Revert value on Scheme record
        if hasattr(scheme, field_name):
            # Parse type if boolean
            if prev_val in ("True", "False"):
                setattr(scheme, field_name, prev_val == "True")
            else:
                setattr(scheme, field_name, prev_val)

        # Mark this version entry as rolled back
        version.is_rolled_back = True
        version.rolled_back_at = now_iso
        version.rolled_back_by = admin_id

        # Create a new version record documenting the rollback
        rollback_log = SchemeVersionHistory(
            scheme_id=scheme.id,
            change_id=version.change_id,
            field_name=field_name,
            previous_value=version.new_value,
            new_value=version.previous_value,
            admin_id=admin_id,
            approval_timestamp=now_iso,
            evidence_source=version.evidence_source,
            reason_for_modification=f"Administrative rollback of change #{version.change_id or version_id}"
        )
        db.add(rollback_log)

        db.commit()

        return {
            "version_id": version_id,
            "scheme_id": scheme.id,
            "status": "rolled_back",
            "field_name": field_name,
            "restored_value": prev_val,
            "rolled_back_by": admin_id,
            "message": f"Successfully rolled back field '{field_name}' to previous value: '{prev_val}'."
        }

scheme_update_service = SchemeUpdateService
