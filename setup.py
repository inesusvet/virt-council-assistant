#!/usr/bin/env python3
"""Setup script to help initialize the Virtual Council Assistant."""
import asyncio
import sys
from pathlib import Path

from app.infrastructure.config import Config
from app.infrastructure.database import Database
from app.domain.entities import Project
from app.adapters.storage import SQLAlchemyProjectRepository


async def setup_database() -> None:
    """Initialize the database and create tables."""
    print("🔧 Setting up database...")
    config = Config.from_env()

    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    db = Database(config.database_url)
    await db.create_tables()
    print("✅ Database tables created successfully!")

    # Add sample projects
    print("\n📊 Adding sample projects...")
    async with await db.get_session() as session:
        repo = SQLAlchemyProjectRepository(session)

        sample_projects = [
            Project(
                name="Virtual Council Infrastructure",
                description="Infrastructure as Code for Virtual Council platform using Terraform",
                status="active",
            ),
            Project(
                name="AI Assistant Development",
                description="Development of the AI-powered assistant for project management",
                status="active",
            ),
            Project(
                name="Knowledge Base System",
                description="Building a comprehensive knowledge base system with semantic search",
                status="active",
            ),
        ]

        for project in sample_projects:
            await repo.save(project)
            print(f"  ✓ Created project: {project.name}")

    await db.close()
    print("\n✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure your .env file with API keys")
    print("2. Run: python -m app.main")
    print("3. Start chatting with your bot on Telegram!")


def check_env_file() -> bool:
    """Check if .env file exists."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Please copy .env.example to .env and configure it:")
        print("   cp .env.example .env")
        print()
        return False
    return True


async def main() -> None:
    """Main setup function."""
    print("=" * 60)
    print("Virtual Council Assistant - Setup")
    print("=" * 60)
    print()

    # Check for .env file
    env_exists = check_env_file()

    if not env_exists:
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() != "y":
            print("Setup cancelled. Please create .env file first.")
            sys.exit(0)

    try:
        await setup_database()
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
