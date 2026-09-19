from fastapi import (
    APIRouter,
    Depends,
    File as FastAPIFile,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db.database import get_db
from app.db.models import (
    File,
    SchoolDocument,
    SchoolMember,
    User,
)
from app.documents.schemas import (
    SchoolDocumentResponse,
)
from app.storage.minio import upload_file


router = APIRouter(
    prefix="/api/documents",
    tags=["Документы школы"],
)


@router.get(
    "/",
    response_model=list[SchoolDocumentResponse],
)
def get_documents(
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

    school_ids = [
        membership.school_id
        for membership in memberships
    ]

    if not school_ids:
        return []

    return (
        db.query(SchoolDocument)
        .filter(
            SchoolDocument.school_id.in_(school_ids)
        )
        .order_by(
            SchoolDocument.created_at.desc()
        )
        .all()
    )


@router.post(
    "/upload",
    response_model=SchoolDocumentResponse,
)
async def upload_document(
    document_type: str = Form(...),
    title: str = Form(...),
    number: str | None = Form(None),
    file: UploadFile = FastAPIFile(...),

    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = (
        db.query(SchoolMember)
        .filter(
            SchoolMember.user_id == current_user.id
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Пользователь не состоит в школе",
        )

    content = await file.read()

    storage_key = upload_file(
        content=content,
        original_name=file.filename or "document",
        content_type=file.content_type
        or "application/octet-stream",
        folder=f"school_documents/{membership.school_id}",
    )

    stored_file = File(
        storage_key=storage_key,
        original_name=file.filename or "document",
        mime_type=file.content_type,
        size=len(content),
    )

    db.add(stored_file)
    db.flush()

    document = SchoolDocument(
        school_id=membership.school_id,
        document_type=document_type,
        title=title,
        number=number,
        file_id=stored_file.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document