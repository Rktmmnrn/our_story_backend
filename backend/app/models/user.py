from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, Enum, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(
        Enum("user", "admin", name="user_role_enum"),
        nullable=False,
        server_default="user",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships — string refs only, no direct imports ──────────────────
    couple_as_user1: Mapped[Optional["Couple"]] = relationship(
        "Couple",
        foreign_keys="Couple.user1_id",
        back_populates="user1",
        uselist=False,
    )
    couple_as_user2: Mapped[Optional["Couple"]] = relationship(
        "Couple",
        foreign_keys="Couple.user2_id",
        back_populates="user2",
        uselist=False,
    )
    media_items: Mapped[List["MediaItem"]] = relationship(
        "MediaItem",
        foreign_keys="MediaItem.uploaded_by",
        back_populates="uploader",
    )
    music_tracks: Mapped[List["MusicTrack"]] = relationship(
        "MusicTrack",
        foreign_keys="MusicTrack.uploaded_by",
        back_populates="uploader",
    )
    special_dates: Mapped[List["SpecialDate"]] = relationship(
        "SpecialDate",
        foreign_keys="SpecialDate.created_by",
        back_populates="creator",
    )
    quotes: Mapped[List["Quote"]] = relationship(
        "Quote",
        foreign_keys="Quote.created_by",
        back_populates="creator",
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        foreign_keys="RefreshToken.user_id",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User(email={self.email})>"