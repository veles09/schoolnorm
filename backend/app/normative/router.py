from hashlib import sha256
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.normative.models import NormativeDocument, NormativeStatus, VkPost
from app.storage.minio import upload_file

router = APIRouter(prefix="/api/normative", tags=["Normative Documents"])
MAX_FILE_SIZE = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}


def get_superadmin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права супер-админа")
    return current_user


def _validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=422, detail="official_url должен быть абсолютным HTTP(S)-адресом")
    return value


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_normative_document(
    title: str = Form(..., min_length=1, max_length=500),
    doc_number: Optional[str] = Form(None, max_length=100),
    source_name: str = Form(..., min_length=1, max_length=255),
    official_url: str = Form(..., max_length=1000),
    summary: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_superadmin),
):
    _validate_url(official_url)
    content = b""
    file_path = None
    if file:
        suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=415, detail="Недопустимый тип файла")
        content = await file.read(MAX_FILE_SIZE + 1)
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Файл превышает лимит 25 МБ")
        file_path = upload_file(content, file.filename or "document", file.content_type or "application/octet-stream", "normative")

    digest = sha256(content if content else f"{title}|{official_url}".encode()).hexdigest()
    doc = NormativeDocument(
        title=title.strip(), doc_number=doc_number, source_name=source_name.strip(),
        official_url=official_url, summary=summary, file_path=file_path,
        content_hash=digest, processing_status="received", status=NormativeStatus.DRAFT,
    )
    db.add(doc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Документ с таким содержимым уже существует")
    db.refresh(doc)
    return {"id": doc.id, "message": "Документ загружен", "status": doc.status.value}


@router.get("/")
def get_normative_documents(
    skip: int = 0, limit: int = 20, status: Optional[NormativeStatus] = None,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    skip = max(skip, 0)
    limit = min(max(limit, 1), 100)
    query = db.query(NormativeDocument)
    if status:
        query = query.filter(NormativeDocument.status == status)
    return query.order_by(NormativeDocument.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/{doc_id}/vk-draft", status_code=status.HTTP_201_CREATED)
def create_vk_draft(
    doc_id: int, post_message: str = Body(..., embed=True, min_length=1, max_length=4096),
    db: Session = Depends(get_db), _: User = Depends(get_superadmin),
):
    doc = db.get(NormativeDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    draft = VkPost(normative_document_id=doc_id, post_message=post_message.strip(), attachment_link=doc.official_url)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return {"id": draft.id, "message": "Черновик создан"}


@router.post("/vk-send/{post_id}")
def send_vk_post(post_id: int, db: Session = Depends(get_db), _: User = Depends(get_superadmin)):
    post = db.get(VkPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    if post.is_sent:
        raise HTTPException(status_code=409, detail="Пост уже отправлен")
    raise HTTPException(status_code=501, detail="VK-интеграция не настроена: отправка отключена")
