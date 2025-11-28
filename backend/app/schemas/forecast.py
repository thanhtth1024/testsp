"""
Forecast schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ForecastResponse(BaseModel):
    """Schema for forecast log response"""
    id: int
    task_id: int
    task_name: Optional[str] = None
    risk_level: str
    risk_percentage: float = Field(..., ge=0, le=100, description="Risk percentage (0-100)")
    predicted_delay_days: int = Field(..., description="Predicted delay in days")
    analysis: str = Field(..., description="AI analysis text")
    recommendations: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "task_id": 1,
                "task_name": "Thiết kế giao diện",
                "risk_level": "high",
                "risk_percentage": 75.5,
                "predicted_delay_days": 3,
                "analysis": "Task có nguy cơ trễ cao do tiến độ chậm...",
                "recommendations": "Nên bổ sung thêm 1 người hoặc giảm scope",
                "created_at": "2025-01-15T11:00:00"
            }
        }
    )

class ForecastListResponse(BaseModel):
    """Schema for forecast list response"""
    forecasts: list[ForecastResponse]
    total: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "forecasts": [],
                "total": 0
            }
        }
    )
