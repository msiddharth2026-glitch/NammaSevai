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
    state: Optional[str] = None  # User's State or UT (None if unstated; Central schemes match all)
    district: Optional[str] = None
    education_level: Optional[str] = None  # school_10th, school_12th, college_ug, diploma, iti, graduate
    school_type: Optional[str] = None      # government, private, aided
    landholding_acres: Optional[float] = None
    
    # Extended profile attributes for comprehensive national matching
    marital_status: Optional[str] = None          # married, unmarried, widow, destitute
    ration_card_type: Optional[str] = None        # bpl, phh, aay, nphh, yellow, orange
    residence_type: Optional[str] = None          # rural, urban, pucca, owned, rented
    is_student: Optional[bool] = None
    is_farmer: Optional[bool] = None
    employment_status: Optional[str] = None       # employed, unemployed, self_employed, unorganized
    
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
    question_hi: Optional[str] = None
    question_ml: Optional[str] = None

class AnalyzeResponse(BaseModel):
    original_text: str
    language: str
    extracted_profile: ExtractedUserProfile
    identified_categories: List[str]
    missing_critical_info: List[MissingInformationItem]
    follow_up_questions_en: List[str]
    follow_up_questions_ta: List[str]
    follow_up_questions_hi: Optional[List[str]] = []
    follow_up_questions_ml: Optional[List[str]] = []
    active_provider: Optional[str] = None
    fallback_chain: Optional[List[Dict[str, str]]] = []

class PotentialSchemeMatch(BaseModel):
    scheme_id: str
    scheme_name_en: str
    scheme_name_ta: str
    scheme_name_hi: Optional[str] = None
    scheme_name_ml: Optional[str] = None
    department_en: str
    department_ta: str
    department_hi: Optional[str] = None
    department_ml: Optional[str] = None
    category: str
    coverage_type: Optional[str] = "State Government (Tamil Nadu)"
    application_url: Optional[str] = None
    benefit_amount: str
    benefit_summary_en: str
    benefit_summary_ta: str
    benefit_summary_hi: Optional[str] = None
    benefit_summary_ml: Optional[str] = None
    
    # Matching breakdown
    match_status: str  # high_potential, potential_match, conditional, not_eligible
    match_confidence: float  # 0 to 100 percentage
    recommendation_category: Optional[str] = "potentially_eligible"  # eligibility_confirmed, potentially_eligible, more_info_required, not_eligible, administrative_review
    eligibility_explanation_en: str
    eligibility_explanation_ta: str
    eligibility_explanation_hi: Optional[str] = None
    eligibility_explanation_ml: Optional[str] = None
    fulfilled_conditions: List[str]
    unverified_conditions: List[str]
    unfulfilled_conditions: Optional[List[str]] = []
    missing_information_fields: Optional[List[str]] = []
    official_disclaimer: Optional[str] = (
        "Official Disclaimer: Matching indicates potential eligibility based on verified rules. "
        "It does not constitute government approval. Final eligibility and benefit disbursement "
        "are subject to verification of original documents by the implementing department."
    )
    
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
    follow_up_questions_hi: Optional[List[str]] = []
    follow_up_questions_ml: Optional[List[str]] = []
    compassionate_response: Optional[str] = None
    active_provider: Optional[str] = None
    fallback_chain: Optional[List[Dict[str, str]]] = []
    disclaimer: str = (
        "Notice: Potential matching does not constitute confirmed eligibility. "
        "Citizens must verify all conditions with the respective department or official portal."
    )
    disclaimer_ta: str = (
        "குறிப்பு: இங்கு காட்டப்படும் முடிவுகள் சாத்தியமான பரிந்துரைகளே தவிர, அதிகாரப்பூர்வ தகுதி உறுதிப்படுத்தல் அல்ல. "
        "விண்ணப்பிக்கும் முன் அரசு தளத்தில் அல்லது இ-சேவை மையத்தில் விதிகளை சரிபார்க்கவும்."
    )
    disclaimer_hi: Optional[str] = (
        "सूचना: संभावित मिलान आधिकारिक पात्रता की गारंटी नहीं है। "
        "अंतिम पात्रता संबंधित सरकारी विभाग या आधिकारिक पोर्टल द्वारा निर्धारित की जाएगी।"
    )
    disclaimer_ml: Optional[str] = (
        "ശ്രദ്ധിക്കുക: സാധ്യതയുള്ള പൊരുത്തം സ്ഥിരീകരിച്ച യോഗ്യതയല്ല. "
        "അന്തിമ യോഗ്യത ഔദ്യോഗിക സർക്കാർ പോർട്ടൽ വഴി സ്ഥിരീകരിക്കേണ്ടതാണ്."
    )
