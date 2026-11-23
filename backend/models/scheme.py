from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_ta = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    department_ta = Column(String(255), nullable=False)
    category = Column(String(64), index=True, nullable=False)
    
    beneficiary_type = Column(String(255), nullable=True)
    beneficiary_type_ta = Column(String(255), nullable=True)
    benefit_summary = Column(Text, nullable=False)
    benefit_summary_ta = Column(Text, nullable=False)
    benefit_amount = Column(String(128), nullable=False)
    
    description = Column(Text, nullable=False)
    description_ta = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    conditions = relationship(
        "EligibilityCondition", 
        back_populates="scheme", 
        cascade="all, delete-orphan", 
        lazy="joined"
    )
    documents = relationship(
        "RequiredDocument", 
        back_populates="scheme", 
        cascade="all, delete-orphan", 
        lazy="joined"
    )
    steps = relationship(
        "ApplicationStep", 
        back_populates="scheme", 
        cascade="all, delete-orphan", 
        order_by="ApplicationStep.step_number",
        lazy="joined"
    )
    source = relationship(
        "OfficialSource", 
        back_populates="scheme", 
        uselist=False, 
        cascade="all, delete-orphan", 
        lazy="joined"
    )
