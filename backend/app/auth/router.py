from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.schemas import (
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TokenResponse,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.db.models import School, SchoolMember, User


router = APIRouter(
    prefix="/api/auth",
    tags=["Авторизация"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
    )

    db.add(user)
    db.flush()

    school = School(
        name=data.school_name,
    )

    db.add(school)
    db.flush()

    membership = SchoolMember(
        user_id=user.id,
        school_id=school.id,
        role="DIRECTOR",
    )

    db.add(membership)

    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Пользователь заблокирован",
        )

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
    )


@router.get(
    "/me",
    response_model=MeResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
    )