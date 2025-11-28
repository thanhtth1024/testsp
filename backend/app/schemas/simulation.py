"""
Simulation schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

class SimulationRequest(BaseModel):
    """Schema for simulation request"""
    project_id: int = Field(..., description="Project ID to simulate")
    scenario: str = Field(..., min_length=10, description="Scenario description")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": 1,
                "scenario": "Nếu task 'Thiết kế giao diện' chậm 5 ngày"
            }
        }
    )

class SimulationResponse(BaseModel):
    """Schema for simulation response"""
    id: int
    project_id: int
    scenario: str = Field(..., description="Scenario description")
    affected_task_ids: Optional[List[int]] = Field(default=[], description="List of affected task IDs")
    total_delay_days: int = Field(default=0, description="Total predicted delay in days")
    analysis: str = Field(..., description="AI impact analysis")
    recommendations: Optional[str] = None
    simulated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "project_id": 1,
                "scenario": "Nếu task 'Thiết kế giao diện' chậm 5 ngày",
                "affected_task_ids": [2, 3, 5],
                "total_delay_days": 7,
                "analysis": "Nếu task này chậm 5 ngày, sẽ ảnh hưởng đến 3 task phụ thuộc...",
                "recommendations": "Cần ưu tiên task này hoặc tái phân bổ nguồn lực",
                "simulated_at": "2025-01-15T12:00:00"
            }
        }
    )

class SimulationListResponse(BaseModel):
    """Schema for simulation list response"""
    simulations: list[SimulationResponse]
    total: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "simulations": [],
                "total": 0
            }
        }
    )
