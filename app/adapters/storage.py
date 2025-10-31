"""SQLAlchemy repository implementations."""

import json
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Message, Project, KnowledgeEntry
from app.domain.repositories import MessageRepository, ProjectRepository, KnowledgeRepository
from app.infrastructure.database.models import MessageModel, ProjectModel, KnowledgeEntryModel


class SQLAlchemyMessageRepository(MessageRepository):
    """SQLAlchemy implementation of MessageRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: Message) -> Message:
        """Save a message to the database."""
        # Use Pydantic's model_dump to get field values
        data = message.model_dump()
        model = MessageModel(
            id=str(data["id"]),
            content=data["content"],
            user_id=data["user_id"],
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            created_at=data["created_at"],
            processed=data["processed"],
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """Retrieve a message by ID."""
        result = await self.session.execute(
            select(MessageModel).where(MessageModel.id == str(message_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_unprocessed(self, limit: int = 10) -> list[Message]:
        """Get unprocessed messages."""
        result = await self.session.execute(
            select(MessageModel).where(~MessageModel.processed).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def mark_as_processed(self, message_id: UUID) -> None:
        """Mark a message as processed."""
        result = await self.session.execute(
            select(MessageModel).where(MessageModel.id == str(message_id))
        )
        model = result.scalar_one_or_none()
        if model:
            model.processed = True
            await self.session.commit()

    @staticmethod
    def _to_entity(model: MessageModel) -> Message:
        """Convert database model to domain entity using Pydantic validation."""
        return Message.model_validate(
            {
                "id": model.id,
                "content": model.content,
                "user_id": model.user_id,
                "chat_id": model.chat_id,
                "message_id": model.message_id,
                "created_at": model.created_at,
                "processed": model.processed,
            }
        )


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of ProjectRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, project: Project) -> Project:
        """Save a project to the database."""
        # Use Pydantic's model_dump to get field values
        data = project.model_dump()

        # Check if project exists
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == str(data["id"]))
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.name = data["name"]
            existing.description = data["description"]
            existing.status = data["status"]
            existing.updated_at = data["updated_at"]
        else:
            # Create new
            model = ProjectModel(
                id=str(data["id"]),
                name=data["name"],
                description=data["description"],
                status=data["status"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            self.session.add(model)

        await self.session.commit()
        if existing:
            await self.session.refresh(existing)
            return self._to_entity(existing)
        else:
            await self.session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Retrieve a project by ID."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == str(project_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[Project]:
        """Retrieve a project by name."""
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.name == name))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_active(self) -> list[Project]:
        """Get all active projects."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.status == "active")
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def search(self, query: str) -> list[Project]:
        """Search projects by name or description."""
        search_term = f"%{query}%"
        result = await self.session.execute(
            select(ProjectModel).where(
                (ProjectModel.name.ilike(search_term))
                | (ProjectModel.description.ilike(search_term))
            )
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: ProjectModel) -> Project:
        """Convert database model to domain entity using Pydantic validation."""
        return Project.model_validate(
            {
                "id": model.id,
                "name": model.name,
                "description": model.description,
                "status": model.status,
                "created_at": model.created_at,
                "updated_at": model.updated_at,
            }
        )


class SQLAlchemyKnowledgeRepository(KnowledgeRepository):
    """SQLAlchemy implementation of KnowledgeRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Save a knowledge entry to the database."""
        # Use Pydantic's model_dump to get field values
        data = entry.model_dump()
        model = KnowledgeEntryModel(
            id=str(data["id"]),
            content=data["content"],
            source_message_id=str(data["source_message_id"]),
            project_id=str(data["project_id"]) if data["project_id"] else None,
            tags=json.dumps(data["tags"]),
            created_at=data["created_at"],
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, entry_id: UUID) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID."""
        result = await self.session.execute(
            select(KnowledgeEntryModel).where(KnowledgeEntryModel.id == str(entry_id))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_project(self, project_id: UUID) -> list[KnowledgeEntry]:
        """Get all knowledge entries for a project."""
        result = await self.session.execute(
            select(KnowledgeEntryModel).where(KnowledgeEntryModel.project_id == str(project_id))
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def search(self, query: str, limit: int = 10) -> list[KnowledgeEntry]:
        """Search knowledge base entries."""
        search_term = f"%{query}%"
        result = await self.session.execute(
            select(KnowledgeEntryModel)
            .where(KnowledgeEntryModel.content.ilike(search_term))
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: KnowledgeEntryModel) -> KnowledgeEntry:
        """Convert database model to domain entity using Pydantic validation."""
        return KnowledgeEntry.model_validate(
            {
                "id": model.id,
                "content": model.content,
                "source_message_id": model.source_message_id,
                "project_id": model.project_id if model.project_id else None,
                "tags": json.loads(model.tags) if model.tags else [],
                "created_at": model.created_at,
            }
        )
