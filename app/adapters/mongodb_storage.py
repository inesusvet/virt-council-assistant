"""MongoDB repository implementations."""

from typing import Optional, Type
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities import Message, Project, KnowledgeEntry
from app.domain.repositories import (
    MessageRepository,
    ProjectRepository,
    KnowledgeRepository,
)
from app.domain.value_objects import ProjectStatus
from app.adapters.base_repositories import MongoBaseRepository


class MongoMessageRepository(MongoBaseRepository[Message], MessageRepository):
    """MongoDB implementation of MessageRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "messages")

    @property
    def entity_class(self) -> Type[Message]:
        """Return the Message entity class."""
        return Message

    async def save(self, message: Message) -> Message:
        """Save a message to the database."""
        return await self._save(message)

    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """Retrieve a message by ID."""
        return await self._get_by_id(message_id)

    async def get_unprocessed(self, limit: int = 10) -> list[Message]:
        """Get unprocessed messages."""
        cursor = self.collection.find({"processed": False}).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in documents]

    async def mark_as_processed(self, message_id: UUID) -> None:
        """Mark a message as processed."""
        await self.collection.update_one({"_id": str(message_id)}, {"$set": {"processed": True}})


class MongoProjectRepository(MongoBaseRepository[Project], ProjectRepository):
    """MongoDB implementation of ProjectRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "projects")

    @property
    def entity_class(self) -> Type[Project]:
        """Return the Project entity class."""
        return Project

    async def save(self, project: Project) -> Project:
        """Save a project to the database."""
        return await self._save(project)

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Retrieve a project by ID."""
        return await self._get_by_id(project_id)

    async def get_by_name(self, name: str) -> Optional[Project]:
        """Retrieve a project by name."""
        document = await self.collection.find_one({"name": name})
        if not document:
            return None
        return self._to_entity(document)

    async def get_all_active(self) -> list[Project]:
        """Get all active projects."""
        cursor = self.collection.find({"status": ProjectStatus.ACTIVE.value})
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    async def search(self, query: str) -> list[Project]:
        """Search projects by name or description using text search."""
        cursor = self.collection.find({"$text": {"$search": query}})
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]


class MongoKnowledgeRepository(MongoBaseRepository[KnowledgeEntry], KnowledgeRepository):
    """MongoDB implementation of KnowledgeRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "knowledge_entries")

    @property
    def entity_class(self) -> Type[KnowledgeEntry]:
        """Return the KnowledgeEntry entity class."""
        return KnowledgeEntry

    async def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Save a knowledge entry to the database."""
        return await self._save(entry)

    async def get_by_id(self, entry_id: UUID) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID."""
        return await self._get_by_id(entry_id)

    async def get_by_project(self, project_id: UUID) -> list[KnowledgeEntry]:
        """Get all knowledge entries for a project."""
        cursor = self.collection.find({"project_id": str(project_id)})
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    async def search(self, query: str, limit: int = 10) -> list[KnowledgeEntry]:
        """Search knowledge base entries using text search."""
        cursor = self.collection.find({"$text": {"$search": query}}).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in documents]
