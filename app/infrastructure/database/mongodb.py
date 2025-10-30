"""MongoDB connection and session management."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class MongoDatabase:
    """MongoDB connection and database management."""

    def __init__(self, connection_string: str, database_name: str = "virt_council"):
        """Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string (e.g., mongodb://localhost:27017)
            database_name: Name of the database to use
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Connect to MongoDB."""
        if self._client is None:
            logger.info(f"Connecting to MongoDB at {self.connection_string}")
            self._client = AsyncIOMotorClient(self.connection_string)
            self._database = self._client[self.database_name]
            # Test connection
            await self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            logger.info("Closing MongoDB connection")
            self._client.close()
            self._client = None
            self._database = None

    @property
    def database(self) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if self._database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._database

    async def create_indexes(self) -> None:
        """Create database indexes for better query performance."""
        if self._database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        # Message collection indexes
        await self._database.messages.create_index("user_id")
        await self._database.messages.create_index("chat_id")
        await self._database.messages.create_index("processed")
        await self._database.messages.create_index("created_at")
        
        # Project collection indexes
        await self._database.projects.create_index("name", unique=True)
        await self._database.projects.create_index("status")
        await self._database.projects.create_index([("name", "text"), ("description", "text")])
        
        # Knowledge entries collection indexes
        await self._database.knowledge_entries.create_index("project_id")
        await self._database.knowledge_entries.create_index("source_message_id")
        await self._database.knowledge_entries.create_index([("content", "text")])
        await self._database.knowledge_entries.create_index("tags")
        
        logger.info("MongoDB indexes created successfully")
