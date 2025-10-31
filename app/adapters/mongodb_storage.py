"""MongoDB repository implementations."""

from typing import Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities import Message, Project, KnowledgeEntry
from app.domain.repositories import (
    MessageRepository,
    ProjectRepository,
    KnowledgeRepository,
)
from app.domain.value_objects import ProjectStatus


class MongoMessageRepository(MessageRepository):
    """MongoDB implementation of MessageRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.messages

    async def save(self, message: Message) -> Message:
        """Save a message to the database."""
        # Use Pydantic's model_dump to serialize
        document = message.model_dump(mode="json")
        document["_id"] = str(message.id)
        document.pop("id", None)  # Remove id field, use _id instead

        await self.collection.replace_one({"_id": document["_id"]}, document, upsert=True)
        return message

    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """Retrieve a message by ID."""
        document = await self.collection.find_one({"_id": str(message_id)})
        if not document:
            return None
        return self._to_entity(document)

    async def get_unprocessed(self, limit: int = 10) -> list[Message]:
        """Get unprocessed messages."""
        cursor = self.collection.find({"processed": False}).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [self._to_entity(doc) for doc in documents]

    async def mark_as_processed(self, message_id: UUID) -> None:
        """Mark a message as processed."""
        await self.collection.update_one({"_id": str(message_id)}, {"$set": {"processed": True}})

    @staticmethod
    def _to_entity(document: dict) -> Message:
        """Convert database document to domain entity using Pydantic validation."""
        # Map _id back to id for Pydantic model
        document["id"] = document.pop("_id")
        return Message.model_validate(document)


class MongoProjectRepository(ProjectRepository):
    """MongoDB implementation of ProjectRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.projects

    async def save(self, project: Project) -> Project:
        """Save a project to the database."""
        # Use Pydantic's model_dump to serialize
        document = project.model_dump(mode="json")
        document["_id"] = str(project.id)
        document.pop("id", None)  # Remove id field, use _id instead

        await self.collection.replace_one({"_id": document["_id"]}, document, upsert=True)
        return project

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Retrieve a project by ID."""
        document = await self.collection.find_one({"_id": str(project_id)})
        if not document:
            return None
        return self._to_entity(document)

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

    @staticmethod
    def _to_entity(document: dict) -> Project:
        """Convert database document to domain entity using Pydantic validation."""
        # Map _id back to id for Pydantic model
        document["id"] = document.pop("_id")
        return Project.model_validate(document)


class MongoKnowledgeRepository(KnowledgeRepository):
    """MongoDB implementation of KnowledgeRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.knowledge_entries

    async def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Save a knowledge entry to the database."""
        # Use Pydantic's model_dump to serialize
        document = entry.model_dump(mode="json")
        document["_id"] = str(entry.id)
        document.pop("id", None)  # Remove id field, use _id instead

        await self.collection.replace_one({"_id": document["_id"]}, document, upsert=True)
        return entry

    async def get_by_id(self, entry_id: UUID) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID."""
        document = await self.collection.find_one({"_id": str(entry_id)})
        if not document:
            return None
        return self._to_entity(document)

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

    @staticmethod
    def _to_entity(document: dict) -> KnowledgeEntry:
        """Convert database document to domain entity using Pydantic validation."""
        # Map _id back to id for Pydantic model
        document["id"] = document.pop("_id")
        return KnowledgeEntry.model_validate(document)
