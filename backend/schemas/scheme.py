from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from .condition import EligibilityConditionResponse, EligibilityConditionCreate
from .document import RequiredDocumentResponse, RequiredDocumentCreate
from .step import ApplicationStepResponse, ApplicationStepCreate
from .source import OfficialSourceResponse, OfficialSourceCreate

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
    description: str
    description_ta: str
    is_active: bool = True

class SchemeListItem(SchemeBase):
    id: str
    source_verification_status: Optional[str] = "verified"
    verified_date: Optional[str] = None
    portal_url: Optional[str] = None
    official_portal: Optional[str] = None
    required_documents: List[dict] = []

    model_config = ConfigDict(from_attributes=True)

class SchemeDetailResponse(SchemeBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    conditions: List[EligibilityConditionResponse] = []
    documents: List[RequiredDocumentResponse] = []
    steps: List[ApplicationStepResponse] = []
    source: Optional[OfficialSourceResponse] = None

    model_config = ConfigDict(from_attributes=True)

class SchemeCreate(SchemeBase):
    id: str
    conditions: List[EligibilityConditionCreate] = []
    documents: List[RequiredDocumentCreate] = []
    steps: List[ApplicationStepCreate] = []
    source: Optional[OfficialSourceCreate] = None

class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    name_ta: Optional[str] = None
    department: Optional[str] = None
    department_ta: Optional[str] = None
    category: Optional[str] = None
    beneficiary_type: Optional[str] = None
    beneficiary_type_ta: Optional[str] = None
    benefit_summary: Optional[str] = None
    benefit_summary_ta: Optional[str] = None
    benefit_amount: Optional[str] = None
    description: Optional[str] = None
    description_ta: Optional[str] = None
    is_active: Optional[bool] = None
