import csv
import io
import json
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.scheme import Scheme
from ..models.condition import EligibilityCondition
from ..models.document import RequiredDocument
from ..models.step import ApplicationStep
from ..models.source import OfficialSource
from ..data.geography import (
    INDIAN_STATES, 
    INDIAN_UNION_TERRITORIES, 
    GOVERNMENT_LEVELS, 
    SCHEME_CATEGORIES,
    normalize_jurisdiction
)

logger = logging.getLogger("nammasevai.importer")

def generate_scheme_id(name: str, state: Optional[str] = None) -> str:
    """Generates a clean URL-friendly unique identifier from name and jurisdiction."""
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.strip().lower()).strip('-')
    if state and state.lower() not in ("all india", "central"):
        state_slug = re.sub(r'[^a-zA-Z0-9]+', '-', state.strip().lower()).strip('-')
        return f"{slug}-{state_slug}"[:64]
    return slug[:64]

class SchemeImporterService:
    """
    Scalable National Scheme Ingestion Service.
    Supports structured JSON and CSV imports, validation, duplicate prevention,
    verification tracking, and detailed audit reporting.
    """

    @staticmethod
    def parse_csv_content(csv_text: str) -> List[Dict[str, Any]]:
        """Parses CSV text into a list of record dictionaries."""
        reader = csv.DictReader(io.StringIO(csv_text))
        records = []
        for row in reader:
            clean_row = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}
            records.append(clean_row)
        return records

    @staticmethod
    def validate_and_normalize_record(raw: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Validates required fields, normalizes geographical metadata, and returns clean dictionary.
        Returns: (is_valid, normalized_dict, error_message)
        """
        name = raw.get("name") or raw.get("scheme_name") or raw.get("official_scheme_name")
        if not name or len(name.strip()) < 3:
            return False, None, "Missing or invalid scheme name"

        category = (raw.get("category") or "other").strip().lower()
        if category not in SCHEME_CATEGORIES and not any(k in category for k in SCHEME_CATEGORIES):
            category = "other"

        # Determine level & state
        raw_level = raw.get("level") or raw.get("government_level") or ""
        raw_state = raw.get("state") or raw.get("state_or_ut") or ""

        norm_state, detected_level = normalize_jurisdiction(raw_state)
        
        # Level reconciliation
        level = "State"
        if raw_level.strip().lower() in ("central", "central government", "national"):
            level = "Central"
            norm_state = "All India"
        elif detected_level:
            level = detected_level
        elif raw_level in GOVERNMENT_LEVELS:
            level = raw_level

        if level == "Central" and (not norm_state or norm_state == "Tamil Nadu"):
            norm_state = "All India"
        elif not norm_state:
            norm_state = "Tamil Nadu"

        # Benefit amount & summary
        benefit_summary = raw.get("benefit_summary") or raw.get("benefits") or raw.get("benefit_amount") or "Government welfare support"
        benefit_amount = raw.get("benefit_amount") or "Financial & Service Support"
        description = raw.get("description") or benefit_summary

        department = raw.get("department") or raw.get("ministry") or "Department of Social Welfare"

        # Verification & source portal
        source_name = raw.get("source_name") or raw.get("official_source") or "National Portal of India"
        portal_url = raw.get("portal_url") or raw.get("application_portal") or raw.get("official_portal") or "https://www.myscheme.gov.in"
        verified_date = raw.get("verified_date") or datetime.now().strftime("%Y-%m-%d")
        verification_status = raw.get("verification_status") or "verified"
        if verification_status not in ("verified", "pending_recheck", "outdated"):
            verification_status = "pending_recheck"

        scheme_status = raw.get("scheme_status") or "Active"
        if scheme_status not in ("Active", "Inactive", "Under Review", "Discontinued"):
            scheme_status = "Active"

        # Generate unique ID if absent
        scheme_id = raw.get("id") or raw.get("scheme_id") or generate_scheme_id(name, norm_state)
        scheme_id = re.sub(r'[^a-zA-Z0-9_\-]', '', scheme_id)[:64]

        normalized = {
            "id": scheme_id,
            "name": name.strip(),
            "name_ta": raw.get("name_ta") or name.strip(),
            "name_hi": raw.get("name_hi"),
            "name_ml": raw.get("name_ml"),
            "department": department.strip(),
            "department_ta": raw.get("department_ta") or department.strip(),
            "department_hi": raw.get("department_hi"),
            "department_ml": raw.get("department_ml"),
            "category": category,
            "level": level,
            "state": norm_state,
            "beneficiary_type": raw.get("beneficiary_type") or raw.get("target_beneficiaries") or "All eligible citizens",
            "beneficiary_type_ta": raw.get("beneficiary_type_ta"),
            "target_beneficiaries": raw.get("target_beneficiaries") or raw.get("beneficiary_type"),
            "target_beneficiaries_ta": raw.get("target_beneficiaries_ta"),
            "benefit_summary": benefit_summary.strip(),
            "benefit_summary_ta": raw.get("benefit_summary_ta") or benefit_summary.strip(),
            "benefit_summary_hi": raw.get("benefit_summary_hi"),
            "benefit_summary_ml": raw.get("benefit_summary_ml"),
            "benefit_amount": benefit_amount.strip(),
            "description": description.strip(),
            "description_ta": raw.get("description_ta") or description.strip(),
            "description_hi": raw.get("description_hi"),
            "description_ml": raw.get("description_ml"),
            "keywords": raw.get("keywords") or f"{name}, {department}, {norm_state}, {level}",
            "scheme_status": scheme_status,
            "is_active": raw.get("is_active", True) in (True, "True", "true", "1", 1),
            "source_name": source_name,
            "portal_url": portal_url,
            "verified_date": verified_date,
            "verification_status": verification_status,
            "source_publication_date": raw.get("source_publication_date"),
            "application_url": raw.get("application_url") or raw.get("portal_url"),
            "conditions": raw.get("conditions") or [],
            "documents": raw.get("documents") or [],
            "steps": raw.get("steps") or []
        }
        return True, normalized, ""

    @classmethod
    def import_records(
        cls, 
        db: Session, 
        records: List[Dict[str, Any]], 
        allow_overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Processes and imports a batch of scheme records.
        Ensures duplicate prevention, verification metadata tracking, and atomicity.
        """
        total = len(records)
        imported = 0
        duplicates = 0
        invalid = 0
        verification_req = 0
        failed = 0
        details = []

        for idx, raw in enumerate(records):
            is_valid, norm, err = cls.validate_and_normalize_record(raw)
            if not is_valid:
                invalid += 1
                details.append({
                    "index": idx,
                    "id": raw.get("id", f"record-{idx}"),
                    "status": "invalid",
                    "reason": err
                })
                continue

            scheme_id = norm["id"]

            # Check for existing duplicate by ID
            existing = db.query(Scheme).filter(Scheme.id == scheme_id).first()
            if existing:
                if not allow_overwrite:
                    duplicates += 1
                    details.append({
                        "index": idx,
                        "id": scheme_id,
                        "name": norm["name"],
                        "status": "duplicate",
                        "reason": f"Scheme with ID '{scheme_id}' already exists in database. Skipped to prevent overwriting."
                    })
                    continue
                else:
                    # Update existing
                    for key in ("name", "name_ta", "name_hi", "name_ml", "department", "department_ta",
                                "department_hi", "department_ml", "category", "level", "state",
                                "benefit_summary", "benefit_summary_ta", "benefit_summary_hi",
                                "benefit_summary_ml", "benefit_amount", "description", "description_ta",
                                "description_hi", "description_ml", "keywords", "scheme_status", "is_active",
                                "target_beneficiaries", "target_beneficiaries_ta", "beneficiary_type"):
                        if key in norm and norm[key] is not None:
                            setattr(existing, key, norm[key])
                    
                    if existing.source:
                        existing.source.source_name = norm["source_name"]
                        existing.source.portal_url = norm["portal_url"]
                        existing.source.verified_date = norm["verified_date"]
                        existing.source.verification_status = norm["verification_status"]
                    
                    imported += 1
                    details.append({
                        "index": idx,
                        "id": scheme_id,
                        "name": norm["name"],
                        "status": "updated",
                        "level": norm["level"],
                        "state": norm["state"]
                    })
                    continue

            # Insert new scheme
            try:
                scheme = Scheme(
                    id=scheme_id,
                    name=norm["name"],
                    name_ta=norm["name_ta"],
                    name_hi=norm.get("name_hi"),
                    name_ml=norm.get("name_ml"),
                    department=norm["department"],
                    department_ta=norm["department_ta"],
                    department_hi=norm.get("department_hi"),
                    department_ml=norm.get("department_ml"),
                    category=norm["category"],
                    level=norm["level"],
                    state=norm["state"],
                    beneficiary_type=norm.get("beneficiary_type"),
                    beneficiary_type_ta=norm.get("beneficiary_type_ta"),
                    target_beneficiaries=norm.get("target_beneficiaries"),
                    target_beneficiaries_ta=norm.get("target_beneficiaries_ta"),
                    benefit_summary=norm["benefit_summary"],
                    benefit_summary_ta=norm["benefit_summary_ta"],
                    benefit_summary_hi=norm.get("benefit_summary_hi"),
                    benefit_summary_ml=norm.get("benefit_summary_ml"),
                    benefit_amount=norm["benefit_amount"],
                    description=norm["description"],
                    description_ta=norm["description_ta"],
                    description_hi=norm.get("description_hi"),
                    description_ml=norm.get("description_ml"),
                    keywords=norm.get("keywords"),
                    scheme_status=norm["scheme_status"],
                    is_active=norm["is_active"]
                )
                db.add(scheme)
                db.flush()

                # Add official source record
                source = OfficialSource(
                    scheme_id=scheme.id,
                    source_name=norm["source_name"],
                    portal_url=norm["portal_url"],
                    application_url=norm.get("application_url"),
                    verified_date=norm["verified_date"],
                    verification_status=norm["verification_status"],
                    source_publication_date=norm.get("source_publication_date"),
                    is_official=True
                )
                db.add(source)

                # Optional conditions
                if norm.get("conditions") and isinstance(norm["conditions"], list):
                    for c in norm["conditions"]:
                        exp_val = c.get("expected_value") or c.get("field_value")
                        if isinstance(c, dict) and "field_name" in c and exp_val is not None:
                            db.add(EligibilityCondition(
                                scheme_id=scheme.id,
                                field_name=c["field_name"],
                                operator=c.get("operator", "eq"),
                                expected_value=str(exp_val),
                                is_mandatory=c.get("is_mandatory", True),
                                description_en=c.get("description_en", f"Criteria for {c['field_name']}"),
                                description_ta=c.get("description_ta", f"{c['field_name']} நிபந்தனை"),
                                prompt_question_en=c.get("prompt_question_en"),
                                prompt_question_ta=c.get("prompt_question_ta")
                            ))

                # Optional documents
                if norm.get("documents") and isinstance(norm["documents"], list):
                    for d in norm["documents"]:
                        doc_name_en = d.get("name_en") or d.get("document_name_en")
                        doc_name_ta = d.get("name_ta") or d.get("document_name_ta") or doc_name_en
                        if isinstance(d, dict) and doc_name_en:
                            db.add(RequiredDocument(
                                scheme_id=scheme.id,
                                name_en=doc_name_en,
                                name_ta=doc_name_ta,
                                is_mandatory=d.get("is_mandatory", True),
                                issuing_authority_en=d.get("issuing_authority_en") or d.get("issuing_authority", "Competent Authority"),
                                issuing_authority_ta=d.get("issuing_authority_ta") or d.get("issuing_authority", "அரசுத் துறை"),
                                description_en=d.get("description_en", doc_name_en),
                                description_ta=d.get("description_ta", doc_name_ta)
                            ))

                # Optional application steps
                if norm.get("steps") and isinstance(norm["steps"], list):
                    for s_idx, st in enumerate(norm["steps"]):
                        if isinstance(st, dict) and ("title_en" in st or "description_en" in st):
                            db.add(ApplicationStep(
                                scheme_id=scheme.id,
                                step_number=st.get("step_number", s_idx + 1),
                                mode=st.get("mode", "online"),
                                title_en=st.get("title_en", f"Step {s_idx + 1}"),
                                title_ta=st.get("title_ta", f"படி {s_idx + 1}"),
                                description_en=st.get("description_en", st.get("title_en", "")),
                                description_ta=st.get("description_ta", st.get("title_ta", "")),
                                portal_url=st.get("portal_url", norm["portal_url"])
                            ))

                imported += 1
                if norm["verification_status"] != "verified":
                    verification_req += 1

                details.append({
                    "index": idx,
                    "id": scheme_id,
                    "name": norm["name"],
                    "status": "imported",
                    "level": norm["level"],
                    "state": norm["state"],
                    "verification": norm["verification_status"]
                })
            except Exception as e:
                failed += 1
                logger.error(f"Failed to insert scheme {scheme_id}: {e}")
                details.append({
                    "index": idx,
                    "id": scheme_id,
                    "name": norm.get("name", "Unknown"),
                    "status": "failed",
                    "reason": str(e)
                })

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Transaction commit failed during scheme import: {e}")
            raise

        return {
            "total_processed": total,
            "imported": imported,
            "duplicates": duplicates,
            "invalid": invalid,
            "verification_required": verification_req,
            "failed": failed,
            "details": details
        }
