from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class RequiredDocument(Base):
    __tablename__ = "required_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name_en = Column(String(255), nullable=False)
    name_ta = Column(String(255), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    
    issuing_authority_en = Column(String(255), nullable=True)
    issuing_authority_ta = Column(String(255), nullable=True)
    description_en = Column(Text, nullable=True)
    description_ta = Column(Text, nullable=True)
    document_code = Column(String(64), nullable=True)  # aadhaar, ration_card, income_cert, etc.

    scheme = relationship("Scheme", back_populates="documents")
