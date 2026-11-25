import re
import time
import json
import difflib
import hashlib
import logging
import datetime
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any, Tuple
from bs4 import BeautifulSoup
import requests
from sqlalchemy.orm import Session

from ..models.source import OfficialSource, DetectedSchemeChange
from ..models.scheme import Scheme
from ..services.portal_health_monitor import create_resilient_session, REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger("nammasevai.content_detector")

# 13 Standard Policy Change Classifications (Task 3)
POLICY_CHANGE_CLASSIFICATIONS = [
    "eligibility_criteria_changed",
    "income_limit_changed",
    "age_limit_changed",
    "benefit_amount_changed",
    "required_documents_changed",
    "application_deadline_changed",
    "application_process_changed",
    "scheme_renamed",
    "scheme_merged_or_replaced",
    "official_url_changed",
    "scheme_discontinued_or_suspended",
    "general_informational_update",
    "uncertain_change_requiring_human_investigation"
]

class ContentChangeDetectorService:
    """
    Automated Government Scheme Content Change & Policy Modification Detector.
    
    Guarantees:
      - Polite, rate-limited retrieval from official government portals.
      - Rigorous HTML normalization filtering dynamic noise, timestamps, and scripts.
      - SHA-256 fingerprint comparison against verified baselines.
      - Accurate policy classification into 13 statutory change types.
      - Mandatory Human Approval Workflow: Zero automatic mutation of active eligibility rules.
    """

    @classmethod
    def normalize_html_content(cls, html_content: str) -> Tuple[str, str]:
        """
        Normalizes raw HTML content by removing scripts, styling, navigation,
        footers, timestamps, session parameters, and dynamic widgets.
        Returns:
            (normalized_text, content_hash)
        """
        if not html_content or not html_content.strip():
            return "", hashlib.sha256(b"").hexdigest()

        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            # Fallback to simple regex if parser fails
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text, hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

        # 1. Remove non-content structural elements
        for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside", "iframe", "svg"]):
            tag.decompose()

        # 2. Extract visible body text
        body = soup.find("body") or soup
        text = body.get_text(separator=" ", strip=True)

        # 3. Strip dynamic noisy patterns: timestamps, visitor counters, session IDs
        noise_patterns = [
            r'Page (?:last )?updated on:?\s*\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)?',
            r'Last (?:modified|reviewed):?\s*\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}',
            r'Generated at:?\s*\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}',
            r'Current time:?\s*\d{1,2}:\d{2}(?::\d{2})?',
            r'(?:Total\s+)?Visitors?(?:\s+Count)?:?\s*[\d,]+',
            r'Session ID:?\s*[A-Za-z0-9_-]+',
            r'csrf[-_]token\s*=\s*[A-Za-z0-9_-]+',
            r'Copyright\s*©?\s*\d{4}',
            r'All rights reserved\.?'
        ]
        for pattern in noise_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)

        # 4. Collapse whitespace
        normalized = re.sub(r'\s+', ' ', text).strip()
        fingerprint = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        
        return normalized, fingerprint

    @classmethod
    def classify_content_change(
        cls, 
        scheme: Scheme, 
        old_excerpt: Optional[str], 
        new_excerpt: str, 
        diff_text: str,
        redirect_url: Optional[str] = None
    ) -> Tuple[str, str, float, Dict[str, Any]]:
        """
        Classifies detected differences into one of 13 policy change categories.
        Returns:
            (classification, summary, confidence_score, proposed_modifications)
        """
        diff_lower = (diff_text + " " + new_excerpt).lower()
        
        # 1. Official URL or Domain Change
        if redirect_url and scheme.source and redirect_url != scheme.source.portal_url:
            return (
                "official_url_changed",
                f"Official government portal redirected or migrated to new destination: {redirect_url}",
                0.95,
                {"portal_url": redirect_url}
            )

        # 2. Scheme Discontinued or Suspended
        discontinued_signals = ["discontinued", "scheme suspended", "withdrawn by government", "no longer active", "திட்டம் நிறுத்தப்பட்டது", "योजना बंद"]
        if any(w in diff_lower for w in discontinued_signals):
            return (
                "scheme_discontinued_or_suspended",
                "Official portal indicates scheme has been discontinued, suspended, or withdrawn by the department.",
                0.90,
                {"scheme_status": "Discontinued", "is_active": False}
            )

        # 3. Scheme Merged or Replaced
        merged_signals = ["merged into", "subsumed under", "replaced by", "merged with", "ஒன்றிணைக்கப்பட்டது"]
        if any(w in diff_lower for w in merged_signals):
            return (
                "scheme_merged_or_replaced",
                "Scheme reported as merged or subsumed into another national/state government program.",
                0.88,
                {"scheme_status": "Under Review"}
            )

        # 4. Income Limit Changed
        income_signals = ["income limit", "income ceiling", "annual income", "family income", "வருமான வரம்பு", "आय सीमा"]
        if any(w in diff_lower for w in income_signals) and re.search(r'(?:₹|rs\.?|inr)\s*[\d,]+', diff_lower):
            # Extract detected amount
            m = re.search(r'(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)', diff_lower)
            detected_amt = m.group(1).replace(",", "") if m else "Updated"
            return (
                "income_limit_changed",
                f"Statutory annual family income ceiling change detected in portal text (Detected figure: ₹{detected_amt}).",
                0.85,
                {"notes": f"Potential income limit change detected on {datetime.date.today().isoformat()}: ₹{detected_amt}"}
            )

        # 5. Age Limit Changed
        age_signals = ["age limit", "minimum age", "maximum age", "வயது வரம்பு", "आयु सीमा", "years of age"]
        if any(w in diff_lower for w in age_signals) and re.search(r'\b\d{1,2}\s*(?:years|yrs|வயது|साल)\b', diff_lower):
            return (
                "age_limit_changed",
                "Statutory age qualification criteria or age boundaries modified in official scheme text.",
                0.85,
                {"notes": "Age criteria boundary revision detected in official guidelines"}
            )

        # 6. Benefit Amount Changed
        benefit_signals = ["benefit amount", "financial assistance", "subsidy", "stipend", "scholarship amount", "மாதம் ₹", "மாத உதவித்தொகை", "वित्तीय सहायता"]
        if any(w in diff_lower for w in benefit_signals) and re.search(r'(?:₹|rs\.?)\s*[\d,]+', diff_lower):
            m = re.search(r'(?:₹|rs\.?)\s*([\d,]+)', diff_lower)
            detected_benefit = f"₹{m.group(1)}" if m else "Revised Benefit"
            return (
                "benefit_amount_changed",
                f"Scheme financial assistance or stipend benefit revised in announcement (Detected: {detected_benefit}).",
                0.88,
                {"benefit_amount": detected_benefit}
            )

        # 7. Application Deadline Changed
        deadline_signals = ["last date", "deadline", "application period", "extended up to", "கடைசி தேதி", "अंतिम तिथि"]
        if any(w in diff_lower for w in deadline_signals):
            return (
                "application_deadline_changed",
                "Application submission deadline or timeline extension announced on official portal.",
                0.85,
                {}
            )

        # 8. Required Documents Changed
        doc_signals = ["documents required", "mandatory documents", "aadhaar", "ration card", "patta", "certificate", "தேவையான ஆவணங்கள்", "आवश्यक दस्तावेज"]
        if any(w in diff_lower for w in doc_signals):
            return (
                "required_documents_changed",
                "Verification document checklist updated or new verification requirement added.",
                0.80,
                {}
            )

        # 9. Application Process / Portal Procedure Changed
        process_signals = ["how to apply", "application procedure", "e-sevai", "csc", "apply online", "விண்ணப்பிக்கும் முறை", "आवेदन प्रक्रिया"]
        if any(w in diff_lower for w in process_signals):
            return (
                "application_process_changed",
                "Application steps, submission workflow, or portal onboarding procedure updated.",
                0.80,
                {}
            )

        # 10. Scheme Renamed
        rename_signals = ["renamed as", "formerly known as", "பெயர் மாற்றம்", "नाम परिवर्तित"]
        if any(w in diff_lower for w in rename_signals):
            return (
                "scheme_renamed",
                "Official scheme nomenclature or department title updated.",
                0.85,
                {}
            )

        # 11. Eligibility Criteria Changed (General)
        elig_signals = ["eligibility criteria", "who can apply", "beneficiary criteria", "தகுதி வரம்பு", "पात्रता"]
        if any(w in diff_lower for w in elig_signals):
            return (
                "eligibility_criteria_changed",
                "Statutory beneficiary qualifications or eligibility rules updated in official notification.",
                0.82,
                {}
            )

        # 12. General Informational Update
        if len(diff_text.strip()) > 30:
            return (
                "general_informational_update",
                "General portal content, helpline notice, or descriptive information updated without immediate statutory policy alterations.",
                0.75,
                {}
            )

        # 13. Uncertain Change Requiring Human Investigation
        return (
            "uncertain_change_requiring_human_investigation",
            "Ambiguous content difference detected. Requires administrator review and gazette verification.",
            0.60,
            {}
        )

    @classmethod
    def check_scheme_content(
        cls, 
        db: Session, 
        scheme_id: str, 
        session: Optional[requests.Session] = None,
        mock_html: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inspects the official source of a single scheme for content modifications.
        Guarantees:
          - HTML normalization ignoring dynamic noise.
          - SHA-256 fingerprint baseline check.
          - Creation of DetectedSchemeChange with review_status="pending".
          - Zero automatic mutation of active scheme rules.
        """
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        if not scheme or not scheme.source:
            return {"scheme_id": scheme_id, "status": "error", "message": "Scheme or official source record missing"}

        source = scheme.source
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        portal_url = source.portal_url

        raw_html = ""
        redirect_url = None

        if mock_html is not None:
            raw_html = mock_html
        else:
            sess = session or create_resilient_session()
            try:
                resp = sess.get(portal_url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True, verify=False)
                if resp.status_code >= 400 and resp.status_code != 403:
                    source.last_content_check = now_iso
                    source.http_status = resp.status_code
                    source.monitoring_status = "unavailable"
                    db.commit()
                    return {
                        "scheme_id": scheme_id,
                        "status": "unavailable",
                        "change_detected": False,
                        "http_status": resp.status_code,
                        "message": f"Portal returned HTTP {resp.status_code}"
                    }
                raw_html = resp.text
                if resp.history:
                    redirect_url = str(resp.url)
            except Exception as e:
                source.last_content_check = now_iso
                source.monitoring_status = "unavailable"
                db.commit()
                return {
                    "scheme_id": scheme_id,
                    "status": "error",
                    "change_detected": False,
                    "message": f"Connection failed: {str(e)}"
                }

        # Normalize and compute fingerprint
        normalized_text, new_hash = cls.normalize_html_content(raw_html)
        current_length = len(normalized_text)
        new_excerpt = normalized_text[:600]

        source.last_content_check = now_iso
        source.content_length = current_length

        # Case 1: Initial Baseline Registration (First content check)
        if not source.content_fingerprint:
            source.content_fingerprint = new_hash
            source.last_known_excerpt = new_excerpt
            db.commit()
            return {
                "scheme_id": scheme_id,
                "status": "baseline_established",
                "change_detected": False,
                "content_fingerprint": new_hash,
                "content_length": current_length,
                "message": "Initial content baseline successfully registered."
            }

        # Case 2: Identical Fingerprint (No change)
        if source.content_fingerprint == new_hash:
            db.commit()
            return {
                "scheme_id": scheme_id,
                "status": "unchanged",
                "change_detected": False,
                "content_fingerprint": new_hash,
                "content_length": current_length,
                "message": "Content verified unchanged against baseline."
            }

        # Case 3: Meaningful Content Change Detected
        old_excerpt = source.last_known_excerpt or ""
        
        # Generate readable diff
        diff_lines = list(difflib.unified_diff(
            old_excerpt.splitlines(keepends=True),
            new_excerpt.splitlines(keepends=True),
            fromfile="Previous Baseline",
            tofile="Detected Content",
            n=2
        ))
        diff_text = "".join(diff_lines) if diff_lines else f"Content length changed: {len(old_excerpt)} -> {len(new_excerpt)} chars"

        # Classify policy change
        classification, summary, confidence, proposed = cls.classify_content_change(
            scheme=scheme,
            old_excerpt=old_excerpt,
            new_excerpt=new_excerpt,
            diff_text=diff_text,
            redirect_url=redirect_url
        )

        # Check for duplicate pending change to prevent spamming admin review queue
        existing_pending = db.query(DetectedSchemeChange).filter(
            DetectedSchemeChange.scheme_id == scheme_id,
            DetectedSchemeChange.review_status == "pending",
            DetectedSchemeChange.change_classification == classification
        ).first()

        change_record = None
        if existing_pending:
            # Update existing pending record with latest evidence
            existing_pending.detected_at = now_iso
            existing_pending.new_excerpt = new_excerpt
            existing_pending.change_summary = summary
            existing_pending.supporting_evidence = diff_text
            existing_pending.proposed_modifications = json.dumps(proposed)
            change_record = existing_pending
        else:
            # Create new pending review entry
            change_record = DetectedSchemeChange(
                scheme_id=scheme_id,
                source_url=portal_url,
                detected_at=now_iso,
                change_classification=classification,
                previous_excerpt=old_excerpt,
                new_excerpt=new_excerpt,
                change_summary=summary,
                confidence_score=confidence,
                supporting_evidence=diff_text,
                proposed_modifications=json.dumps(proposed),
                review_status="pending",
                applied_to_scheme=False
            )
            db.add(change_record)

        # Update source metadata (WITHOUT modifying active statutory scheme rules!)
        source.last_detected_modification = now_iso
        source.monitoring_status = "under_review"

        db.commit()

        return {
            "scheme_id": scheme_id,
            "status": "change_detected",
            "change_detected": True,
            "change_id": change_record.id,
            "classification": classification,
            "confidence": confidence,
            "summary": summary,
            "proposed_modifications": proposed,
            "review_status": "pending",
            "applied_to_scheme": False,
            "notice": "Mandatory Human Approval Required: Statutory rules remain unmodified until authorized administrator approves."
        }

    @classmethod
    def run_content_audit(
        cls, 
        db: Session, 
        scheme_ids: Optional[List[str]] = None,
        rate_limit_delay_seconds: float = 0.5
    ) -> Dict[str, Any]:
        """
        Executes rate-limited content monitoring audit across registered official sources.
        """
        query = db.query(OfficialSource)
        if scheme_ids:
            query = query.filter(OfficialSource.scheme_id.in_(scheme_ids))
        
        sources = query.all()
        session = create_resilient_session()

        total_checked = 0
        baselines_registered = 0
        unchanged_count = 0
        changes_detected = 0
        errors_count = 0
        results = []

        for src in sources:
            time.sleep(rate_limit_delay_seconds)  # Politeness rate limiting
            res = cls.check_scheme_content(db=db, scheme_id=src.scheme_id, session=session)
            results.append(res)
            total_checked += 1
            
            st = res.get("status")
            if st == "baseline_established":
                baselines_registered += 1
            elif st == "unchanged":
                unchanged_count += 1
            elif st == "change_detected":
                changes_detected += 1
            else:
                errors_count += 1

        return {
            "audit_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_sources_registered": db.query(OfficialSource).count(),
            "sources_audited": total_checked,
            "baselines_registered": baselines_registered,
            "unchanged_sources": unchanged_count,
            "changes_detected": changes_detected,
            "unavailable_or_errors": errors_count,
            "pending_admin_reviews": db.query(DetectedSchemeChange).filter(DetectedSchemeChange.review_status == "pending").count(),
            "results": results
        }

content_change_detector = ContentChangeDetectorService
