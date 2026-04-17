"""
Authentication service: register, login, token refresh, logout.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.utils.auth import (
    hash_password, verify_password,
    create_access_token,
    generate_refresh_token, hash_refresh_token, refresh_token_expires_at,
)


async def register_user(db: AsyncSession, email: str, password: str, display_name: str):
    from app.crud.user import crud_user
    from app.schemas.user import UserCreate

    existing = await crud_user.get_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cet email existe déjà",
        )
    obj_in = UserCreate(email=email, password=password, display_name=display_name)
    user = await crud_user.create(db, obj_in, hash_password(password))
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> dict:
    from app.crud.user import crud_user
    from app.crud.refresh_token import crud_refresh_token

    user = await crud_user.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé",
        )

    access_token = create_access_token(str(user.id), user.role)
    raw_refresh, token_hash = generate_refresh_token()

    await crud_refresh_token.create(
        db,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=refresh_token_expires_at(),
    )

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh,
        "token_type": "bearer",
    }


async def refresh_tokens(db: AsyncSession, raw_refresh_token: str) -> dict:
    from app.crud.refresh_token import crud_refresh_token
    from app.crud.user import crud_user

    token_hash = hash_refresh_token(raw_refresh_token)
    stored = await crud_refresh_token.get_valid_by_hash(db, token_hash)

    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré",
        )

    user = await crud_user.get_by_id(db, stored.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
        )

    # Rotate: revoke old, create new
    await crud_refresh_token.revoke(db, stored)

    access_token = create_access_token(str(user.id), user.role)
    raw_new, new_hash = generate_refresh_token()
    await crud_refresh_token.create(
        db,
        user_id=user.id,
        token_hash=new_hash,
        expires_at=refresh_token_expires_at(),
    )

    return {
        "access_token": access_token,
        "refresh_token": raw_new,
        "token_type": "bearer",
    }


async def logout_user(db: AsyncSession, raw_refresh_token: str) -> None:
    from app.crud.refresh_token import crud_refresh_token

    token_hash = hash_refresh_token(raw_refresh_token)
    stored = await crud_refresh_token.get_valid_by_hash(db, token_hash)
    if stored:
        await crud_refresh_token.revoke(db, stored)