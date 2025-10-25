"""Value objects for the Virtual Council Assistant."""
from enum import Enum
from typing import Optional


class ProjectStatus(Enum):
    """Project status enumeration."""

    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageClassification:
    """Represents a classification result for a message."""

    def __init__(
        self,
        category: str,
        confidence: float,
        suggested_project_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        summary: Optional[str] = None,
    ):
        self.category = category
        self.confidence = confidence
        self.suggested_project_id = suggested_project_id
        self.tags = tags or []
        self.summary = summary

    def is_confident(self, threshold: float = 0.7) -> bool:
        """Check if classification confidence meets threshold."""
        return self.confidence >= threshold


class ResearchSuggestion:
    """Represents a research suggestion for next steps."""

    def __init__(
        self,
        title: str,
        description: str,
        priority: int = 0,
        resources: Optional[list[str]] = None,
    ):
        self.title = title
        self.description = description
        self.priority = priority
        self.resources = resources or []
