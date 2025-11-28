"""
Project schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional

class ProjectBase(BaseModel):
    """Base schema for project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Dự án Website Công ty",
                "description": "Xây dựng website corporate cho công ty",
                "start_date": "2025-01-01",
                "end_date": "2025-06-30"
            }
        }
    )

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|on_hold)$")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Dự án Website Công ty (Updated)",
                "status": "active"
            }
        }
    )

class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    owner_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    owner_name: Optional[str] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Dự án Website Công ty",
                "description": "Xây dựng website corporate",
                "owner_id": 1,
                "owner_name": "Nguyễn Văn A",
                "start_date": "2025-01-01",
                "end_date": "2025-06-30",
                "status": "active",
                "total_tasks": 15,
                "completed_tasks": 8,
                "created_at": "2025-01-01T10:00:00",
                "updated_at": "2025-01-15T14:30:00"
            }
        }
    )

class ProjectListResponse(BaseModel):
    """Schema for project list response"""
    projects: list[ProjectResponse]
    total: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "projects": [],
                "total": 0
            }
        }
    )
