from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Tuple
from math import radians, cos, sin, asin, sqrt
from app.models.models import Product, User
from app.schemas.product_schemas import ProductCreate, ProductUpdate, GeoSearchRequest

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

class ProductService:

    @staticmethod
    async def create(db: AsyncSession, data: ProductCreate, seller: User) -> Product:
        product = Product(**data.model_dump(), seller_id=seller.id)
        db.add(product)
        await db.flush()
        await db.refresh(product)
        return product

    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: int) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.id == product_id, Product.is_active == True))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_products(db, page=1, page_size=20, category=None, condition=None, max_price=None, seller_id=None):
        q = select(Product).where(Product.is_active == True)
        if category: q = q.where(Product.category == category)
        if condition: q = q.where(Product.condition == condition)
        if max_price: q = q.where(Product.price <= max_price)
        if seller_id: q = q.where(Product.seller_id == seller_id)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        q = q.order_by(Product.created_at.desc()).offset((page-1)*page_size).limit(page_size)
        products = (await db.execute(q)).scalars().all()
        return total, list(products)

    @staticmethod
    async def geo_search(db: AsyncSession, params: GeoSearchRequest):
        q = select(Product).where(Product.is_active == True, Product.latitude.isnot(None), Product.longitude.isnot(None))
        if params.max_price: q = q.where(Product.price <= params.max_price)
        if params.condition: q = q.where(Product.condition == params.condition)
        if params.category: q = q.where(Product.category == params.category)
        all_products = (await db.execute(q)).scalars().all()
        with_distance = []
        for p in all_products:
            dist = haversine_km(params.latitude, params.longitude, p.latitude, p.longitude)
            if dist <= params.radius_km:
                obj = {**p.__dict__, "distance_km": round(dist, 2)}
                obj.pop("_sa_instance_state", None)
                with_distance.append(obj)
        with_distance.sort(key=lambda x: (x["distance_km"], x["price"]))
        total = len(with_distance)
        start = (params.page - 1) * params.page_size
        return total, with_distance[start: start + params.page_size]

    @staticmethod
    async def update(db, product, data, seller):
        if product.seller_id != seller.id and seller.role != "admin":
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Sem permissão.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(product, field, value)
        await db.flush()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete(db, product, seller):
        if product.seller_id != seller.id and seller.role != "admin":
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Sem permissão.")
        product.is_active = False
        await db.flush()