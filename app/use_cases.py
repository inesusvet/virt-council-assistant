"""Use cases for the Virtual Council Assistant."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Message, Project, KnowledgeEntry
from app.domain.repositories import MessageRepository, ProjectRepository, KnowledgeRepository
from app.domain.value_objects import MessageClassification, ResearchSuggestion


class LLMProvider(Protocol):
    """Protocol for LLM provider interaction."""

    async def classify_message(
        self, content: str, projects: list[Project]
    ) -> MessageClassification:
        """Classify a message and suggest project association."""
        ...

    async def extract_knowledge(self, content: str) -> str:
        """Extract structured knowledge from message content."""
        ...

    async def suggest_next_steps(
        self, project: Project, knowledge_entries: list[KnowledgeEntry]
    ) -> list[ResearchSuggestion]:
        """Suggest next research steps based on project context."""
        ...


class ProcessMessageUseCase:
    """Use case for processing incoming messages."""

    def __init__(
        self,
        message_repo: MessageRepository,
        project_repo: ProjectRepository,
        knowledge_repo: KnowledgeRepository,
        llm_provider: LLMProvider,
    ):
        self.message_repo = message_repo
        self.project_repo = project_repo
        self.knowledge_repo = knowledge_repo
        self.llm_provider = llm_provider

    async def execute(self, message: Message) -> MessageClassification:
        """Process a message: classify, extract knowledge, and store."""
        # Save the message first
        saved_message = await self.message_repo.save(message)

        # Get active projects for classification
        projects = await self.project_repo.get_all_active()

        # Classify the message
        classification = await self.llm_provider.classify_message(message.content, projects)

        # Extract knowledge and save to knowledge base
        knowledge_content = await self.llm_provider.extract_knowledge(message.content)
        knowledge_entry = KnowledgeEntry(
            content=knowledge_content,
            source_message_id=saved_message.id,
            project_id=(
                UUID(classification.suggested_project_id)
                if classification.suggested_project_id
                else None
            ),
            tags=classification.tags,
        )
        await self.knowledge_repo.save(knowledge_entry)

        # Mark message as processed
        saved_message.mark_as_processed()
        await self.message_repo.mark_as_processed(saved_message.id)

        return classification


class CreateProjectUseCase:
    """Use case for creating a new project."""

    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    async def execute(self, name: str, description: str) -> Project:
        """Create a new project with the given name and description.

        Args:
            name: Project name
            description: Project description

        Returns:
            Created project

        Raises:
            ValueError: If a project with the same name already exists
        """
        # Check if project with this name already exists
        existing = await self.project_repo.search(name)
        for project in existing:
            if project.name.lower() == name.lower():
                raise ValueError(f"Project with name '{name}' already exists")

        # Create new project
        project = Project(name=name, description=description, status="active")

        return await self.project_repo.save(project)


class GetNextStepsUseCase:
    """Use case for getting research suggestions for a project."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        knowledge_repo: KnowledgeRepository,
        llm_provider: LLMProvider,
    ):
        self.project_repo = project_repo
        self.knowledge_repo = knowledge_repo
        self.llm_provider = llm_provider

    async def execute(self, project_id: UUID) -> list[ResearchSuggestion]:
        """Get next step suggestions for a project."""
        # Get the project
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Get knowledge entries for the project
        knowledge_entries = await self.knowledge_repo.get_by_project(project_id)

        # Get suggestions from LLM
        suggestions = await self.llm_provider.suggest_next_steps(project, knowledge_entries)

        return suggestions


class SearchKnowledgeUseCase:
    """Use case for searching the knowledge base."""

    def __init__(self, knowledge_repo: KnowledgeRepository):
        self.knowledge_repo = knowledge_repo

    async def execute(self, query: str, limit: int = 10) -> list[KnowledgeEntry]:
        """Search the knowledge base."""
        return await self.knowledge_repo.search(query, limit)
