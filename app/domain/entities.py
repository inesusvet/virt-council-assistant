"""Domain entities for the Virtual Council Assistant."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Message:
    """Represents a user message received via Telegram."""

    def __init__(
        self,
        content: str,
        user_id: str,
        chat_id: str,
        message_id: Optional[int] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        processed: bool = False,
    ):
        self.id = id or uuid4()
        self.content = content
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.created_at = created_at or datetime.utcnow()
        self.processed = processed

    def mark_as_processed(self) -> None:
        """Mark the message as processed."""
        self.processed = True


class Project:
    """Represents a project in the system."""

    def __init__(
        self,
        name: str,
        description: str,
        status: str = "active",
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.name = name
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_description(self, description: str) -> None:
        """Update project description."""
        self.description = description
        self.updated_at = datetime.utcnow()


class KnowledgeEntry:
    """Represents a knowledge base entry."""

    def __init__(
        self,
        content: str,
        source_message_id: UUID,
        project_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.content = content
        self.source_message_id = source_message_id
        self.project_id = project_id
        self.tags = tags or []
        self.created_at = created_at or datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the knowledge entry."""
        if tag not in self.tags:
            self.tags.append(tag)

    def link_to_project(self, project_id: UUID) -> None:
        """Link this knowledge entry to a project."""
        self.project_id = project_id
