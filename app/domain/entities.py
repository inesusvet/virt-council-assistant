"""Domain entities for the Virtual Council Assistant."""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Message:
    """Represents a user message received via Telegram."""

    content: str
    user_id: str
    chat_id: str
    message_id: Optional[int] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed: bool = False

    def mark_as_processed(self) -> None:
        """Mark the message as processed."""
        self.processed = True


@dataclass
class Project:
    """Represents a project in the system."""

    name: str
    description: str
    status: str = "active"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def update_description(self, description: str) -> None:
        """Update project description."""
        self.description = description
        self.updated_at = datetime.now(UTC)


@dataclass
class KnowledgeEntry:
    """Represents a knowledge base entry."""

    content: str
    source_message_id: UUID
    project_id: Optional[UUID] = None
    tags: list[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_tag(self, tag: str) -> None:
        """Add a tag to the knowledge entry."""
        if tag not in self.tags:
            self.tags.append(tag)

    def link_to_project(self, project_id: UUID) -> None:
        """Link this knowledge entry to a project."""
        self.project_id = project_id
