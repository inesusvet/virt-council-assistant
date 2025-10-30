"""MongoDB repository implementations."""

from typing import Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities import Message, Project, KnowledgeEntry
from app.domain.repositories import MessageRepository, ProjectRepository, KnowledgeRepository


class MongoMessageRepository(MessageRepository):
    """MongoDB implementation of MessageRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.messages

    async def save(self, message: Message) -> Message:
        """Save a message to the database."""
        document = {
            "_id": str(message.id),
            "content": message.content,
            "user_id": message.user_id,
            "chat_id": message.chat_id,
            "message_id": message.message_id,
            "created_at": message.created_at,
            "processed": message.processed,
        }
        await self.collection.replace_one({"_id": str(message.id)}, document, upsert=True)
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
        """Convert database document to domain entity."""
        return Message(
            id=UUID(document["_id"]),
            content=document["content"],
            user_id=document["user_id"],
            chat_id=document["chat_id"],
            message_id=document.get("message_id"),
            created_at=document["created_at"],
            processed=document["processed"],
        )


class MongoProjectRepository(ProjectRepository):
    """MongoDB implementation of ProjectRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.projects

    async def save(self, project: Project) -> Project:
        """Save a project to the database."""
        document = {
            "_id": str(project.id),
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }
        await self.collection.replace_one({"_id": str(project.id)}, document, upsert=True)
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
        cursor = self.collection.find({"status": "active"})
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    async def search(self, query: str) -> list[Project]:
        """Search projects by name or description using text search."""
        cursor = self.collection.find({"$text": {"$search": query}})
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    @staticmethod
    def _to_entity(document: dict) -> Project:
        """Convert database document to domain entity."""
        return Project(
            id=UUID(document["_id"]),
            name=document["name"],
            description=document["description"],
            status=document["status"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )


class MongoKnowledgeRepository(KnowledgeRepository):
    """MongoDB implementation of KnowledgeRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.knowledge_entries

    async def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Save a knowledge entry to the database."""
        document = {
            "_id": str(entry.id),
            "content": entry.content,
            "source_message_id": str(entry.source_message_id),
            "project_id": str(entry.project_id) if entry.project_id else None,
            "tags": entry.tags,
            "created_at": entry.created_at,
        }
        await self.collection.replace_one({"_id": str(entry.id)}, document, upsert=True)
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
        """Convert database document to domain entity."""
        return KnowledgeEntry(
            id=UUID(document["_id"]),
            content=document["content"],
            source_message_id=UUID(document["source_message_id"]),
            project_id=UUID(document["project_id"]) if document.get("project_id") else None,
            tags=document.get("tags", []),
            created_at=document["created_at"],
        )
