"""
Couple router: /api/v1/couple
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.dependencies import get_current_couple, get_current_user, get_db
from app.services import couple_service

router = APIRouter(prefix="/couple", tags=["Couple"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_couple(
    anniversary_date: date,
    couple_name: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    couple = await couple_service.create_couple(
        db, current_user.id, anniversary_date, couple_name
    )
    return {"data": {"id": str(couple.id), "anniversary_date": couple.anniversary_date}, "message": "Couple créé"}


@router.get("/")
async def get_couple(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    couple=Depends(get_current_couple),
):
    return {
        "data": {
            "id": str(couple.id),
            "couple_name": couple.couple_name,
            "anniversary_date": couple.anniversary_date,
            "user1_id": str(couple.user1_id),
            "user2_id": str(couple.user2_id) if couple.user2_id else None,
            "is_active": couple.is_active,
            "created_at": couple.created_at,
        },
        "message": "success",
    }


@router.patch("/")
async def update_couple(
    anniversary_date: date | None = None,
    couple_name: str | None = None,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.couple import crud_couple
    from app.schemas.couple import CoupleUpdate

    obj_in = CoupleUpdate(anniversary_date=anniversary_date, couple_name=couple_name)
    updated = await crud_couple.update(db, couple, obj_in)
    return {"data": {"couple_name": updated.couple_name, "anniversary_date": updated.anniversary_date}, "message": "Couple mis à jour"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def dissolve_couple(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    couple=Depends(get_current_couple),
):
    if couple.user1_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le créateur du couple peut le dissoudre",
        )
    from app.crud.couple import crud_couple
    await crud_couple.dissolve(db, couple)


@router.post("/invite")
async def invite_partner(
    recipient_email: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    couple=Depends(get_current_couple),
):
    result = await couple_service.send_couple_invite(
        db, couple.id, current_user.id, recipient_email
    )
    return {"data": result, "message": "Invitation envoyée"}


@router.post("/join/{token}")
async def join_couple(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    couple = await couple_service.join_couple_by_token(db, token, current_user.id)
    return {"data": {"id": str(couple.id)}, "message": "Vous avez rejoint le couple ♡"}


@router.get("/timer")
async def get_timer(couple=Depends(get_current_couple)):
    result = couple_service.compute_timer(couple.anniversary_date)
    return {"data": result, "message": "success"}