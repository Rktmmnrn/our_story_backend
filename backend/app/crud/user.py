"""CRUD operations for User model."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    """CRUD operations for User."""

    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, obj_in: UserCreate, hashed_password: str
    ) -> User:
        """Create a new user."""
        user = User(
            email=obj_in.email,
            password_hash=hashed_password,
            display_name=obj_in.display_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update(
        self, db: AsyncSession, user: User, obj_in: UserUpdate
    ) -> User:
        """Update user information."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    async def set_avatar(
        self, db: AsyncSession, user: User, avatar_url: str
    ) -> User:
        """Set user avatar URL."""
        user.avatar_url = avatar_url
        await db.commit()
        await db.refresh(user)
        return user

    async def list_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """List all users with pagination."""
        result = await db.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def count(self, db: AsyncSession) -> int:
        """Count total users."""
        result = await db.execute(select(func.count(User.id)))
        return result.scalar_one()

    async def delete(self, db: AsyncSession, user: User) -> None:
        """Delete a user."""
        await db.delete(user)
        await db.commit()


crud_user = CRUDUser()