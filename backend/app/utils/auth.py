"""
Authentication utilities for JWT token handling and password hashing.
Provides functions for password verification, token creation, and user authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenData

# Configuration
SECRET_KEY = "your-secret-key-change-in-production-ai-deadline-2024-secure-key-123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password from user input
        hashed_password: Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user data to encode in token
        expires_delta: Optional token expiration time delta
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData: Decoded token data if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        
        if user_id is None or username is None:
            return None
            
        return TokenData(user_id=user_id, username=username, role=role, exp=exp)
    except JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    token_data = decode_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin role for protected endpoints.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current user if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập. Chỉ admin mới có thể thực hiện thao tác này."
        )
    
    return current_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username/email and password.
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
        
    Returns:
        User: Authenticated user if credentials are valid, None otherwise
    """
    # Try to find user by username or email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user
