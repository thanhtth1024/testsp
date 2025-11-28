"""
Project model - represents projects in the system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class Project(Base):
    """
    Project model for managing projects.
    
    Attributes:
        id: Primary key
        name: Project name
        description: Project description
        owner_id: Foreign key to user (project owner)
        status: Project status
        start_date: Project start date
        end_date: Project end date
        created_at: Project creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    simulation_logs = relationship("SimulationLog", back_populates="project", cascade="all, delete-orphan")
