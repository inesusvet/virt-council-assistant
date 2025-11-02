"""Unit tests for domain entities."""

from uuid import uuid4

from app.domain.entities import Message, Project, KnowledgeEntry


def test_message_creation() -> None:
    """Test message entity creation."""
    message = Message(
        content="Test message",
        user_id="123",
        chat_id="456",
        message_id=789,
    )

    assert message.content == "Test message"
    assert message.user_id == "123"
    assert message.chat_id == "456"
    assert message.message_id == 789
    assert message.processed is False
    assert message.id is not None
    assert message.created_at is not None


def test_message_mark_as_processed() -> None:
    """Test marking message as processed."""
    message = Message(
        content="Test",
        user_id="123",
        chat_id="456",
    )

    assert message.processed is False
    message.mark_as_processed()
    assert message.processed is True


def test_project_creation() -> None:
    """Test project entity creation."""
    project = Project(
        name="Test Project",
        description="A test project",
        status="active",
    )

    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.status == "active"
    assert project.id is not None
    assert project.created_at is not None


def test_project_update_description() -> None:
    """Test updating project description."""
    project = Project(
        name="Test",
        description="Original",
    )

    original_updated_at = project.updated_at
    project.update_description("New description")

    assert project.description == "New description"
    assert project.updated_at > original_updated_at


def test_knowledge_entry_creation() -> None:
    """Test knowledge entry creation."""
    message_id = uuid4()
    entry = KnowledgeEntry(
        content="Test knowledge",
        source_message_id=message_id,
    )

    assert entry.content == "Test knowledge"
    assert entry.source_message_id == message_id
    assert entry.project_id is None
    assert entry.tags == []
    assert entry.id is not None


def test_knowledge_entry_add_tag() -> None:
    """Test adding tags to knowledge entry."""
    entry = KnowledgeEntry(
        content="Test",
        source_message_id=uuid4(),
    )

    entry.add_tag("python")
    entry.add_tag("testing")
    entry.add_tag("python")  # Duplicate

    assert len(entry.tags) == 2
    assert "python" in entry.tags
    assert "testing" in entry.tags


def test_knowledge_entry_link_to_project() -> None:
    """Test linking knowledge entry to project."""
    project_id = uuid4()
    entry = KnowledgeEntry(
        content="Test",
        source_message_id=uuid4(),
    )

    assert entry.project_id is None
    entry.link_to_project(project_id)
    assert entry.project_id == project_id
