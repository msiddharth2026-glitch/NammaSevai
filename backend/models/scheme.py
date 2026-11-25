from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_ta = Column(String(255), nullable=False)
    name_hi = Column(String(255), nullable=True)
    name_ml = Column(String(255), nullable=True)

    department = Column(String(255), nullable=False)
    department_ta = Column(String(255), nullable=False)
    department_hi = Column(String(255), nullable=True)
    department_ml = Column(String(255), nullable=True)

    category = Column(String(64), index=True, nullable=False)
    
    # National Geographical Classification: "Central", "State", "Union Territory"
    level = Column(String(32), index=True, nullable=False, default="State")
    # Specific State or Union Territory name (e.g. "Tamil Nadu", "Maharashtra", "Delhi") or "All India" for Central
    state = Column(String(64), index=True, nullable=True)

    beneficiary_type = Column(String(255), nullable=True)
    beneficiary_type_ta = Column(String(255), nullable=True)
    target_beneficiaries = Column(String(255), nullable=True)
    target_beneficiaries_ta = Column(String(255), nullable=True)

    benefit_summary = Column(Text, nullable=False)
    benefit_summary_ta = Column(Text, nullable=False)
    benefit_summary_hi = Column(Text, nullable=True)
    benefit_summary_ml = Column(Text, nullable=True)
    benefit_amount = Column(String(128), nullable=False)
    
    description = Column(Text, nullable=False)
    description_ta = Column(Text, nullable=False)
    description_hi = Column(Text, nullable=True)
    description_ml = Column(Text, nullable=True)

    # Keywords / search tags for multi-lingual and alternate name discovery
    keywords = Column(Text, nullable=True)

    # Status: "Active", "Inactive", "Under Review", "Discontinued"
    scheme_status = Column(String(32), index=True, nullable=False, default="Active")
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    conditions = relationship(
        "EligibilityCondition", 
        back_populates="scheme", 
        cascade="all, delete-orphan", 
        lazy="selectin"
    )
    documents = relationship(
        "RequiredDocument", 
        back_populates="scheme", 
        cascade="all, delete-orphan", 
        lazy="selectin"
    )
    steps = relationship(
        "ApplicationStep", 
        back_populates="scheme", 
        cascade="all, delete-orphan", 
        order_by="ApplicationStep.step_number",
        lazy="selectin"
    )
    source = relationship(
        "OfficialSource", 
        back_populates="scheme", 
        uselist=False, 
        cascade="all, delete-orphan", 
        lazy="joined"
    )
    detected_changes = relationship(
        "DetectedSchemeChange", 
        back_populates="scheme", 
        cascade="all, delete-orphan"
    )
    version_history = relationship(
        "SchemeVersionHistory", 
        back_populates="scheme", 
        cascade="all, delete-orphan"
    )
