"""
Authentication schemas for request/response validation.
Defines Pydantic models for user registration, login, and token responses.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """
    Schema for user registration request.
    """
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=6, description="User password (minimum 6 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "nguyen.van.a@example.com",
                "username": "nguyenvana",
                "password": "matkhau123",
                "full_name": "Nguyễn Văn A"
            }
        }
    )

class UserLogin(BaseModel):
    """
    Schema for user login request.
    """
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "nguyenvana",
                "password": "matkhau123"
            }
        }
    )

class Token(BaseModel):
    """
    Schema for JWT token response.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

class UserResponse(BaseModel):
    """
    Schema for user information response.
    Excludes sensitive data like password_hash.
    """
    id: int
    email: str
    username: str
    full_name: str
    role: str
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "nguyen.van.a@example.com",
                "username": "nguyenvana",
                "full_name": "Nguyễn Văn A",
                "role": "user",
                "created_at": "2024-01-15T10:30:00"
            }
        }
    )

class TokenData(BaseModel):
    """
    Schema for decoded token data.
    Used internally for token validation.
    """
    user_id: int
    username: str
    role: str
    exp: Optional[int] = None

class MessageResponse(BaseModel):
    """
    Schema for simple message responses.
    """
    message: str
    success: bool = True
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Thao tác thành công",
                "success": True
            }
        }
    )
