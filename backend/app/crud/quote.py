"""CRUD operations for Quote model."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.quote import Quote
from app.schemas.quote import QuoteCreate, QuoteUpdate


class CRUDQuote:
    """CRUD operations for Quote."""

    async def get_by_id(self, db: AsyncSession, quote_id: UUID) -> Optional[Quote]:
        """Get quote by ID."""
        result = await db.execute(
            select(Quote)
            .where(Quote.id == quote_id)
            .options(selectinload(Quote.creator))
        )
        return result.scalar_one_or_none()

    async def list_by_couple(
        self, db: AsyncSession, couple_id: UUID, favorites_only: bool = False
    ) -> list[Quote]:
        """List quotes for a couple, optionally filtering favorites."""
        query = select(Quote).where(Quote.couple_id == couple_id)

        if favorites_only:
            query = query.where(Quote.is_favorite == True)

        query = query.order_by(Quote.created_at.desc()).options(
            selectinload(Quote.creator)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_all(self, db: AsyncSession) -> int:
        """Count all quotes."""
        result = await db.execute(select(func.count(Quote.id)))
        return result.scalar_one()

    async def create(
        self,
        db: AsyncSession,
        couple_id: UUID,
        created_by: UUID,
        obj_in: QuoteCreate,
    ) -> Quote:
        """Create a new quote."""
        quote = Quote(
            couple_id=couple_id,
            created_by=created_by,
            text=obj_in.text,
            author=obj_in.author,
        )
        db.add(quote)
        await db.commit()
        await db.refresh(quote, ["created_by"])
        return quote

    async def update(
        self, db: AsyncSession, quote: Quote, obj_in: QuoteUpdate
    ) -> Quote:
        """Update quote information."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(quote, field, value)

        await db.commit()
        await db.refresh(quote, ["created_by"])
        return quote

    async def delete(self, db: AsyncSession, quote: Quote) -> None:
        """Delete a quote."""
        await db.delete(quote)
        await db.commit()


crud_quote = CRUDQuote()