"""Example script demonstrating MongoDB storage and project creation."""

import asyncio
from app.domain.entities import Project, Message, KnowledgeEntry
from app.infrastructure.database import MongoDatabase
from app.adapters.mongodb_storage import (
    MongoProjectRepository,
    MongoMessageRepository,
    MongoKnowledgeRepository,
)
from app.use_cases import CreateProjectUseCase


async def main():
    """Demonstrate MongoDB storage and project creation."""
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

    # Example 1: Create a new project using the use case
    print("=== Creating a new project ===")
    create_project_use_case = CreateProjectUseCase(project_repo)
    
    project = await create_project_use_case.execute(
        name="Authentication System",
        description="Building a secure authentication system with JWT tokens and OAuth2"
    )
    
    print(f"✅ Project created!")
    print(f"   Name: {project.name}")
    print(f"   Description: {project.description}")
    print(f"   ID: {project.id}")
    print(f"   Status: {project.status}")
    print(f"   Created: {project.created_at}\n")

    # Example 2: Save a message
    print("=== Saving a message ===")
    message = Message(
        content="Working on JWT token implementation. Need to add refresh token support.",
        user_id="user123",
        chat_id="chat456",
        message_id=789
    )
    
    saved_message = await message_repo.save(message)
    print(f"✅ Message saved!")
    print(f"   Content: {saved_message.content}")
    print(f"   ID: {saved_message.id}\n")

    # Example 3: Save knowledge entry
    print("=== Saving knowledge entry ===")
    knowledge = KnowledgeEntry(
        content="JWT tokens should have short expiry times (15 minutes). Refresh tokens can last longer (7 days).",
        source_message_id=saved_message.id,
        project_id=project.id,
        tags=["jwt", "security", "authentication", "tokens"]
    )
    
    saved_knowledge = await knowledge_repo.save(knowledge)
    print(f"✅ Knowledge entry saved!")
    print(f"   Content: {saved_knowledge.content}")
    print(f"   Tags: {', '.join(saved_knowledge.tags)}")
    print(f"   Project ID: {saved_knowledge.project_id}\n")

    # Example 4: Retrieve project
    print("=== Retrieving project ===")
    retrieved_project = await project_repo.get_by_id(project.id)
    if retrieved_project:
        print(f"✅ Project retrieved!")
        print(f"   Name: {retrieved_project.name}")
        print(f"   Description: {retrieved_project.description}\n")

    # Example 5: Get knowledge entries for the project
    print("=== Getting knowledge entries for project ===")
    entries = await knowledge_repo.get_by_project(project.id)
    print(f"✅ Found {len(entries)} knowledge entries")
    for entry in entries:
        print(f"   - {entry.content[:80]}...")
        print(f"     Tags: {', '.join(entry.tags)}\n")

    # Cleanup
    await db.close()
    print("Connection closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure MongoDB is running on localhost:27017")
        print("You can start MongoDB with: docker run -d -p 27017:27017 mongo")
