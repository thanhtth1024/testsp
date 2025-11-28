"""
User model - represents system users.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        email: User's unique email address
        username: User's unique username
        full_name: User's full name
        password_hash: Hashed password
        role: User role (user/admin)
        created_at: Account creation timestamp
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", back_populates="assignee")
