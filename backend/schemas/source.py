from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class OfficialSourceBase(BaseModel):
    source_name: str
    portal_url: str
    application_url: Optional[str] = None
    verified_date: str
    verification_status: str = "Verified"  # Verified, Partially Verified, Needs Review, Inactive or Discontinued, Source Unavailable
    helpline_number: Optional[str] = None
    government_order_ref: Optional[str] = None
    notes: Optional[str] = None
    http_status: Optional[int] = None
    last_health_check: Optional[str] = None
    health_response_time_ms: Optional[int] = None
    redirect_url: Optional[str] = None
    domain_migration_detected: Optional[bool] = False
    health_error: Optional[str] = None
    
    # Automated Content Monitoring Attributes
    source_category: Optional[str] = "Official Portal"
    ministry_department: Optional[str] = None
    assigned_administrator: Optional[str] = "admin@nammasevai.gov.in"
    last_content_check: Optional[str] = None
    last_detected_modification: Optional[str] = None
    content_fingerprint: Optional[str] = None
    content_length: Optional[int] = None
    last_known_excerpt: Optional[str] = None
    monitoring_status: Optional[str] = "active"

class OfficialSourceCreate(OfficialSourceBase):
    pass

class OfficialSourceResponse(OfficialSourceBase):
    id: int
    scheme_id: str

    model_config = ConfigDict(from_attributes=True)

class PortalHealthCheckResult(BaseModel):
    scheme_id: str
    scheme_name: str
    portal_url: str
    is_available: bool
    http_status: Optional[int] = None
    response_time_ms: Optional[int] = None
    redirect_url: Optional[str] = None
    domain_migration_detected: bool = False
    error_message: Optional[str] = None
    checked_at: str
    content_verification_status: str

class PortalHealthSummary(BaseModel):
    total_checked: int
    available_count: int
    unavailable_count: int
    redirects_detected: int
    domain_migrations_detected: int
    last_check_time: Optional[str] = None
    broken_portals: List[PortalHealthCheckResult] = []
