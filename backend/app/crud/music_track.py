"""CRUD operations for MusicTrack model."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.music_track import MusicTrack
from app.schemas.music_track import MusicTrackCreate, MusicTrackUpdate


class CRUDMusicTrack:
    """CRUD operations for MusicTrack."""

    async def get_by_id(
        self, db: AsyncSession, track_id: UUID
    ) -> Optional[MusicTrack]:
        """Get music track by ID."""
        result = await db.execute(
            select(MusicTrack)
            .where(MusicTrack.id == track_id)
            .options(selectinload(MusicTrack.uploaded_by))
        )
        return result.scalar_one_or_none()

    async def list_by_couple(
        self, db: AsyncSession, couple_id: UUID
    ) -> list[MusicTrack]:
        """List music tracks for a couple."""
        result = await db.execute(
            select(MusicTrack)
            .where(MusicTrack.couple_id == couple_id)
            .order_by(MusicTrack.created_at.desc())
            .options(selectinload(MusicTrack.uploaded_by))
        )
        return list(result.scalars().all())

    async def count_all(self, db: AsyncSession) -> int:
        """Count all music tracks."""
        result = await db.execute(select(func.count(MusicTrack.id)))
        return result.scalar_one()

    async def create(
        self,
        db: AsyncSession,
        couple_id: UUID,
        uploaded_by: UUID,
        file_path: str,
        obj_in: MusicTrackCreate,
    ) -> MusicTrack:
        """Create a new music track."""
        track = MusicTrack(
            couple_id=couple_id,
            uploaded_by_id=uploaded_by,
            file_path=file_path,
            title=obj_in.title,
            artist=obj_in.artist,
        )
        db.add(track)
        await db.commit()
        await db.refresh(track, ["uploaded_by"])
        return track

    async def update(
        self, db: AsyncSession, track: MusicTrack, obj_in: MusicTrackUpdate
    ) -> MusicTrack:
        """Update music track information."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(track, field, value)

        await db.commit()
        await db.refresh(track, ["uploaded_by"])
        return track

    async def delete(self, db: AsyncSession, track: MusicTrack) -> str:
        """Delete a music track and return file path for cleanup."""
        file_path = track.file_path
        await db.delete(track)
        await db.commit()
        return file_path