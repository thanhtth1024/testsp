"""
ForecastLog model - stores AI predictions for tasks.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ForecastLog(Base):
    """
    ForecastLog model for storing AI risk predictions.
    
    Attributes:
        id: Primary key
        task_id: Foreign key to task
        risk_level: Predicted risk level
        risk_percentage: Risk percentage (0-100)
        predicted_delay_days: Predicted delay in days
        analysis: AI analysis text
        recommendations: AI recommendations
        created_at: Forecast creation timestamp
    """
    __tablename__ = "forecast_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_percentage = Column(Float, nullable=False)  # 0-100
    predicted_delay_days = Column(Integer, default=0, nullable=False)
    analysis = Column(Text, nullable=False)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    task = relationship("Task", back_populates="forecast_logs")
