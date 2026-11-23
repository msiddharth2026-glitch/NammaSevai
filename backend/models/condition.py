from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class EligibilityCondition(Base):
    __tablename__ = "eligibility_conditions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Structured condition definition
    field_name = Column(String(64), nullable=False)  # age, gender, income, education, school_type, occupation, land_acres, community, disability
    operator = Column(String(16), default="eq")      # eq, lte, gte, in, contains, is_true
    expected_value = Column(String(255), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    
    # Human-readable criteria descriptions
    description_en = Column(Text, nullable=False)
    description_ta = Column(Text, nullable=False)
    
    # Follow-up questions when this information is missing
    prompt_question_en = Column(Text, nullable=True)
    prompt_question_ta = Column(Text, nullable=True)

    scheme = relationship("Scheme", back_populates="conditions")
