"""
Quotes router: /api/v1/quotes
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_couple, get_current_user, get_db

router = APIRouter(prefix="/quotes", tags=["Citations"])


@router.get("/")
async def list_quotes(
    favorites_only: bool = False,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.quote import crud_quote

    quotes = await crud_quote.list_by_couple(db, couple.id, favorites_only=favorites_only)
    return {
        "data": [
            {
                "id": str(q.id),
                "text": q.text,
                "author": q.author,
                "is_favorite": q.is_favorite,
                "created_at": q.created_at,
            }
            for q in quotes
        ],
        "message": "success",
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_quote(
    text: str,
    author: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    couple=Depends(get_current_couple),
):
    from app.crud.quote import crud_quote
    from app.schemas.quote import QuoteCreate

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La citation ne peut pas être vide",
        )

    obj_in = QuoteCreate(text=text, author=author)
    quote = await crud_quote.create(db, couple.id, current_user.id, obj_in)
    return {
        "data": {"id": str(quote.id), "text": quote.text},
        "message": "Citation ajoutée",
    }


@router.patch("/{quote_id}")
async def update_quote(
    quote_id: UUID,
    text: str | None = None,
    author: str | None = None,
    is_favorite: bool | None = None,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.quote import crud_quote
    from app.schemas.quote import QuoteUpdate

    q = await crud_quote.get_by_id(db, quote_id)
    if not q or q.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Citation introuvable")

    obj_in = QuoteUpdate(text=text, author=author, is_favorite=is_favorite)
    updated = await crud_quote.update(db, q, obj_in)
    return {"data": {"id": str(updated.id), "is_favorite": updated.is_favorite}, "message": "Citation mise à jour"}


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(
    quote_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.quote import crud_quote

    q = await crud_quote.get_by_id(db, quote_id)
    if not q or q.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Citation introuvable")

    await crud_quote.delete(db, q)