"""
Task schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional

class TaskBase(BaseModel):
    """Base schema for task"""
    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    project_id: int = Field(..., description="Project ID this task belongs to")
    assigned_to: Optional[int] = Field(None, description="User ID of assignee")
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    status: str = Field(default="todo", pattern="^(todo|in_progress|done|blocked)$")
    deadline: Optional[date] = Field(None, description="Task deadline")

class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours to complete")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Thiết kế giao diện trang chủ",
                "description": "Thiết kế UI/UX cho trang chủ website",
                "project_id": 1,
                "assigned_to": 2,
                "priority": "high",
                "status": "todo",
                "deadline": "2025-02-15",
                "estimated_hours": 40
            }
        }
    )

class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(todo|in_progress|done|blocked)$")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    deadline: Optional[date] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "in_progress",
                "progress": 60,
                "actual_hours": 25
            }
        }
    )

class TaskProgressUpdate(BaseModel):
    """Schema for updating task progress"""
    progress: int = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "progress": 75
            }
        }
    )

class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    progress: int
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    last_progress_update: datetime
    
    # Additional computed fields
    assigned_name: Optional[str] = None
    project_name: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Thiết kế giao diện trang chủ",
                "description": "Thiết kế UI/UX cho trang chủ website",
                "project_id": 1,
                "project_name": "Dự án Website",
                "assigned_to": 2,
                "assigned_name": "Nguyễn Văn B",
                "priority": "high",
                "status": "in_progress",
                "progress": 60,
                "estimated_hours": 40,
                "actual_hours": 25,
                "deadline": "2025-02-15",
                "created_at": "2025-01-01T10:00:00",
                "updated_at": "2025-01-15T14:30:00",
                "last_progress_update": "2025-01-15T14:30:00"
            }
        }
    )

class TaskListResponse(BaseModel):
    """Schema for task list response"""
    tasks: list[TaskResponse]
    total: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tasks": [],
                "total": 0
            }
        }
    )
