from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_type = Column(String, nullable=False)  # task_completion, procrastination, productivity
    confidence_score = Column(Float, nullable=False)  # 0-100
    prediction_data = Column(JSON, nullable=False)
    factors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="predictions")


class ProductivityMetric(Base):
    __tablename__ = "productivity_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    tasks_completed = Column(Integer, default=0)
    tasks_planned = Column(Integer, default=0)
    focus_hours = Column(Float, default=0.0)
    distraction_count = Column(Integer, default=0)
    mood = Column(String, nullable=True)
    energy_level = Column(Integer, nullable=True)  # 1-10
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="productivity_metrics")
