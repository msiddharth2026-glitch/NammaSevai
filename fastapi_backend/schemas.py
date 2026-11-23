from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class DocumentItem(BaseModel):
    name: str
    name_ta: Optional[str] = None
    mandatory: bool = True

class SchemeBase(BaseModel):
    name: str
    name_ta: str
    department: str
    department_ta: str
    category: str
    beneficiary_type: Optional[str] = None
    beneficiary_type_ta: Optional[str] = None
    benefit_summary: str
    benefit_summary_ta: str
    benefit_amount: str
    description: Optional[str] = None
    description_ta: Optional[str] = None
    eligibility_criteria: List[str] = []
    eligibility_criteria_ta: List[str] = []
    required_documents: List[Dict[str, Any]] = []
    application_procedure: Optional[Dict[str, str]] = {}
    official_portal: str
    official_source: Optional[str] = "Tamil Nadu Government Portal"
    source_verification: Optional[str] = "verified"
    important_dates: Optional[str] = None
    helpline: Optional[str] = None
    keywords: List[str] = []

class SchemeCreate(SchemeBase):
    id: Optional[str] = None

class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    name_ta: Optional[str] = None
    department: Optional[str] = None
    department_ta: Optional[str] = None
    category: Optional[str] = None
    benefit_summary: Optional[str] = None
    benefit_summary_ta: Optional[str] = None
    benefit_amount: Optional[str] = None
    description: Optional[str] = None
    description_ta: Optional[str] = None
    eligibility_criteria: Optional[List[str]] = None
    required_documents: Optional[List[Dict[str, Any]]] = None
    official_portal: Optional[str] = None
    source_verification: Optional[str] = None

class SchemeResponse(SchemeBase):
    id: str
    verified_date: Optional[str] = None

    class Config:
        from_attributes = True

class CitizenQueryRequest(BaseModel):
    query: str
    lang: Optional[str] = "ta"
    preferred_category: Optional[str] = None

class MatchedSchemeItem(BaseModel):
    scheme: SchemeResponse
    match_percent: int
    status: str
    reason: str

class CitizenQueryResponse(BaseModel):
    query: str
    response_message: str
    matches: List[MatchedSchemeItem]
    detected_intent: Dict[str, Any]
