from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.models import User
from app.core.security import hash_password, verify_password
from app.schemas.user_schemas import RegisterRequest

class UserService:

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: RegisterRequest) -> User:
        existing = await UserService.get_by_email(db, data.email)
        if existing:
            from fastapi import HTTPException
            raise HTTPException(status_code=409, detail="Email já registado.")
        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role,
            phone=data.phone,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await UserService.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def update_location(db: AsyncSession, user: User, latitude: float, longitude: float, address: Optional[str] = None) -> User:
        user.latitude = latitude
        user.longitude = longitude
        if address:
            user.address = address
        await db.flush()
        await db.refresh(user)
        return user