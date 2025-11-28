"""
Task model - represents tasks within projects.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Task(Base):
    """
    Task model for project tasks.
    
    Attributes:
        id: Primary key
        name: Task name
        description: Task description
        project_id: Foreign key to project
        assigned_to: Foreign key to user (task assignee)
        status: Task status
        priority: Task priority level
        progress: Task completion percentage (0-100)
        deadline: Task deadline
        last_progress_update: Last time progress was updated
        created_at: Task creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0-100
    deadline = Column(DateTime, nullable=False)
    last_progress_update = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    forecast_logs = relationship("ForecastLog", back_populates="task", cascade="all, delete-orphan")
