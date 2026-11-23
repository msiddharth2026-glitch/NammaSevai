from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .scheme import SchemeDetailResponse
from .document import RequiredDocumentResponse
from .step import ApplicationStepResponse

class ExtractedUserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None  # female, male, other
    occupation: Optional[str] = None  # student, farmer, tailor, self_employed, unemployed, housewife, senior
    annual_income: Optional[float] = None
    state: str = "Tamil Nadu"
    district: Optional[str] = None
    education_level: Optional[str] = None  # school_10th, school_12th, college_ug, diploma, iti, graduate
    school_type: Optional[str] = None      # government, private, aided
    landholding_acres: Optional[float] = None
    
    # Sensitive attributes: collected ONLY when voluntarily provided by citizen and relevant
    community_category: Optional[str] = None  # SC, ST, BC, MBC, General
    disability_status: Optional[bool] = None
    is_pregnant_or_lactating: Optional[bool] = None
    is_widow_or_destitute: Optional[bool] = None
    has_tailoring_training: Optional[bool] = None

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Citizen's voice query or typed situation")
    lang: Optional[str] = "ta"
    session_id: Optional[str] = None

class MissingInformationItem(BaseModel):
    field_name: str
    relevance_to_scheme: str
    question_en: str
    question_ta: str

class AnalyzeResponse(BaseModel):
    original_text: str
    language: str
    extracted_profile: ExtractedUserProfile
    identified_categories: List[str]
    missing_critical_info: List[MissingInformationItem]
    follow_up_questions_en: List[str]
    follow_up_questions_ta: List[str]

class PotentialSchemeMatch(BaseModel):
    scheme_id: str
    scheme_name_en: str
    scheme_name_ta: str
    department_en: str
    department_ta: str
    category: str
    benefit_amount: str
    benefit_summary_en: str
    benefit_summary_ta: str
    
    # Matching breakdown
    match_status: str  # high_potential, potential_match, conditional, not_eligible
    match_confidence: float  # 0 to 100 percentage
    eligibility_explanation_en: str
    eligibility_explanation_ta: str
    fulfilled_conditions: List[str]
    unverified_conditions: List[str]
    
    # Actionable items for citizen
    required_documents: List[RequiredDocumentResponse]
    application_steps: List[ApplicationStepResponse]
    official_portal_url: str
    official_source_name: str
    verified_date: str

class MatchRequest(BaseModel):
    query: Optional[str] = None
    profile: Optional[ExtractedUserProfile] = None
    lang: Optional[str] = "ta"
    category: Optional[str] = None

class MatchResponse(BaseModel):
    total_potential_matches: int
    matches: List[PotentialSchemeMatch]
    extracted_profile: ExtractedUserProfile
    follow_up_questions_en: List[str]
    follow_up_questions_ta: List[str]
    disclaimer: str = (
        "Notice: Potential matching does not constitute confirmed eligibility. "
        "Citizens must verify all conditions with the respective department or official portal."
    )
    disclaimer_ta: str = (
        "குறிப்பு: இங்கு காட்டப்படும் முடிவுகள் சாத்தியமான பரிந்துரைகளே தவிர, அதிகாரப்பூர்வ தகுதி உறுதிப்படுத்தல் அல்ல. "
        "விண்ணப்பிக்கும் முன் அரசு தளத்தில் அல்லது இ-சேவை மையத்தில் விதிகளை சரிபார்க்கவும்."
    )
