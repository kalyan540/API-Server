from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from app.models.user import User
from app.auth.routes import get_current_user
from app.middleware import limiter
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])

# Pydantic models
class UserInfo(BaseModel):
    id: int
    email: str
    is_admin: bool
    created_at: datetime
    device_count: int

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserInfo)
@limiter.limit("30/minute")
async def get_current_user_info(request: Request, current_user: User = Depends(get_current_user)):
    """Get current user's information including device count"""
    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        device_count=len(current_user.devices)
    ) 