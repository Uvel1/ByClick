from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ProductCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=1, ge=0)
    condition: Literal["new", "used"] = "new"
    category: Optional[str] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    condition: Optional[Literal["new", "used"]] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    stock: int
    condition: str
    category: Optional[str]
    image_url: Optional[str]
    is_active: bool
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    seller_id: int
    distance_km: Optional[float] = None
    created_at: datetime
    model_config = {"from_attributes": True}

class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[ProductOut]

class GeoSearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=10.0, gt=0, le=500)
    max_price: Optional[float] = Field(None, gt=0)
    condition: Optional[Literal["new", "used"]] = None
    category: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)