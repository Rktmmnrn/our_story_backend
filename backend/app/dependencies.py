# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from jose import JWTError

from app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Récupère l'utilisateur courant à partir du JWT token.
    """
    if not token:
        return None
    
    try:
        payload = decode_token(token)
        if not payload:
            return None
        
        user_id: str = payload.get("sub")
        if not user_id:
            return None
        
        # Vérifier le type de token
        if payload.get("type") != "access":
            return None
        
        # Récupérer l'utilisateur
        user_query = await db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = user_query.scalar_one_or_none()
        
        return user
        
    except (JWTError, ValueError):
        return None

async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Vérifie que l'utilisateur est authentifié et actif.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email non vérifié"
        )
    
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Vérifie que l'utilisateur a vérifié son email.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email non vérifié"
        )
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Vérifie que l'utilisateur a le rôle admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis"
        )
    return current_user

# Dépendance optionnelle pour les endpoints publics/privés
async def get_optional_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    """
    Récupère l'utilisateur si authentifié, sinon None.
    Utile pour les endpoints qui fonctionnent avec ou sans authentification.
    """
    return current_user