from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from app.database import get_db
from app.models.user import User
from app.auth.jwt import hash_password, verify_password, create_access_token, create_websocket_token, verify_token
from app.middleware import limiter
from fastapi import Request

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class WebSocketTokenResponse(BaseModel):
    websocket_token: str
    token_type: str
    expires_in: int
    subscription_topics: List[str]
    publish_topics: List[str]
    user_id: int

@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        user_id=new_user.id,
        email=new_user.email,
        role="admin" if new_user.is_admin else "user"
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role="admin" if user.is_admin else "user"
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/stream/token", response_model=WebSocketTokenResponse)
@limiter.limit("5/minute")
async def get_websocket_token(request: Request, current_user: User = Depends(get_current_user)):
    """Issue a WebSocket/MQTT token for real-time streaming following MQTT pattern"""
    websocket_token = create_websocket_token(
        user_id=current_user.id,
        email=current_user.email
    )
    
    # Generate the topic lists for response
    subscription_topics = [
        f"devices/{current_user.id}/#",
        f"user/{current_user.id}/data",
        f"user/{current_user.id}/status"
    ]
    
    publish_topics = [f"devices/{current_user.id}/commands"]
    
    return WebSocketTokenResponse(
        websocket_token=websocket_token,
        token_type="websocket",
        expires_in=3600,  # 1 hour
        subscription_topics=subscription_topics,
        publish_topics=publish_topics,
        user_id=current_user.id
    ) 