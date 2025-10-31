"""Example script demonstrating MongoDB storage with Pydantic validation."""

import asyncio
from pydantic import ValidationError
from app.domain.entities import Project, Message, KnowledgeEntry
from app.infrastructure.database import MongoDatabase
from app.adapters.mongodb_storage import (
    MongoProjectRepository,
    MongoMessageRepository,
    MongoKnowledgeRepository,
)
from app.use_cases import CreateProjectUseCase


async def main():
    """Demonstrate MongoDB storage with Pydantic entities."""
    # Initialize MongoDB connection
    # Note: Make sure MongoDB is running on localhost:27017
    db = MongoDatabase("mongodb://localhost:27017", "virt_council_demo")
    await db.connect()
    await db.create_indexes()

    print("Connected to MongoDB!\n")

    # Create repositories
    project_repo = MongoProjectRepository(db.database)
    message_repo = MongoMessageRepository(db.database)
    knowledge_repo = MongoKnowledgeRepository(db.database)

    # Example 1: Create a new project with Pydantic validation
    print("=== Creating a new project with Pydantic validation ===")
    create_project_use_case = CreateProjectUseCase(project_repo)

    project = await create_project_use_case.execute(
        name="Authentication System",
        description="Building a secure authentication system with JWT tokens and OAuth2",
    )

    print("✅ Project created and validated!")
    print(f"   Name: {project.name}")
    print(f"   Description: {project.description}")
    print(f"   ID: {project.id}")
    print(f"   Status: {project.status}")
    print(f"   Created: {project.created_at}\n")

    # Example 2: Demonstrate Pydantic validation on invalid data
    print("=== Testing Pydantic validation (invalid project) ===")
    try:
        Project(
            name="",  # Empty name should fail validation
            description="This should fail",
        )
    except ValidationError as e:
        print("✅ Validation caught empty name error!")
        print(f"   Error: {e.errors()[0]['msg']}\n")

    # Example 3: Save a message with automatic validation
    print("=== Saving a message with Pydantic validation ===")
    message = Message(
        content="Working on JWT token implementation. Need to add refresh token support.",
        user_id="user123",
        chat_id="chat456",
        message_id=789,
    )

    saved_message = await message_repo.save(message)
    print("✅ Message saved and validated!")
    print(f"   Content: {saved_message.content}")
    print(f"   ID: {saved_message.id}\n")

    # Example 4: Retrieve and validate data from database
    print("=== Retrieving and validating data from database ===")
    retrieved_project = await project_repo.get_by_id(project.id)
    if retrieved_project:
        print("✅ Project retrieved and validated using Pydantic!")
        print(f"   Name: {retrieved_project.name}")
        print(f"   Type: {type(retrieved_project).__name__}")
        # Demonstrate Pydantic's model_dump
        print(f"   JSON export: {retrieved_project.model_dump_json()[:80]}...\n")

    # Example 5: Save knowledge entry with tag validation
    print("=== Saving knowledge entry with tag normalization ===")
    knowledge = KnowledgeEntry(
        content="JWT tokens should have short expiry times (15 minutes). Refresh tokens can last longer (7 days).",
        source_message_id=saved_message.id,
        project_id=project.id,
        tags=["JWT", " Security ", "AUTHENTICATION", "  tokens  "],  # Mixed case/spaces
    )

    saved_knowledge = await knowledge_repo.save(knowledge)
    print("✅ Knowledge entry saved with normalized tags!")
    print(f"   Content: {saved_knowledge.content[:50]}...")
    print(f"   Tags (normalized): {saved_knowledge.tags}")  # Should be lowercase and trimmed
    print(f"   Project ID: {saved_knowledge.project_id}\n")

    # Example 6: Test status validation
    print("=== Testing status validation ===")
    try:
        Project(
            name="Test Project",
            description="Testing status validation",
            status="invalid_status",  # Should fail
        )
    except ValidationError as e:
        print("✅ Validation caught invalid status!")
        print(f"   Error: {e.errors()[0]['msg']}\n")

    # Cleanup
    await db.close()
    print("Connection closed.")
    print("\n" + "=" * 60)
    print("Summary: All Pydantic validations work correctly!")
    print("- Entities validate on creation")
    print("- Data serializes/deserializes automatically with model_dump/model_validate")
    print("- Invalid data is caught before it reaches the database")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure MongoDB is running on localhost:27017")
        print("You can start MongoDB with: docker run -d -p 27017:27017 mongo")
