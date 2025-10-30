"""Main application entry point."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Union

from app.infrastructure.config import Config
from app.infrastructure.database import Database, MongoDatabase
from app.adapters.telegram import TelegramBotAdapter
from app.adapters.llm import PydanticAILLMProvider
from app.adapters.storage import (
    SQLAlchemyMessageRepository,
    SQLAlchemyProjectRepository,
    SQLAlchemyKnowledgeRepository,
)
from app.adapters.mongodb_storage import (
    MongoMessageRepository,
    MongoProjectRepository,
    MongoKnowledgeRepository,
)
from app.use_cases import ProcessMessageUseCase, CreateProjectUseCase
from app.domain.entities import Message, Project
from app.domain.value_objects import MessageClassification
from app.domain.repositories import MessageRepository, ProjectRepository, KnowledgeRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger(__name__)


class Application:
    """Main application class."""

    def __init__(self, config: Config):
        self.config = config
        self.database: Union[Database, MongoDatabase, None] = None
        self.telegram_bot: TelegramBotAdapter | None = None
        self.llm_provider: PydanticAILLMProvider | None = None

    def _get_repositories(self) -> tuple[MessageRepository, ProjectRepository, KnowledgeRepository]:
        """Get repository instances based on storage backend."""
        if self.config.storage_backend == "mongodb":
            if not isinstance(self.database, MongoDatabase):
                raise RuntimeError("MongoDB database not initialized")
            db = self.database.database
            return (
                MongoMessageRepository(db),
                MongoProjectRepository(db),
                MongoKnowledgeRepository(db),
            )
        else:  # sqlalchemy
            if not isinstance(self.database, Database):
                raise RuntimeError("SQLAlchemy database not initialized")
            # Note: For SQLAlchemy, we need a session which is handled differently
            # This is a synchronous method, so we return a factory instead
            raise RuntimeError("Use async context for SQLAlchemy repositories")

    async def initialize(self) -> None:
        """Initialize application components."""
        logger.info("Initializing application...")

        # Ensure data directory exists
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        # Initialize database based on storage backend
        if self.config.storage_backend == "mongodb":
            self.database = MongoDatabase(self.config.mongodb_url, self.config.mongodb_database)
            await self.database.connect()
            await self.database.create_indexes()
            logger.info("MongoDB initialized")
        else:  # sqlalchemy
            self.database = Database(self.config.database_url)
            await self.database.create_tables()
            logger.info("SQLAlchemy database initialized")

        # Initialize LLM provider
        if self.config.llm_provider == "openai":
            self.llm_provider = PydanticAILLMProvider(
                provider="openai",
                api_key=self.config.openai_api_key,
                model_name=self.config.openai_model,
            )
        elif self.config.llm_provider == "gemini":
            self.llm_provider = PydanticAILLMProvider(
                provider="gemini",
                api_key=self.config.gemini_api_key,
                model_name=self.config.gemini_model,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")

        logger.info(f"LLM provider initialized: {self.config.llm_provider}")

        # Initialize Telegram bot
        self.telegram_bot = TelegramBotAdapter(self.config.telegram_bot_token)

        # Set up message handler
        async def message_handler(message: Message) -> MessageClassification:
            """Handle incoming messages."""
            if self.config.storage_backend == "mongodb":
                message_repo, project_repo, knowledge_repo = self._get_repositories()
            else:
                async with await self.database.get_session() as session:
                    message_repo = SQLAlchemyMessageRepository(session)
                    project_repo = SQLAlchemyProjectRepository(session)
                    knowledge_repo = SQLAlchemyKnowledgeRepository(session)

                    use_case = ProcessMessageUseCase(
                        message_repo=message_repo,
                        project_repo=project_repo,
                        knowledge_repo=knowledge_repo,
                        llm_provider=self.llm_provider,
                    )

                    return await use_case.execute(message)

            # MongoDB case
            use_case = ProcessMessageUseCase(
                message_repo=message_repo,
                project_repo=project_repo,
                knowledge_repo=knowledge_repo,
                llm_provider=self.llm_provider,
            )
            return await use_case.execute(message)

        # Set up project creation handler
        async def create_project_handler(name: str, description: str) -> Project:
            """Handle project creation."""
            if self.config.storage_backend == "mongodb":
                _, project_repo, _ = self._get_repositories()
            else:
                async with await self.database.get_session() as session:
                    project_repo = SQLAlchemyProjectRepository(session)
                    use_case = CreateProjectUseCase(project_repo)
                    return await use_case.execute(name, description)

            # MongoDB case
            use_case = CreateProjectUseCase(project_repo)
            return await use_case.execute(name, description)

        self.telegram_bot.set_message_handler(message_handler)
        self.telegram_bot.set_create_project_handler(create_project_handler)
        logger.info("Telegram bot initialized")

    async def start(self) -> None:
        """Start the application."""
        logger.info("Starting application...")
        await self.initialize()
        await self.telegram_bot.start()
        logger.info("Application started successfully")

        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutdown signal received")
            await self.stop()

    async def stop(self) -> None:
        """Stop the application."""
        logger.info("Stopping application...")

        if self.telegram_bot:
            await self.telegram_bot.stop()

        if self.database:
            await self.database.close()

        logger.info("Application stopped")


async def main() -> None:
    """Main entry point."""
    try:
        # Load configuration
        config = Config.from_env()
        config.validate()

        # Create and run application
        app = Application(config)
        await app.start()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
