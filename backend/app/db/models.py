from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    memberships: Mapped[list["SchoolMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(1000))
    region: Mapped[str | None] = mapped_column(String(255))
    municipality: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    members: Mapped[list["SchoolMember"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )
    documents: Mapped[list["SchoolDocument"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )


class SchoolMember(Base):
    __tablename__ = "school_members"
    __table_args__ = (UniqueConstraint("user_id", "school_id", name="uq_school_members_user_school"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="DIRECTOR", nullable=False)

    user: Mapped[User] = relationship(back_populates="memberships")
    school: Mapped[School] = relationship(back_populates="members")


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    storage_key: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    original_name: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class DocumentTag(Base):
    __tablename__ = "document_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SchoolDocument(Base):
    __tablename__ = "school_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    number: Mapped[str | None] = mapped_column(String(255))
    document_date: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    file_id: Mapped[int | None] = mapped_column(ForeignKey("files.id", ondelete="SET NULL"))
    text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    school: Mapped[School] = relationship(back_populates="documents")
    tags: Mapped[list["SchoolDocumentTag"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class SchoolDocumentTag(Base):
    __tablename__ = "school_document_tags"
    __table_args__ = (UniqueConstraint("school_document_id", "tag_id", name="uq_school_document_tags_document_tag"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    school_document_id: Mapped[int] = mapped_column(
        ForeignKey("school_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("document_tags.id", ondelete="CASCADE"), nullable=False, index=True
    )

    document: Mapped[SchoolDocument] = relationship(back_populates="tags")
    tag: Mapped[DocumentTag] = relationship()
