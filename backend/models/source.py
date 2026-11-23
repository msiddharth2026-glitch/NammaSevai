from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class OfficialSource(Base):
    __tablename__ = "official_sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    source_name = Column(String(255), nullable=False)
    portal_url = Column(String(512), nullable=False)
    verified_date = Column(String(32), nullable=False)  # YYYY-MM-DD
    verification_status = Column(String(32), default="verified")  # verified, pending_recheck, outdated
    helpline_number = Column(String(128), nullable=True)
    government_order_ref = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    scheme = relationship("Scheme", back_populates="source")
