from pydantic import BaseModel, ConfigDict
from typing import Optional

class RequiredDocumentBase(BaseModel):
    name_en: str
    name_ta: str
    is_mandatory: bool = True
    issuing_authority_en: Optional[str] = None
    issuing_authority_ta: Optional[str] = None
    description_en: Optional[str] = None
    description_ta: Optional[str] = None
    document_code: Optional[str] = None

class RequiredDocumentCreate(RequiredDocumentBase):
    pass

class RequiredDocumentResponse(RequiredDocumentBase):
    id: int
    scheme_id: str

    model_config = ConfigDict(from_attributes=True)
