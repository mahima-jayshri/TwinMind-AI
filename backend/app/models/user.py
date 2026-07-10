from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, nullable=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    is_onboarded = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Digital DNA Profile
    digital_dna = Column(JSON, nullable=True)
    
    # Agent Settings
    preferred_mode = Column(String, default="mentor")  # mentor, best_friend, roast, future_me, interviewer
    preferred_tone = Column(String, default="professional")
    preferred_language = Column(String, default="english")
