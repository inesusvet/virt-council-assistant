"""Unit tests for CreateProjectUseCase."""

import pytest

from app.domain.entities import Project
from app.use_cases import CreateProjectUseCase


class MockProjectRepository:
    """Mock project repository for testing."""

    def __init__(self):
        self.projects = []

    async def save(self, project: Project) -> Project:
        """Save a project."""
        self.projects.append(project)
        return project

    async def search(self, query: str) -> list[Project]:
        """Search projects by name or description."""
        results = []
        for project in self.projects:
            if (
                query.lower() in project.name.lower()
                or query.lower() in project.description.lower()
            ):
                results.append(project)
        return results

    async def get_by_name(self, name: str) -> Project | None:
        """Get project by name."""
        for project in self.projects:
            if project.name == name:
                return project
        return None


@pytest.mark.asyncio
async def test_create_project_use_case_success():
    """Test successful project creation."""
    repo = MockProjectRepository()
    use_case = CreateProjectUseCase(repo)

    project = await use_case.execute("New Project", "Project description")

    assert project.name == "New Project"
    assert project.description == "Project description"
    assert project.status == "active"
    assert len(repo.projects) == 1


@pytest.mark.asyncio
async def test_create_project_use_case_duplicate_name():
    """Test that creating a project with duplicate name raises error."""
    repo = MockProjectRepository()
    use_case = CreateProjectUseCase(repo)

    # Create first project
    await use_case.execute("Existing Project", "First description")

    # Try to create project with same name
    with pytest.raises(ValueError, match="Project with name 'Existing Project' already exists"):
        await use_case.execute("Existing Project", "Second description")


@pytest.mark.asyncio
async def test_create_project_use_case_case_insensitive():
    """Test that project name matching is case-insensitive."""
    repo = MockProjectRepository()
    use_case = CreateProjectUseCase(repo)

    # Create first project
    await use_case.execute("My Project", "First description")

    # Try to create project with same name but different case
    with pytest.raises(ValueError, match="already exists"):
        await use_case.execute("my project", "Second description")


@pytest.mark.asyncio
async def test_create_project_use_case_multiple_projects():
    """Test creating multiple unique projects."""
    repo = MockProjectRepository()
    use_case = CreateProjectUseCase(repo)

    project1 = await use_case.execute("Project 1", "First project")
    project2 = await use_case.execute("Project 2", "Second project")
    project3 = await use_case.execute("Project 3", "Third project")

    assert len(repo.projects) == 3
    assert project1.name == "Project 1"
    assert project2.name == "Project 2"
    assert project3.name == "Project 3"
