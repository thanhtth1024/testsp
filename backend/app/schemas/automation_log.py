"""
Automation log schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any

class AutomationLogResponse(BaseModel):
    """Schema for automation log response"""
    id: int
    workflow_name: str
    status: str
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    executed_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "workflow_name": "Quick Progress Forecast",
                "status": "success",
                "input_data": {"tasks_analyzed": 10},
                "output_data": {"high_risk_tasks": 2},
                "error_message": None,
                "executed_at": "2025-01-15T11:00:00"
            }
        }
    )

class AutomationLogListResponse(BaseModel):
    """Schema for automation log list response"""
    logs: list[AutomationLogResponse]
    total: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "logs": [],
                "total": 0
            }
        }
    )
