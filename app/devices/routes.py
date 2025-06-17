from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.device import Device
from app.models.user import User
from app.auth.routes import get_current_user
from app.middleware import limiter
from fastapi import Request
import uuid

router = APIRouter(prefix="/devices", tags=["Devices"])

# Pydantic models
class DeviceCreate(BaseModel):
    name: str
    device_id: str = None  # Optional, will generate if not provided

class DeviceResponse(BaseModel):
    id: int
    name: str
    device_id: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DeviceList(BaseModel):
    devices: List[DeviceResponse]
    total: int

@router.get("/", response_model=DeviceList)
@limiter.limit("10/minute")
async def get_user_devices(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all devices belonging to the current user"""
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()
    
    return DeviceList(
        devices=[DeviceResponse.from_orm(device) for device in devices],
        total=len(devices)
    )

@router.post("/", response_model=DeviceResponse)
@limiter.limit("10/minute")
async def create_device(request: Request, device_data: DeviceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Register a new device for the current user"""
    # Generate device_id if not provided
    if not device_data.device_id:
        device_data.device_id = f"device_{uuid.uuid4().hex[:12]}"
    
    # Check if device_id already exists
    existing_device = db.query(Device).filter(Device.device_id == device_data.device_id).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device ID already exists"
        )
    
    # Create new device
    new_device = Device(
        name=device_data.name,
        device_id=device_data.device_id,
        user_id=current_user.id
    )
    
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    
    return DeviceResponse.from_orm(new_device)

@router.delete("/{device_id}")
@limiter.limit("10/minute")
async def delete_device(request: Request, device_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a device owned by the current user"""
    # Find device
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.user_id == current_user.id  # Ensure user owns the device
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by user"
        )
    
    # Delete device
    db.delete(device)
    db.commit()
    
    return {"message": f"Device {device.name} deleted successfully"}

@router.get("/{device_id}", response_model=DeviceResponse)
@limiter.limit("10/minute")
async def get_device(request: Request, device_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific device owned by the current user"""
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.user_id == current_user.id  # Ensure user owns the device
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by user"
        )
    
    return DeviceResponse.from_orm(device) 