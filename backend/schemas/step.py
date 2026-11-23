from pydantic import BaseModel, ConfigDict
from typing import Optional

class ApplicationStepBase(BaseModel):
    step_number: int = 1
    mode: str = "both"  # online, offline, both
    title_en: str
    title_ta: str
    description_en: str
    description_ta: str
    portal_url: Optional[str] = None
    office_name_en: Optional[str] = None
    office_name_ta: Optional[str] = None

class ApplicationStepCreate(ApplicationStepBase):
    pass

class ApplicationStepResponse(ApplicationStepBase):
    id: int
    scheme_id: str

    model_config = ConfigDict(from_attributes=True)
