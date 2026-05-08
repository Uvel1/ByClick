from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_seller
from app.schemas.product_schemas import (
    ProductCreate, ProductUpdate, ProductOut, ProductListResponse,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Produtos"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    condition: Optional[str] = Query(None, pattern="^(new|used)$"),
    max_price: Optional[float] = Query(None, gt=0),
    seller_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lista produtos com filtros e paginação."""
    total, products = await ProductService.list_products(
        db, page, page_size, category, condition, max_price, seller_id
    )
    return ProductListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=[ProductOut.model_validate(p) for p in products],
    )


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Devolve um produto pelo ID."""
    product = await ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return product


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_seller),
):
    """Cria um produto (apenas vendedores)."""
    product = await ProductService.create(db, data, current_user)
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_seller),
):
    """Actualiza um produto (dono ou admin)."""
    product = await ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    updated = await ProductService.update(db, product, data, current_user)
    return updated


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_seller),
):
    """Desactiva um produto (soft delete)."""
    product = await ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    await ProductService.delete(db, product, current_user)
