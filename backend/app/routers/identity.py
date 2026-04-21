from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    UserCreate,
    UserUpdate,
    InviteRequest,
)
from app.services import auth_service
from app.middleware.auth import get_current_user, require_admin, require_editor

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    user = auth_service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    access_token = auth_service.create_access_token(user.id, user.role)
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        ),
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"data": {"logged_out": True}}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@router.get("/users", response_model=List[UserResponse])
def get_users(
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(User.is_active == True).all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users/invite", response_model=UserResponse)
def invite_user(
    request: InviteRequest,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    hashed_password = auth_service.hash_password("temp_password123")
    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        full_name=None,
        role=request.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_active=new_user.is_active,
    )


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UserUpdate,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.role is not None:
        user.role = request.role
    if request.is_active is not None:
        user.is_active = request.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


@router.delete("/users/{user_id}")
def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = False
    db.commit()
    
    return {"data": {"deleted": True}}