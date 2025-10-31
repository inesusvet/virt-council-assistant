"""Unit tests for MongoDB repositories."""

import pytest
from uuid import uuid4

from app.domain.entities import Message, Project, KnowledgeEntry
from app.adapters.mongodb_storage import (
    MongoMessageRepository,
    MongoProjectRepository,
    MongoKnowledgeRepository,
)


class MockDatabase:
    """Mock MongoDB database for testing."""

    def __init__(self):
        self.messages = MockCollection()
        self.projects = MockCollection()
        self.knowledge_entries = MockCollection()


class MockCollection:
    """Mock MongoDB collection for testing."""

    def __init__(self):
        self.documents = {}

    async def replace_one(self, filter_doc, document, upsert=False):
        """Mock replace_one operation."""
        doc_id = filter_doc.get("_id")
        if upsert or doc_id in self.documents:
            self.documents[doc_id] = document
        return None

    async def find_one(self, filter_doc):
        """Mock find_one operation."""
        doc_id = filter_doc.get("_id")
        return self.documents.get(doc_id)

    def find(self, filter_doc=None):
        """Mock find operation."""
        return MockCursor(self.documents, filter_doc)

    async def update_one(self, filter_doc, update_doc):
        """Mock update_one operation."""
        doc_id = filter_doc.get("_id")
        if doc_id in self.documents:
            # Handle $set operator
            set_values = update_doc.get("$set", {})
            self.documents[doc_id].update(set_values)
        return None


class MockCursor:
    """Mock MongoDB cursor for testing."""

    def __init__(self, documents, filter_doc=None):
        self.documents = documents
        self.filter_doc = filter_doc or {}
        self._limit = None

    def limit(self, count):
        """Mock limit operation."""
        self._limit = count
        return self

    async def to_list(self, length=None):
        """Mock to_list operation."""
        # Simple filter matching
        results = []
        for doc in self.documents.values():
            match = True
            for key, value in self.filter_doc.items():
                if key.startswith("$"):
                    continue
                if doc.get(key) != value:
                    match = False
                    break
            if match:
                results.append(doc)
                if self._limit and len(results) >= self._limit:
                    break
        return results


@pytest.mark.asyncio
async def test_mongo_message_repository_save():
    """Test saving a message to MongoDB repository."""
    db = MockDatabase()
    repo = MongoMessageRepository(db)

    message = Message(
        content="Test message",
        user_id="user123",
        chat_id="chat456",
        message_id=789,
    )

    saved = await repo.save(message)

    assert saved.id == message.id
    assert saved.content == "Test message"
    assert saved.user_id == "user123"


@pytest.mark.asyncio
async def test_mongo_message_repository_get_by_id():
    """Test retrieving a message by ID from MongoDB repository."""
    db = MockDatabase()
    repo = MongoMessageRepository(db)

    message = Message(
        content="Test message",
        user_id="user123",
        chat_id="chat456",
    )
    await repo.save(message)

    retrieved = await repo.get_by_id(message.id)

    assert retrieved is not None
    assert retrieved.id == message.id
    assert retrieved.content == "Test message"


@pytest.mark.asyncio
async def test_mongo_message_repository_mark_as_processed():
    """Test marking a message as processed in MongoDB repository."""
    db = MockDatabase()
    repo = MongoMessageRepository(db)

    message = Message(
        content="Test message",
        user_id="user123",
        chat_id="chat456",
        processed=False,
    )
    await repo.save(message)

    await repo.mark_as_processed(message.id)

    retrieved = await repo.get_by_id(message.id)
    assert retrieved.processed is True


@pytest.mark.asyncio
async def test_mongo_project_repository_save():
    """Test saving a project to MongoDB repository."""
    db = MockDatabase()
    repo = MongoProjectRepository(db)

    project = Project(
        name="Test Project",
        description="A test project",
        status="active",
    )

    saved = await repo.save(project)

    assert saved.id == project.id
    assert saved.name == "Test Project"
    assert saved.description == "A test project"


@pytest.mark.asyncio
async def test_mongo_project_repository_get_by_id():
    """Test retrieving a project by ID from MongoDB repository."""
    db = MockDatabase()
    repo = MongoProjectRepository(db)

    project = Project(
        name="Test Project",
        description="A test project",
    )
    await repo.save(project)

    retrieved = await repo.get_by_id(project.id)

    assert retrieved is not None
    assert retrieved.id == project.id
    assert retrieved.name == "Test Project"


@pytest.mark.asyncio
async def test_mongo_knowledge_repository_save():
    """Test saving a knowledge entry to MongoDB repository."""
    db = MockDatabase()
    repo = MongoKnowledgeRepository(db)

    message_id = uuid4()
    project_id = uuid4()

    entry = KnowledgeEntry(
        content="Test knowledge",
        source_message_id=message_id,
        project_id=project_id,
        tags=["test", "knowledge"],
    )

    saved = await repo.save(entry)

    assert saved.id == entry.id
    assert saved.content == "Test knowledge"
    assert saved.project_id == project_id


@pytest.mark.asyncio
async def test_mongo_knowledge_repository_get_by_id():
    """Test retrieving a knowledge entry by ID from MongoDB repository."""
    db = MockDatabase()
    repo = MongoKnowledgeRepository(db)

    message_id = uuid4()
    entry = KnowledgeEntry(
        content="Test knowledge",
        source_message_id=message_id,
        tags=["test"],
    )
    await repo.save(entry)

    retrieved = await repo.get_by_id(entry.id)

    assert retrieved is not None
    assert retrieved.id == entry.id
    assert retrieved.content == "Test knowledge"
