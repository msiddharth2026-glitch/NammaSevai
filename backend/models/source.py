from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class OfficialSource(Base):
    __tablename__ = "official_sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    source_name = Column(String(255), nullable=False)
    portal_url = Column(String(512), nullable=False)
    application_url = Column(String(512), nullable=True)
    verified_date = Column(String(32), nullable=False)  # YYYY-MM-DD
    verification_status = Column(String(32), default="Verified")  # Verified, Partially Verified, Needs Review, Inactive or Discontinued, Source Unavailable
    source_publication_date = Column(String(32), nullable=True)  # YYYY-MM-DD
    is_official = Column(Boolean, default=True)

    helpline_number = Column(String(128), nullable=True)
    government_order_ref = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Portal Automated Network Health Monitoring
    http_status = Column(Integer, nullable=True)
    last_health_check = Column(String(64), nullable=True)
    health_response_time_ms = Column(Integer, nullable=True)
    redirect_url = Column(String(512), nullable=True)
    domain_migration_detected = Column(Boolean, default=False)
    health_error = Column(Text, nullable=True)

    # Automated Scheme Content Change & Policy Monitoring
    source_category = Column(String(64), default="Official Portal", nullable=True)  # Official Portal, Ministry Website, Gazette, Statutory Scheme Portal
    ministry_department = Column(String(255), nullable=True)
    assigned_administrator = Column(String(128), default="admin@nammasevai.gov.in", nullable=True)
    last_content_check = Column(String(64), nullable=True)  # ISO timestamp
    last_detected_modification = Column(String(64), nullable=True)  # ISO timestamp
    content_fingerprint = Column(String(64), nullable=True)  # SHA-256 hash of normalized content
    content_length = Column(Integer, nullable=True)
    last_known_excerpt = Column(Text, nullable=True)
    monitoring_status = Column(String(32), default="active", nullable=True)  # active, paused, under_review

    scheme = relationship("Scheme", back_populates="source")


class PortalHealthLog(Base):
    __tablename__ = "portal_health_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    portal_url = Column(String(512), nullable=False)
    checked_at = Column(String(64), nullable=False)
    http_status = Column(Integer, nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    redirect_url = Column(String(512), nullable=True)
    domain_migration_detected = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)


class DetectedSchemeChange(Base):
    """
    Records meaningful scheme policy changes detected by the automated monitor.
    Strictly requires authorized human administrator approval before applying
    any modifications to active scheme records or eligibility rules.
    """
    __tablename__ = "detected_scheme_changes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    source_url = Column(String(512), nullable=False)
    detected_at = Column(String(64), nullable=False)  # ISO timestamp

    # Classification of policy change
    # Values: eligibility_criteria_changed, income_limit_changed, age_limit_changed,
    # benefit_amount_changed, required_documents_changed, application_deadline_changed,
    # application_process_changed, scheme_renamed, scheme_merged_or_replaced,
    # official_url_changed, scheme_discontinued_or_suspended, general_informational_update,
    # uncertain_change_requiring_human_investigation
    change_classification = Column(String(64), nullable=False, index=True)
    
    previous_excerpt = Column(Text, nullable=True)
    new_excerpt = Column(Text, nullable=True)
    change_summary = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.85)
    supporting_evidence = Column(Text, nullable=True)
    proposed_modifications = Column(Text, nullable=True)  # JSON dictionary of proposed field changes

    # Human Review Workflow Status
    # Values: "pending", "approved", "rejected", "evidence_requested"
    review_status = Column(String(32), default="pending", index=True, nullable=False)
    reviewed_by = Column(String(128), nullable=True)
    reviewed_at = Column(String(64), nullable=True)
    review_notes = Column(Text, nullable=True)
    applied_to_scheme = Column(Boolean, default=False, nullable=False)

    scheme = relationship("Scheme", back_populates="detected_changes")


class SchemeVersionHistory(Base):
    """
    Chronological audit trail of all approved administrative modifications.
    Allows exact point-in-time inspection and rollback to prior versions.
    """
    __tablename__ = "scheme_version_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    change_id = Column(Integer, ForeignKey("detected_scheme_changes.id", ondelete="SET NULL"), nullable=True)

    field_name = Column(String(64), nullable=False, index=True)  # name, benefit_amount, benefit_summary, description, scheme_status, official_url, conditions, documents, steps
    previous_value = Column(Text, nullable=True)  # String or JSON serialization
    new_value = Column(Text, nullable=True)       # String or JSON serialization
    
    admin_id = Column(String(128), nullable=False)
    approval_timestamp = Column(String(64), nullable=False)  # ISO timestamp
    evidence_source = Column(String(512), nullable=True)     # Official government portal or gazette URL
    reason_for_modification = Column(Text, nullable=False)

    is_rolled_back = Column(Boolean, default=False, nullable=False)
    rolled_back_at = Column(String(64), nullable=True)
    rolled_back_by = Column(String(128), nullable=True)

    scheme = relationship("Scheme", back_populates="version_history")
