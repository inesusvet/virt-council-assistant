"""Unit tests for value objects."""
import pytest

from app.domain.value_objects import (
    ProjectStatus,
    MessageClassification,
    ResearchSuggestion,
)


def test_project_status_enum() -> None:
    """Test ProjectStatus enum."""
    assert ProjectStatus.ACTIVE.value == "active"
    assert ProjectStatus.ON_HOLD.value == "on_hold"
    assert ProjectStatus.COMPLETED.value == "completed"
    assert ProjectStatus.ARCHIVED.value == "archived"


def test_message_classification_creation() -> None:
    """Test MessageClassification creation."""
    classification = MessageClassification(
        category="feature_request",
        confidence=0.85,
        suggested_project_id="project-123",
        tags=["api", "feature"],
        summary="Request for new API feature",
    )

    assert classification.category == "feature_request"
    assert classification.confidence == 0.85
    assert classification.suggested_project_id == "project-123"
    assert classification.tags == ["api", "feature"]
    assert classification.summary == "Request for new API feature"


def test_message_classification_is_confident() -> None:
    """Test confidence threshold check."""
    high_confidence = MessageClassification(
        category="test",
        confidence=0.9,
    )
    low_confidence = MessageClassification(
        category="test",
        confidence=0.5,
    )

    assert high_confidence.is_confident(threshold=0.7) is True
    assert low_confidence.is_confident(threshold=0.7) is False


def test_research_suggestion_creation() -> None:
    """Test ResearchSuggestion creation."""
    suggestion = ResearchSuggestion(
        title="Review API design",
        description="Review the current API design patterns",
        priority=4,
        resources=["https://example.com/api-guide", "REST API Best Practices"],
    )

    assert suggestion.title == "Review API design"
    assert suggestion.description == "Review the current API design patterns"
    assert suggestion.priority == 4
    assert len(suggestion.resources) == 2
