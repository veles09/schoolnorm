from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base

class NormativeStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REPEALED = "repealed"
    ARCHIVED = "archived"

class NormativeDocument(Base):
    __tablename__ = "normative_documents"
    
    # Добавляем этот аргумент, чтобы избежать ошибки повторного определения
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    
    # Основные данные
    title = Column(String(500), nullable=False, index=True)
    doc_number = Column(String(100), nullable=True) # Номер документа
    doc_date = Column(DateTime, nullable=True) # Дата документа
    
    # Источник
    source_name = Column(String(255), nullable=True) # Например: Минпросвещения
    official_url = Column(String(1000), nullable=True) # Ссылка на источник
    
    # Контент
    summary = Column(Text, nullable=True) # Краткое описание (для VK/рассылки)
    full_text = Column(Text, nullable=True) # Полный текст (для поиска и ИИ)
    file_path = Column(String(500), nullable=True) # Путь к файлу в MinIO
    
    # Статус и метаданные
    status = Column(SQLEnum(NormativeStatus), default=NormativeStatus.DRAFT)
    is_important = Column(Boolean, default=False) # Флаг важности для школы
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VkPost(Base):
    __tablename__ = "vk_posts"
    
    # Добавляем этот аргумент
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    
    normative_document_id = Column(Integer, ForeignKey("normative_documents.id"), nullable=False)
    group_id = Column(String(100), nullable=True) # ID группы VK
    post_message = Column(Text, nullable=False) # Текст поста
    attachment_link = Column(String(1000), nullable=True) # Ссылка на документ
    
    vk_post_id = Column(String(100), nullable=True) # ID созданного поста в VK
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("NormativeDocument")