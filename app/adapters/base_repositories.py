"""Base repository classes with common logic."""

from abc import ABC
from typing import Generic, TypeVar, Type, Optional, Any
from uuid import UUID
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Type variables for generic repository classes
EntityType = TypeVar("EntityType", bound=BaseModel)
ModelType = TypeVar("ModelType")


class MongoBaseRepository(ABC, Generic[EntityType]):
    """Base class for MongoDB repositories with common Pydantic serialization logic."""

    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self.collection: AsyncIOMotorCollection = database[collection_name]

    @property
    def entity_class(self) -> Type[EntityType]:
        """Return the entity class for this repository. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must define entity_class property")

    async def _save(self, entity: EntityType) -> EntityType:
        """Generic save method using Pydantic serialization."""
        # Use Pydantic's model_dump to serialize
        document = entity.model_dump(mode="json")
        document["_id"] = str(entity.id)  # type: ignore
        document.pop("id", None)  # Remove id field, use _id instead

        await self.collection.replace_one({"_id": document["_id"]}, document, upsert=True)
        return entity

    async def _get_by_id(self, entity_id: UUID) -> Optional[EntityType]:
        """Generic get by ID method."""
        document = await self.collection.find_one({"_id": str(entity_id)})
        if not document:
            return None
        return self._to_entity(document)

    def _to_entity(self, document: dict) -> EntityType:
        """Convert database document to domain entity using Pydantic validation."""
        # Map _id back to id for Pydantic model
        document["id"] = document.pop("_id")
        return self.entity_class.model_validate(document)


class SQLAlchemyBaseRepository(ABC, Generic[EntityType, ModelType]):
    """Base class for SQLAlchemy repositories with common Pydantic serialization logic."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def entity_class(self) -> Type[EntityType]:
        """Return the entity class for this repository. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must define entity_class property")

    @property
    def model_class(self) -> Type[ModelType]:
        """Return the SQLAlchemy model class for this repository. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must define model_class property")

    async def _get_by_id(self, entity_id: UUID) -> Optional[EntityType]:
        """Generic get by ID method."""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == str(entity_id))  # type: ignore
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: ModelType) -> EntityType:
        """Convert database model to domain entity using Pydantic validation.

        Must be implemented by subclasses to handle model-specific field mapping.
        """
        raise NotImplementedError("Subclasses must implement _to_entity method")

    def _model_to_dict(self, model: ModelType) -> dict[str, Any]:
        """Convert SQLAlchemy model to dictionary for Pydantic validation.

        Must be implemented by subclasses to handle model-specific field mapping.
        """
        raise NotImplementedError("Subclasses must implement _model_to_dict method")
