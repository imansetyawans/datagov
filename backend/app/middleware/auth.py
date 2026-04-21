from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services import auth_service
from app.models import User

security = HTTPBearer()


class RBAC:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        token = credentials.credentials
        
        try:
            payload = auth_service.decode_token(token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        if self.allowed_roles and role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' not allowed to access this resource",
            )
        
        user = auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        
        return user


def get_current_user() -> User:
    """Get current authenticated user (any role)."""
    return RBAC(allowed_roles=[])


def require_admin() -> User:
    """Require admin role."""
    return RBAC(allowed_roles=["admin"])


def require_editor() -> User:
    """Require editor or admin role."""
    return RBAC(allowed_roles=["admin", "editor"])


def require_viewer() -> User:
    """Require any authenticated user (viewer, editor, or admin)."""
    return RBAC(allowed_roles=["admin", "editor", "viewer"])