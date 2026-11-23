from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(128), unique=True, index=True, nullable=False)
    preferred_language = Column(String(16), default="ta")
    
    # Demographic information (voluntarily provided)
    age = Column(Integer, nullable=True)
    gender = Column(String(16), nullable=True)  # female, male, other
    occupation = Column(String(128), nullable=True)
    annual_income = Column(Float, nullable=True)
    state = Column(String(64), default="Tamil Nadu")
    district = Column(String(64), nullable=True)
    education_level = Column(String(64), nullable=True)
    school_type = Column(String(32), nullable=True)  # government, private, aided
    
    # Sensitive attributes (ONLY stored when citizen voluntarily provides them and they are relevant)
    community_category = Column(String(32), nullable=True)  # SC, ST, BC, MBC, General
    disability_status = Column(Boolean, nullable=True)
    disability_type = Column(String(64), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
