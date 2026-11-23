from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_ta = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    department_ta = Column(String(255), nullable=False)
    category = Column(String(64), index=True, nullable=False)
    beneficiary_type = Column(String(255))
    beneficiary_type_ta = Column(String(255))
    benefit_summary = Column(Text, nullable=False)
    benefit_summary_ta = Column(Text, nullable=False)
    benefit_amount = Column(String(128))
    description = Column(Text)
    description_ta = Column(Text)
    eligibility_criteria = Column(JSON, default=list)
    eligibility_criteria_ta = Column(JSON, default=list)
    required_documents = Column(JSON, default=list)
    application_procedure = Column(JSON, default=dict)
    official_portal = Column(String(512), nullable=False)
    official_source = Column(String(255))
    source_verification = Column(String(32), default="verified")
    verified_date = Column(String(32))
    important_dates = Column(String(255))
    helpline = Column(String(128))
    keywords = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
