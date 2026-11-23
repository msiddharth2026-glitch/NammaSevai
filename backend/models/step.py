from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ApplicationStep(Base):
    __tablename__ = "application_steps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    step_number = Column(Integer, nullable=False, default=1)
    mode = Column(String(16), default="both")  # online, offline, both
    title_en = Column(String(255), nullable=False)
    title_ta = Column(String(255), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ta = Column(Text, nullable=False)
    portal_url = Column(String(512), nullable=True)
    office_name_en = Column(String(255), nullable=True)
    office_name_ta = Column(String(255), nullable=True)

    scheme = relationship("Scheme", back_populates="steps")
