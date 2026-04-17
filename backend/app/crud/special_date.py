"""CRUD operations for SpecialDate model."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.special_date import SpecialDate
from app.schemas.special_date import SpecialDateCreate, SpecialDateUpdate


class CRUDSpecialDate:
    """CRUD operations for SpecialDate."""

    async def get_by_id(
        self, db: AsyncSession, date_id: UUID
    ) -> Optional[SpecialDate]:
        """Get special date by ID."""
        result = await db.execute(
            select(SpecialDate)
            .where(SpecialDate.id == date_id)
            .options(selectinload(SpecialDate.creator))
        )
        return result.scalar_one_or_none()

    async def list_by_couple(
        self, db: AsyncSession, couple_id: UUID
    ) -> list[SpecialDate]:
        """List special dates for a couple, sorted by event date."""
        result = await db.execute(
            select(SpecialDate)
            .where(SpecialDate.couple_id == couple_id)
            .order_by(SpecialDate.event_date.asc())
            .options(selectinload(SpecialDate.creator))
        )
        return list(result.scalars().all())

    async def count_all(self, db: AsyncSession) -> int:
        """Count all special dates."""
        result = await db.execute(select(func.count(SpecialDate.id)))
        return result.scalar_one()

    async def create(
        self,
        db: AsyncSession,
        couple_id: UUID,
        created_by: UUID,
        obj_in: SpecialDateCreate,
    ) -> SpecialDate:
        """Create a new special date."""
        special_date = SpecialDate(
            couple_id=couple_id,
            created_by=created_by,
            title=obj_in.title,
            event_date=obj_in.event_date,
            description=obj_in.description,
            emoji=obj_in.emoji,
        )
        db.add(special_date)
        await db.commit()
        await db.refresh(special_date, ["created_by"])
        return special_date

    async def update(
        self, db: AsyncSession, special_date: SpecialDate, obj_in: SpecialDateUpdate
    ) -> SpecialDate:
        """Update special date information."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(special_date, field, value)

        await db.commit()
        await db.refresh(special_date, ["created_by"])
        return special_date

    async def delete(self, db: AsyncSession, special_date: SpecialDate) -> None:
        """Delete a special date."""
        await db.delete(special_date)
        await db.commit()


crud_special_date = CRUDSpecialDate()