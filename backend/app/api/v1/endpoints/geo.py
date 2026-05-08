from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.schemas.product_schemas import GeoSearchRequest, ProductOut, ProductListResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/geo", tags=["Geolocalização"])

@router.get("/products", response_model=ProductListResponse)
async def geo_search_products(latitude: float = Query(...), longitude: float = Query(...), radius_km: float = Query(10.0), max_price: Optional[float] = None, condition: Optional[str] = None, category: Optional[str] = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    params = GeoSearchRequest(latitude=latitude, longitude=longitude, radius_km=radius_km, max_price=max_price, condition=condition, category=category, page=page, page_size=page_size)
    total, products = await ProductService.geo_search(db, params)
    return ProductListResponse(total=total, page=page, page_size=page_size, results=[ProductOut.model_validate(p) for p in products])

@router.post("/products/search", response_model=ProductListResponse)
async def geo_search_post(params: GeoSearchRequest, db: AsyncSession = Depends(get_db)):
    total, products = await ProductService.geo_search(db, params)
    return ProductListResponse(total=total, page=params.page, page_size=params.page_size, results=[ProductOut.model_validate(p) for p in products])