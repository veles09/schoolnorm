from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import SchoolMember


def get_school_member(
    db: Session,
    user_id: int,
    school_id: int,
) -> SchoolMember:
    member = (
        db.query(SchoolMember)
        .filter(
            SchoolMember.user_id == user_id,
            SchoolMember.school_id == school_id,
        )
        .first()
    )

    if member is None:
        raise HTTPException(
            status_code=403,
            detail="Нет доступа к этой школе",
        )

    return member


def require_director(member: SchoolMember) -> None:
    if member.role != "DIRECTOR":
        raise HTTPException(
            status_code=403,
            detail="Требуются права директора",
        )