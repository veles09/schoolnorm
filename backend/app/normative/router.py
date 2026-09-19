from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
from app.normative.models import NormativeDocument, VkPost, NormativeStatus

from app.db.database import get_db
from app.core.config import settings
from app.auth.security import get_current_user # Импортируем зависимость авторизации
from app.users.models import User # Предполагаем, что модель User существует

router = APIRouter(prefix="/api/normative", tags=["Normative Documents"])

# Простая проверка на супер-админа (по email или флагу в БД)
# Временно считаем супер-админом пользователя с конкретным email или первым пользователем
def get_superadmin(current_user: User = Depends(get_current_user)):
    # ЗАМЕНИТЕ email на ваш реальный email супер-админа
    SUPERADMIN_EMAIL = "velesiz00@gmail.com" 
    
    if current_user.email != SUPERADMIN_EMAIL and not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=403, detail="Требуется права супер-админа")
    return current_user

@router.post("/upload")
async def upload_normative_document(
    title: str = Form(...),
    doc_number: Optional[str] = Form(None),
    source_name: Optional[str] = Form(None),
    official_url: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_superadmin)
):
    """Загрузка нового нормативного документа (только супер-админ)"""
    
    file_path = None
    
    # Загрузка файла в MinIO если есть
    if file:
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=f"http://{settings.minio_endpoint}",
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                use_ssl=False
            )
            
            file_extension = file.filename.split(".")[-1] if file.filename else "doc"
            object_name = f"normative/{datetime.utcnow().strftime('%Y/%m')}/{file.filename}"
            
            # Читаем файл в память
            file_content = await file.read()
            
            s3_client.put_object(
                Bucket=settings.minio_bucket,
                Key=object_name,
                Body=file_content,
                ContentType=file.content_type or "application/octet-stream"
            )
            file_path = object_name
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")

    new_doc = NormativeDocument(
        title=title,
        doc_number=doc_number,
        source_name=source_name,
        official_url=official_url,
        summary=summary,
        file_path=file_path,
        status=NormativeStatus.DRAFT
    )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return {"id": new_doc.id, "message": "Документ загружен", "status": new_doc.status}

@router.get("/")
async def get_normative_documents(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Доступно всем авторизованным для просмотра
):
    """Получение списка нормативных документов"""
    
    query = db.query(NormativeDocument)
    
    if status:
        query = query.filter(NormativeDocument.status == status)
        
    docs = query.order_by(NormativeDocument.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": d.id,
            "title": d.title,
            "doc_number": d.doc_number,
            "source_name": d.source_name,
            "status": d.status,
            "is_important": d.is_important,
            "created_at": d.created_at
        }
        for d in docs
    ]

@router.post("/{doc_id}/vk-draft")
async def create_vk_draft(
    doc_id: int,
    post_message: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_superadmin)
):
    """Создание черновика поста для VK"""
    
    doc = db.query(NormativeDocument).filter(NormativeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    draft = VkPost(
        normative_document_id=doc_id,
        post_message=post_message,
        attachment_link=f"/normative/{doc_id}", # Ссылка на страницу документа
        is_sent=False
    )
    
    db.add(draft)
    db.commit()
    db.refresh(draft)
    
    return {"id": draft.id, "message": "Черновик создан"}

@router.post("/vk-send/{post_id}")
async def send_vk_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_superadmin)
):
    """Отправка поста в VK (заглушка для реализации API VK)"""
    
    post = db.query(VkPost).filter(VkPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    if post.is_sent:
        raise HTTPException(status_code=400, detail="Пост уже отправлен")
    
    # --- ЗДЕСЬ БУДЕТ ЛОГИКА ОТРАВКИ В VK API ---
    # Сейчас просто имитируем успешную отправку
    print(f"Sending to VK: {post.post_message}")
    print(f"Link: {post.attachment_link}")
    
    # Имитация успеха
    post.is_sent = True
    post.sent_at = datetime.utcnow()
    post.vk_post_id = "mock_vk_id_12345"
    
    db.commit()
    
    return {"message": "Пост успешно отправлен в VK", "vk_id": post.vk_post_id}