from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class NormativeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REPEALED = "repealed"
    ARCHIVED = "archived"


class NormativeDocument(Base):
    __tablename__ = "normative_documents"
    __table_args__ = (
        UniqueConstraint("source_name", "external_id", name="uq_normative_source_external_id"),
        UniqueConstraint("content_hash", name="uq_normative_content_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    doc_number: Mapped[str | None] = mapped_column(String(100))
    doc_date: Mapped[datetime | None] = mapped_column(DateTime)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    official_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    full_text: Mapped[str | None] = mapped_column(Text)
    file_path: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[NormativeStatus] = mapped_column(default=NormativeStatus.DRAFT, nullable=False)
    is_relevant: Mapped[bool | None] = mapped_column(Boolean)
    document_type: Mapped[str | None] = mapped_column(String(30))
    filter_confidence: Mapped[float | None] = mapped_column(Float)
    processing_status: Mapped[str] = mapped_column(String(30), default="received", nullable=False, index=True)
    processing_error: Mapped[str | None] = mapped_column(Text)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tags: Mapped[list["NormativeDocumentTag"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    vk_posts: Mapped[list["VkPost"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class NormativeDocumentTag(Base):
    __tablename__ = "normative_document_tags"
    __table_args__ = (UniqueConstraint("normative_document_id", "tag_id", name="uq_normative_document_tags_document_tag"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    normative_document_id: Mapped[int] = mapped_column(ForeignKey("normative_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("document_tags.id", ondelete="CASCADE"), nullable=False, index=True)

    document: Mapped[NormativeDocument] = relationship(back_populates="tags")
    tag: Mapped["DocumentTag"] = relationship()


class VkPost(Base):
    __tablename__ = "vk_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    normative_document_id: Mapped[int] = mapped_column(ForeignKey("normative_documents.id", ondelete="CASCADE"), nullable=False)
    group_id: Mapped[str | None] = mapped_column(String(100))
    post_message: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_link: Mapped[str | None] = mapped_column(String(1000))
    vk_post_id: Mapped[str | None] = mapped_column(String(100))
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document: Mapped[NormativeDocument] = relationship(back_populates="vk_posts")
