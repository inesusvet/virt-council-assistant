"""Repository interfaces for the Virtual Council Assistant."""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities import Message, Project, KnowledgeEntry


class MessageRepository(ABC):
    """Interface for message persistence."""

    @abstractmethod
    async def save(self, message: Message) -> Message:
        """Save a message to the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """Retrieve a message by ID."""
        pass

    @abstractmethod
    async def get_unprocessed(self, limit: int = 10) -> list[Message]:
        """Get unprocessed messages."""
        pass

    @abstractmethod
    async def mark_as_processed(self, message_id: UUID) -> None:
        """Mark a message as processed."""
        pass


class ProjectRepository(ABC):
    """Interface for project persistence."""

    @abstractmethod
    async def save(self, project: Project) -> Project:
        """Save a project to the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Retrieve a project by ID."""
        pass

    @abstractmethod
    async def get_all_active(self) -> list[Project]:
        """Get all active projects."""
        pass

    @abstractmethod
    async def search(self, query: str) -> list[Project]:
        """Search projects by name or description."""
        pass


class KnowledgeRepository(ABC):
    """Interface for knowledge base persistence."""

    @abstractmethod
    async def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Save a knowledge entry to the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, entry_id: UUID) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID."""
        pass

    @abstractmethod
    async def get_by_project(self, project_id: UUID) -> list[KnowledgeEntry]:
        """Get all knowledge entries for a project."""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[KnowledgeEntry]:
        """Search knowledge base entries."""
        pass
