"""
Special dates router: /api/v1/dates
"""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_couple, get_current_user, get_db

router = APIRouter(prefix="/dates", tags=["Dates Spéciales"])


@router.get("/")
async def list_dates(
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.special_date import crud_special_date

    dates = await crud_special_date.list_by_couple(db, couple.id)
    return {
        "data": [
            {
                "id": str(d.id),
                "title": d.title,
                "event_date": d.event_date,
                "description": d.description,
                "emoji": d.emoji,
                "created_at": d.created_at,
            }
            for d in dates
        ],
        "message": "success",
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_date(
    title: str,
    event_date: date,
    description: str | None = None,
    emoji: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    couple=Depends(get_current_couple),
):
    from app.crud.special_date import crud_special_date
    from app.schemas.special_date import SpecialDateCreate

    obj_in = SpecialDateCreate(
        title=title, event_date=event_date,
        description=description, emoji=emoji
    )
    special_date = await crud_special_date.create(db, couple.id, current_user.id, obj_in)
    return {
        "data": {"id": str(special_date.id), "title": special_date.title},
        "message": "Date ajoutée",
    }


@router.get("/{date_id}")
async def get_date(
    date_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.special_date import crud_special_date

    d = await crud_special_date.get_by_id(db, date_id)
    if not d or d.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Date introuvable")

    return {
        "data": {
            "id": str(d.id), "title": d.title, "event_date": d.event_date,
            "description": d.description, "emoji": d.emoji, "created_at": d.created_at,
        },
        "message": "success",
    }


@router.patch("/{date_id}")
async def update_date(
    date_id: UUID,
    title: str | None = None,
    event_date: date | None = None,
    description: str | None = None,
    emoji: str | None = None,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.special_date import crud_special_date
    from app.schemas.special_date import SpecialDateUpdate

    d = await crud_special_date.get_by_id(db, date_id)
    if not d or d.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Date introuvable")

    obj_in = SpecialDateUpdate(title=title, event_date=event_date, description=description, emoji=emoji)
    updated = await crud_special_date.update(db, d, obj_in)
    return {"data": {"id": str(updated.id)}, "message": "Date mise à jour"}


@router.delete("/{date_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_date(
    date_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.special_date import crud_special_date

    d = await crud_special_date.get_by_id(db, date_id)
    if not d or d.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Date introuvable")

    await crud_special_date.delete(db, d)