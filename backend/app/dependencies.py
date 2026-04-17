"""
FastAPI dependency injection.
All reusable dependencies: DB session, current user, couple guard, admin guard.
"""
from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.utils.auth import decode_access_token


bearer_scheme = HTTPBearer()


# ── Database ──────────────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Auth ──────────────────────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Validates JWT access token, returns the User model instance.
    Import User model inside function to avoid circular imports.
    """
    from app.crud.user import crud_user  # noqa: avoid circular

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await crud_user.get_by_id(db, UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def require_admin(current_user=Depends(get_current_user)):
    """Requires the current user to have the admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )
    return current_user


async def get_current_couple(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the active Couple of the current user.
    Raises 403 if user has no active couple.
    """
    from app.crud.couple import crud_couple  # noqa: avoid circular

    couple = await crud_couple.get_active_by_user_id(db, current_user.id)
    if couple is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'appartenez à aucun couple actif",
        )
    return couple