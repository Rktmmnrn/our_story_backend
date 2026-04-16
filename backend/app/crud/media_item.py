"""CRUD operations for MediaItem model."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.media_item import MediaItem
from app.schemas.media_item import MediaItemCreate, MediaItemUpdate


class CRUDMediaItem:
    """CRUD operations for MediaItem."""

    async def get_by_id(
        self, db: AsyncSession, item_id: UUID
    ) -> Optional[MediaItem]:
        """Get media item by ID."""
        result = await db.execute(
            select(MediaItem)
            .where(MediaItem.id == item_id)
            .options(selectinload(MediaItem.uploaded_by))
        )
        return result.scalar_one_or_none()

    async def list_by_couple(
        self, db: AsyncSession, couple_id: UUID, skip: int = 0, limit: int = 50
    ) -> list[MediaItem]:
        """List media items for a couple."""
        result = await db.execute(
            select(MediaItem)
            .where(MediaItem.couple_id == couple_id)
            .offset(skip)
            .limit(limit)
            .order_by(MediaItem.created_at.desc())
            .options(selectinload(MediaItem.uploaded_by))
        )
        return list(result.scalars().all())

    async def count_by_couple(self, db: AsyncSession, couple_id: UUID) -> int:
        """Count media items for a couple."""
        result = await db.execute(
            select(func.count(MediaItem.id)).where(MediaItem.couple_id == couple_id)
        )
        return result.scalar_one()

    async def count_all(self, db: AsyncSession) -> int:
        """Count all media items."""
        result = await db.execute(select(func.count(MediaItem.id)))
        return result.scalar_one()

    async def count_by_type(self, db: AsyncSession, media_type: str) -> int:
        """Count media items by type."""
        result = await db.execute(
            select(func.count(MediaItem.id)).where(MediaItem.media_type == media_type)
        )
        return result.scalar_one()

    async def create(
        self,
        db: AsyncSession,
        couple_id: UUID,
        uploaded_by: UUID,
        media_type: str,
        file_path: str,
        original_filename: str,
        file_size_bytes: int,
        mime_type: str,
        obj_in: MediaItemCreate,
    ) -> MediaItem:
        """Create a new media item."""
        media_item = MediaItem(
            couple_id=couple_id,
            uploaded_by_id=uploaded_by,
            media_type=media_type,
            file_path=file_path,
            original_filename=original_filename,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            title=obj_in.title,
            description=obj_in.description,
            taken_at=obj_in.taken_at,
        )
        db.add(media_item)
        await db.commit()
        await db.refresh(media_item, ["uploaded_by"])
        return media_item

    async def update(
        self, db: AsyncSession, item: MediaItem, obj_in: MediaItemUpdate
    ) -> MediaItem:
        """Update media item metadata."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await db.commit()
        await db.refresh(item, ["uploaded_by"])
        return item

    async def delete(self, db: AsyncSession, item: MediaItem) -> str:
        """Delete a media item and return file path for cleanup."""
        file_path = item.file_path
        await db.delete(item)
        await db.commit()
        return file_path