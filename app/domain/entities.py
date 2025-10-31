"""Domain entities for the Virtual Council Assistant."""

from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

from app.domain.value_objects import ProjectStatus


class Message(BaseModel):
    """Represents a user message received via Telegram."""

    content: str
    user_id: str
    chat_id: str
    message_id: Optional[int] = None
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    processed: bool = False

    model_config = {"frozen": False, "validate_assignment": True}

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()

    def mark_as_processed(self) -> None:
        """Mark the message as processed."""
        self.processed = True


class Project(BaseModel):
    """Represents a project in the system."""

    name: str
    description: str
    status: str = ProjectStatus.ACTIVE.value
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"frozen": False, "validate_assignment": True}

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate that description is not empty."""
        if not v or not v.strip():
            raise ValueError("Project description cannot be empty")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate project status."""
        valid_statuses = {status.value for status in ProjectStatus}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(sorted(valid_statuses))}")
        return v

    def update_description(self, description: str) -> None:
        """Update project description."""
        self.description = description
        self.updated_at = datetime.now(UTC)


class KnowledgeEntry(BaseModel):
    """Represents a knowledge base entry."""

    content: str
    source_message_id: UUID
    project_id: Optional[UUID] = None
    tags: list[str] = Field(default_factory=list)
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"frozen": False, "validate_assignment": True}

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError("Knowledge content cannot be empty")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and clean tags."""
        return [tag.strip().lower() for tag in v if tag.strip()]

    def add_tag(self, tag: str) -> None:
        """Add a tag to the knowledge entry."""
        clean_tag = tag.strip().lower()
        if clean_tag and clean_tag not in self.tags:
            self.tags.append(clean_tag)

    def link_to_project(self, project_id: UUID) -> None:
        """Link this knowledge entry to a project."""
        self.project_id = project_id
