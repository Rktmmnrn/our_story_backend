from datetime import datetime, date
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey, CheckConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base
from backend.app.models.media_item import MediaItem
from backend.app.models.music_track import MusicTrack
from backend.app.models.quote import Quote
from backend.app.models.special_date import SpecialDate
from backend.app.models.user import User

from app.models import Base

class Couple(Base):
    __tablename__ = "couples"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    user1_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    user2_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )
    couple_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    anniversary_date: Mapped[date] = mapped_column(Date, nullable=False)
    invite_token: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        nullable=True
    )
    invite_token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    __table_args__ = (
        CheckConstraint("user1_id != user2_id", name="check_different_users"),
    )
    
    # Relationships
    user1: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user1_id],
        back_populates="couple_as_user1"
    )
    user2: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[user2_id],
        back_populates="couple_as_user2"
    )
    media_items: Mapped[List["MediaItem"]] = relationship(
        "MediaItem",
        foreign_keys="MediaItem.couple_id",
        back_populates="couple"
    )
    music_tracks: Mapped[List["MusicTrack"]] = relationship(
        "MusicTrack",
        foreign_keys="MusicTrack.couple_id",
        back_populates="couple"
    )
    special_dates: Mapped[List["SpecialDate"]] = relationship(
        "SpecialDate",
        foreign_keys="SpecialDate.couple_id",
        back_populates="couple"
    )
    quotes: Mapped[List["Quote"]] = relationship(
        "Quote",
        foreign_keys="Quote.couple_id",
        back_populates="couple"
    )
    
    def __repr__(self) -> str:
        return f"<Couple(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id})>"