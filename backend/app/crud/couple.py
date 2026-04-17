"""CRUD operations for Couple model."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.couple import Couple
from app.schemas.couple import CoupleUpdate


class CRUDCouple:
    """CRUD operations for Couple."""

    async def get_by_id(self, db: AsyncSession, couple_id: UUID) -> Optional[Couple]:
        """Get couple by ID with relationships loaded."""
        result = await db.execute(
            select(Couple)
            .where(Couple.id == couple_id)
            .options(selectinload(Couple.user1), selectinload(Couple.user2))
        )
        return result.scalar_one_or_none()

    async def get_active_by_user_id(
        self, db: AsyncSession, user_id: UUID
    ) -> Optional[Couple]:
        """Get active couple for a user."""
        result = await db.execute(
            select(Couple)
            .where(
                or_(Couple.user1_id == user_id, Couple.user2_id == user_id),
                Couple.is_active == True,
            )
            .options(selectinload(Couple.user1), selectinload(Couple.user2))
        )
        return result.scalar_one_or_none()

    async def get_by_invite_token(
        self, db: AsyncSession, token: str
    ) -> Optional[Couple]:
        """Get couple by invite token."""
        result = await db.execute(
            select(Couple)
            .where(Couple.invite_token == token)
            .options(selectinload(Couple.user1), selectinload(Couple.user2))
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        user1_id: UUID,
        anniversary_date: date,
        couple_name: Optional[str] = None,
    ) -> Couple:
        """Create a new couple."""
        couple = Couple(
            user1_id=user1_id,
            anniversary_date=anniversary_date,
            couple_name=couple_name,
        )
        db.add(couple)
        await db.commit()
        await db.refresh(couple, ["user1", "user2"])
        return couple

    async def update(
        self, db: AsyncSession, couple: Couple, obj_in: CoupleUpdate
    ) -> Couple:
        """Update couple information."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(couple, field, value)

        await db.commit()
        await db.refresh(couple, ["user1", "user2"])
        return couple

    async def set_invite_token(
        self, db: AsyncSession, couple: Couple, token: str, expires_at: datetime
    ) -> Couple:
        """Set invite token for couple."""
        couple.invite_token = token
        couple.invite_token_expires_at = expires_at
        await db.commit()
        await db.refresh(couple, ["user1", "user2"])
        return couple

    async def join_couple(
        self, db: AsyncSession, couple: Couple, user2_id: UUID
    ) -> Couple:
        """Join a user to a couple."""
        couple.user2_id = user2_id
        couple.invite_token = None
        couple.invite_token_expires_at = None
        await db.commit()
        await db.refresh(couple, ["user1", "user2"])
        return couple

    async def dissolve(self, db: AsyncSession, couple: Couple) -> Couple:
        """Dissolve a couple (set inactive)."""
        couple.is_active = False
        await db.commit()
        await db.refresh(couple, ["user1", "user2"])
        return couple

    async def list_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Couple]:
        """List all couples with pagination."""
        result = await db.execute(
            select(Couple)
            .offset(skip)
            .limit(limit)
            .order_by(Couple.created_at.desc())
            .options(selectinload(Couple.user1), selectinload(Couple.user2))
        )
        return list(result.scalars().all())

    async def count(self, db: AsyncSession) -> int:
        """Count total couples."""
        result = await db.execute(select(func.count(Couple.id)))
        return result.scalar_one()

    async def count_active(self, db: AsyncSession) -> int:
        """Count active couples."""
        result = await db.execute(
            select(func.count(Couple.id)).where(Couple.is_active == True)
        )
        return result.scalar_one()


crud_couple = CRUDCouple()