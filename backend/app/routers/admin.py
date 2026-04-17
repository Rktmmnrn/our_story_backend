"""
Admin router: /api/v1/admin
All endpoints require JWT with role == "admin".
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_admin
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stats = await admin_service.get_dashboard_stats(db)
    return {"data": stats, "message": "success"}


@router.get("/users")
async def list_users(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    from app.crud.user import crud_user

    skip = (page - 1) * per_page
    users = await crud_user.list_all(db, skip=skip, limit=per_page)
    total = await crud_user.count(db)
    return {
        "data": [
            {
                "id": str(u.id),
                "email": u.email,
                "display_name": u.display_name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "message": "success",
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    from app.crud.user import crud_user

    user = await crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    return {
        "data": {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
        "message": "success",
    }


@router.patch("/users/{user_id}")
async def update_user(
    user_id: UUID,
    is_active: bool | None = None,
    role: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin),
):
    from app.crud.user import crud_user
    from app.schemas.user import UserUpdate

    user = await crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    if role and role not in ("user", "admin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role invalide. Valeurs acceptées : 'user', 'admin'",
        )

    if is_active is not None:
        user.is_active = is_active
    if role is not None:
        user.role = role

    await db.flush()
    return {"data": {"id": str(user.id), "is_active": user.is_active, "role": user.role}, "message": "Utilisateur mis à jour"}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin),
):
    await admin_service.admin_delete_user(db, user_id, current_admin.id)


@router.get("/couples")
async def list_couples(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    from app.crud.couple import crud_couple

    skip = (page - 1) * per_page
    couples = await crud_couple.list_all(db, skip=skip, limit=per_page)
    total = await crud_couple.count(db)
    return {
        "data": [
            {
                "id": str(c.id),
                "couple_name": c.couple_name,
                "anniversary_date": c.anniversary_date,
                "user1_id": str(c.user1_id),
                "user2_id": str(c.user2_id) if c.user2_id else None,
                "is_active": c.is_active,
            }
            for c in couples
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "message": "success",
    }


@router.delete("/couples/{couple_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_couple(
    couple_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    await admin_service.admin_delete_couple(db, couple_id)


@router.get("/media")
async def list_all_media(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    from app.crud.media_item import crud_media_item

    skip = (page - 1) * per_page
    items = await crud_media_item.list_all(db, skip=skip, limit=per_page)
    total = await crud_media_item.count_all(db)
    return {
        "data": [
            {
                "id": str(i.id),
                "couple_id": str(i.couple_id),
                "media_type": i.media_type,
                "original_filename": i.original_filename,
                "file_size_bytes": i.file_size_bytes,
                "created_at": i.created_at,
            }
            for i in items
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "message": "success",
    }


@router.delete("/media/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_media(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    from app.crud.media_item import crud_media_item
    from app.utils.file_manager import delete_file

    item = await crud_media_item.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Média introuvable")

    file_path = await crud_media_item.delete(db, item)
    delete_file(file_path)