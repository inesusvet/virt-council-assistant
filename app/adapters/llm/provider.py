"""LLM provider implementation."""
import json
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider

from app.adapters.llm import prompts
from app.domain.entities import KnowledgeEntry, Project
from app.domain.value_objects import MessageClassification, ResearchSuggestion


class PydanticAILLMProvider:
    """LLM provider implementation using Pydantic AI."""

    def __init__(self, provider: str, api_key: str, model_name: str):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name

        # Initialize the model based on provider
        if provider == "openai":
            provider = OpenAIProvider(api_key=api_key)
            self.model = OpenAIModel(model_name, provider=provider)
        elif provider == "gemini":
            provider = GoogleProvider(api_key=api_key)
            self.model = GoogleModel(model_name, provider=provider)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def classify_message(
        self, content: str, projects: list[Project]
    ) -> MessageClassification:
        """Classify a message and suggest project association."""
        # Create project context for the agent
        project_context = "\n".join(
            [f"- {p.name}: {p.description} (ID: {p.id})" for p in projects]
        )

        prompt = prompts.CLASSIFY_MESSAGE_PROMPT.format(
            content=content, project_context=project_context
        )

        # Create an agent for classification
        agent = Agent(self.model, result_type=str)

        try:
            result = await agent.run(prompt)
            response_data = json.loads(result.data)

            return MessageClassification(
                category=response_data.get("category", "general"),
                confidence=float(response_data.get("confidence", 0.5)),
                suggested_project_id=response_data.get("suggested_project_id"),
                tags=response_data.get("tags", []),
                summary=response_data.get("summary", ""),
            )
        except Exception as e:
            # Fallback classification
            return MessageClassification(
                category="general",
                confidence=0.3,
                summary=f"Failed to classify: {str(e)}",
            )

    async def extract_knowledge(self, content: str) -> str:
        """Extract structured knowledge from message content."""
        prompt = prompts.EXTRACT_KNOWLEDGE_PROMPT.format(content=content)

        agent = Agent(self.model, result_type=str)

        try:
            result = await agent.run(prompt)
            return result.data
        except Exception as e:
            return f"Original message: {content}\n\nNote: Failed to extract structured knowledge: {str(e)}"

    async def suggest_next_steps(
        self, project: Project, knowledge_entries: list[KnowledgeEntry]
    ) -> list[ResearchSuggestion]:
        """Suggest next research steps based on project context."""
        # Create context from knowledge entries
        knowledge_context = "\n\n".join(
            [f"- {entry.content}" for entry in knowledge_entries[:10]]  # Limit to recent
        )

        prompt = prompts.SUGGEST_NEXT_STEPS_PROMPT.format(
            project=project, knowledge_context=knowledge_context
        )

        agent = Agent(self.model, result_type=str)

        try:
            result = await agent.run(prompt)
            suggestions_data = json.loads(result.data)

            return [
                ResearchSuggestion(
                    title=s.get("title", ""),
                    description=s.get("description", ""),
                    priority=int(s.get("priority", 3)),
                    resources=s.get("resources", []),
                )
                for s in suggestions_data
            ]
        except Exception as e:
            # Return a default suggestion on error
            return [
                ResearchSuggestion(
                    title="Review Project Status",
                    description=f"Review the current status and next steps for {project.name}. (Error occurred: {str(e)})",
                    priority=3,
                    resources=[],
                )
            ]
