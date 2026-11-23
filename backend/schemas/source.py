from pydantic import BaseModel, ConfigDict
from typing import Optional

class OfficialSourceBase(BaseModel):
    source_name: str
    portal_url: str
    verified_date: str
    verification_status: str = "verified"
    helpline_number: Optional[str] = None
    government_order_ref: Optional[str] = None
    notes: Optional[str] = None

class OfficialSourceCreate(OfficialSourceBase):
    pass

class OfficialSourceResponse(OfficialSourceBase):
    id: int
    scheme_id: str

    model_config = ConfigDict(from_attributes=True)
