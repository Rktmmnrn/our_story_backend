"""
Auth router: /api/v1/auth
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.services import auth_service
from app.utils.file_manager import InvalidMimeType, save_upload, validate_photo

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    email: str,
    password: str,
    display_name: str,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.register_user(db, email, password, display_name)
    return {
        "data": {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
        },
        "message": "Compte créé avec succès",
    }


@router.post("/login")
async def login(
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    tokens = await auth_service.login_user(db, email, password)
    return {"data": tokens, "message": "Connexion réussie"}


@router.post("/refresh")
async def refresh(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    tokens = await auth_service.refresh_tokens(db, refresh_token)
    return {"data": tokens, "message": "Tokens renouvelés"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    await auth_service.logout_user(db, refresh_token)


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return {
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "display_name": current_user.display_name,
            "avatar_url": current_user.avatar_url,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
        },
        "message": "success",
    }


@router.patch("/me")
async def update_me(
    display_name: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.crud.user import crud_user
    from app.schemas.user import UserUpdate

    obj_in = UserUpdate(display_name=display_name)
    user = await crud_user.update(db, current_user, obj_in)
    return {"data": {"display_name": user.display_name}, "message": "Profil mis à jour"}


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.crud.user import crud_user

    try:
        validate_photo(file)
    except InvalidMimeType as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))

    file_path, _ = await save_upload(file, "photo")

    user = await crud_user.set_avatar(db, current_user, f"/api/v1/media/file/{file_path}")
    return {"data": {"avatar_url": user.avatar_url}, "message": "Avatar mis à jour"}