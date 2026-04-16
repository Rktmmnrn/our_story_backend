"""CRUD operations for RefreshToken model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class CRUDRefreshToken:
    """CRUD operations for RefreshToken."""

    async def create(
        self,
        db: AsyncSession,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Create a new refresh token."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token

    async def get_valid_by_hash(
        self, db: AsyncSession, token_hash: str
    ) -> Optional[RefreshToken]:
        """Get a valid (non-revoked, non-expired) refresh token by hash."""
        now = datetime.utcnow()
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, db: AsyncSession, token: RefreshToken) -> None:
        """Revoke a refresh token."""
        token.revoked = True
        await db.commit()

    async def revoke_all_for_user(self, db: AsyncSession, user_id: UUID) -> None:
        """Revoke all refresh tokens for a user."""
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
            )
        )
        tokens = result.scalars().all()

        for token in tokens:
            token.revoked = True

        await db.commit()

    async def delete_expired(self, db: AsyncSession) -> int:
        """Delete expired refresh tokens and return count."""
        now = datetime.utcnow()
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.expires_at <= now)
        )
        tokens = result.scalars().all()

        count = len(tokens)
        for token in tokens:
            await db.delete(token)

        await db.commit()
        return count