"""Database models using SQLAlchemy."""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class MessageModel(Base):
    """Database model for messages."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(100), nullable=False)
    message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ProjectModel(Base):
    """Database model for projects."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    knowledge_entries: Mapped[list["KnowledgeEntryModel"]] = relationship(
        "KnowledgeEntryModel", back_populates="project"
    )


class KnowledgeEntryModel(Base):
    """Database model for knowledge base entries."""

    __tablename__ = "knowledge_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("messages.id"), nullable=False
    )
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=True
    )
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    project: Mapped[Optional["ProjectModel"]] = relationship(
        "ProjectModel", back_populates="knowledge_entries"
    )
