#!/usr/bin/env python3
"""
Example script demonstrating how to programmatically add projects to the system.
"""
import asyncio
from app.infrastructure.config import Config
from app.infrastructure.database import Database
from app.domain.entities import Project
from app.adapters.storage import SQLAlchemyProjectRepository


async def add_project_example():
    """Example of adding a single project."""
    config = Config.from_env()
    db = Database(config.database_url)

    async with await db.get_session() as session:
        repo = SQLAlchemyProjectRepository(session)
        project = Project(
            name="Example Project", description="This is an example project", status="active"
        )
        saved_project = await repo.save(project)
        print(f"✅ Created project: {saved_project.name}")

    await db.close()


if __name__ == "__main__":
    asyncio.run(add_project_example())
