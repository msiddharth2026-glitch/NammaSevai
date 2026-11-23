from pydantic import BaseModel, ConfigDict
from typing import Optional

class EligibilityConditionBase(BaseModel):
    field_name: str
    operator: str = "eq"
    expected_value: str
    is_mandatory: bool = True
    description_en: str
    description_ta: str
    prompt_question_en: Optional[str] = None
    prompt_question_ta: Optional[str] = None

class EligibilityConditionCreate(EligibilityConditionBase):
    pass

class EligibilityConditionResponse(EligibilityConditionBase):
    id: int
    scheme_id: str

    model_config = ConfigDict(from_attributes=True)
