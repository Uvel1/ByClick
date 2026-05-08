from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    role: Literal["buyer", "seller"] = "buyer"
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class UserUpdateLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None