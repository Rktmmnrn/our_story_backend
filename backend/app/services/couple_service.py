"""
Couple service: creation, invitation by email, joining, timer calculation.
"""
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.auth import generate_invite_token, invite_token_expires_at
from app.utils.email import send_invite_email


async def create_couple(
    db: AsyncSession,
    user_id: UUID,
    anniversary_date: date,
    couple_name: str | None,
):
    from app.crud.couple import crud_couple

    # A user can only be in one active couple
    existing = await crud_couple.get_active_by_user_id(db, user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous appartenez déjà à un couple actif",
        )

    couple = await crud_couple.create(db, user_id, anniversary_date, couple_name)
    return couple


async def send_couple_invite(
    db: AsyncSession,
    couple_id: UUID,
    current_user_id: UUID,
    recipient_email: str,
):
    from app.crud.couple import crud_couple

    couple = await crud_couple.get_by_id(db, couple_id)
    if not couple or not couple.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couple introuvable")

    if couple.user1_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    if couple.user2_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce couple a déjà deux membres",
        )

    token = generate_invite_token()
    expires_at = invite_token_expires_at()

    await crud_couple.set_invite_token(db, couple, token, expires_at)

    invite_link = f"{settings.FRONTEND_BASE_URL}/join/{token}"

    from app.crud.user import crud_user
    inviter = await crud_user.get_by_id(db, current_user_id)

    email_sent = await send_invite_email(
        recipient_email=recipient_email,
        inviter_name=inviter.display_name,
        invite_link=invite_link,
    )

    return {
        "invite_link": invite_link,
        "expires_at": expires_at,
        "email_sent": email_sent,
    }


async def join_couple_by_token(db: AsyncSession, token: str, user_id: UUID):
    from app.crud.couple import crud_couple

    # User must not already be in a couple
    existing = await crud_couple.get_active_by_user_id(db, user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous appartenez déjà à un couple actif",
        )

    couple = await crud_couple.get_by_invite_token(db, token)
    if not couple or not couple.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lien d'invitation invalide ou expiré",
        )

    # Check token expiry
    if couple.invite_token_expires_at and couple.invite_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Ce lien d'invitation a expiré",
        )

    if couple.user2_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce couple est déjà complet",
        )

    if couple.user1_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas rejoindre votre propre invitation",
        )

    couple = await crud_couple.join_couple(db, couple, user_id)
    return couple


def compute_timer(anniversary_date: date) -> dict:
    today = date.today()
    days_together = (today - anniversary_date).days

    if days_together < 0:
        days_together = 0

    # Next anniversary (same day/month, next or current year)
    try:
        next_ann = anniversary_date.replace(year=today.year)
    except ValueError:
        # Feb 29 on non-leap year → Feb 28
        next_ann = anniversary_date.replace(year=today.year, day=28)

    if next_ann <= today:
        try:
            next_ann = anniversary_date.replace(year=today.year + 1)
        except ValueError:
            next_ann = anniversary_date.replace(year=today.year + 1, day=28)

    next_anniversary_in_days = (next_ann - today).days

    return {
        "days_together": days_together,
        "anniversary_date": anniversary_date,
        "next_anniversary_in_days": next_anniversary_in_days,
    }