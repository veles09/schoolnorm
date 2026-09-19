from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db.database import get_db
from app.db.models import SchoolMember, User
from app.schools.schemas import SchoolResponse, SchoolUpdateRequest


router = APIRouter(
    prefix="/api/schools",
    tags=["Школы"],
)


@router.get("/mine")
def my_schools(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memberships = (
        db.query(SchoolMember)
        .filter(
            SchoolMember.user_id == current_user.id
        )
        .all()
    )

    return [
        {
            "school_id": membership.school.id,
            "school_name": membership.school.name,
            "role": membership.role,
        }
        for membership in memberships
    ]


def get_my_school(
    current_user: User,
    db: Session,
):
    membership = (
        db.query(SchoolMember)
        .filter(
            SchoolMember.user_id == current_user.id
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=404,
            detail="Школа пользователя не найдена",
        )

    return membership.school


@router.get(
    "/my",
    response_model=SchoolResponse,
)
def get_my_school_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_my_school(current_user, db)


@router.put(
    "/my",
    response_model=SchoolResponse,
)
def update_my_school(
    data: SchoolUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    school = get_my_school(current_user, db)

    school.name = data.name
    school.short_name = data.short_name
    school.address = data.address
    school.region = data.region
    school.municipality = data.municipality

    db.commit()
    db.refresh(school)

    return school