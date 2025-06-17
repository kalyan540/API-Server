import os
import jwt
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Configuration
JWT_SECRET_BASE64 = os.getenv("JWT_SECRET_BASE64", "WsNiwFBf2CJqVRz8/9OT58zgsXtRqArsUtvoeFrI+rc=")
JWT_SECRET = base64.b64decode(JWT_SECRET_BASE64)
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
WEBSOCKET_TOKEN_EXPIRE_HOURS = 1  # Changed to 1 hour like MQTT example

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int, email: str, role: str = "user") -> str:
    """Create a JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_websocket_token(user_id: int, email: str, device_topics: Optional[List[str]] = None) -> str:
    """Create a WebSocket/MQTT streaming token following the MQTT pattern"""
    expire = datetime.now(timezone.utc) + timedelta(hours=WEBSOCKET_TOKEN_EXPIRE_HOURS)
    
    # Default topics based on user_id for device-specific streaming
    if device_topics is None:
        device_topics = [
            f"devices/{user_id}/#",  # All topics for user's devices
            f"user/{user_id}/data",  # User-specific data topic
            f"user/{user_id}/status" # User-specific status topic
        ]
    
    payload = {
        "sub": email,  # Use email as the subject like MQTT example
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(expire.timestamp()),
        "subs": device_topics,  # Subscription topics user can listen to
        "publ": [f"devices/{user_id}/commands"],  # Publish topics user can send to
        "user_id": user_id,  # Additional user context
        "type": "websocket"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_websocket_token(token: str) -> Optional[dict]:
    """Verify WebSocket/MQTT token and return payload with topic permissions"""
    payload = verify_token(token)
    if payload and payload.get("type") == "websocket":
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("sub"),
            "subscription_topics": payload.get("subs", []),
            "publish_topics": payload.get("publ", []),
            "expires_at": payload.get("exp")
        }
    return None 