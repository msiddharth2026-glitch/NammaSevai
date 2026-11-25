from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database import Base

class CitizenPilotFeedback(Base):
    __tablename__ = "citizen_pilot_feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(128), nullable=True, index=True)
    participant_category = Column(String(64), nullable=True)  # Student, Farmer, Woman Entrepreneur, Senior, etc.
    preferred_language = Column(String(16), nullable=False, default="ta")
    
    # 1 to 5 ratings
    ease_of_use_rating = Column(Integer, nullable=False)  # 1-5
    clarity_rating = Column(Integer, nullable=False)      # 1-5 (understanding conditions)
    usefulness_rating = Column(Integer, nullable=False)   # 1-5 (usefulness of recommendations)
    
    # Qualitative feedback
    problems_encountered = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
