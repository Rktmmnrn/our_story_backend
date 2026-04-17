from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import String, Text, Enum, BigInteger, DateTime, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.couple import Couple

class MediaItem(Base):
    __tablename__ = "media_items"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    couple_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("couples.id", ondelete="CASCADE"),
        nullable=False
    )
    uploaded_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    media_type: Mapped[str] = mapped_column(
        Enum("photo", "video", name="media_type_enum"),
        nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    taken_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    couple: Mapped["Couple"] = relationship(
        "Couple",
        foreign_keys=[couple_id],
        back_populates="media_items"
    )
    uploader: Mapped["User"] = relationship(
        "User",
        foreign_keys=[uploaded_by],
        back_populates="media_items"
    )
    
    def __repr__(self) -> str:
        return f"<MediaItem(id={self.id}, type={self.media_type}, filename={self.original_filename})>"