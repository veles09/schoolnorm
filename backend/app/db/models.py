from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.database import Base


# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    memberships = relationship(
        "SchoolMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ============================================================
# ШКОЛЫ
# ============================================================

class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    short_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    region: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    municipality: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    members = relationship(
        "SchoolMember",
        back_populates="school",
        cascade="all, delete-orphan",
    )

    documents = relationship(
        "SchoolDocument",
        back_populates="school",
        cascade="all, delete-orphan",
    )


# ============================================================
# УЧАСТНИКИ ШКОЛЫ
# ============================================================

class SchoolMember(Base):
    __tablename__ = "school_members"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="DIRECTOR",
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="memberships",
    )

    school = relationship(
        "School",
        back_populates="members",
    )


# ============================================================
# ФАЙЛЫ
# ============================================================

class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    storage_key: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    original_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    size: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# ИСТОЧНИКИ НОРМАТИВКИ
# ============================================================

class NormativeSource(Base):
    __tablename__ = "normative_sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    documents = relationship(
        "NormativeDocument",
        back_populates="source",
    )


# ============================================================
# НОРМАТИВНЫЕ ДОКУМЕНТЫ
# ============================================================

class NormativeDocument(Base):
    __tablename__ = "normative_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("normative_sources.id"),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    document_number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    document_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    publication_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    effective_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
    )

    official_url: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    file_id: Mapped[int | None] = mapped_column(
        ForeignKey("files.id"),
        nullable=True,
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    source = relationship(
        "NormativeSource",
        back_populates="documents",
    )


# ============================================================
# ВЕРСИИ НОРМАТИВНОГО ДОКУМЕНТА
# ============================================================

class NormativeVersion(Base):
    __tablename__ = "normative_versions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    normative_document_id: Mapped[int] = mapped_column(
        ForeignKey("normative_documents.id"),
        nullable=False,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    effective_from: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    file_id: Mapped[int | None] = mapped_column(
        ForeignKey("files.id"),
        nullable=True,
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    change_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# ДОКУМЕНТЫ ШКОЛЫ / ЛНА
# ============================================================

class SchoolDocument(Base):
    __tablename__ = "school_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id"),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    document_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
    )

    file_id: Mapped[int | None] = mapped_column(
        ForeignKey("files.id"),
        nullable=True,
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    school = relationship(
        "School",
        back_populates="documents",
    )