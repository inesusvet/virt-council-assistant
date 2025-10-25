# Contributing to Virtual Council Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Follow the architecture**:
   - Respect Clean Architecture principles
   - Place code in the appropriate layer
   - Follow dependency rules (inner layers don't depend on outer)

4. **Write tests**:
   - Add unit tests for new functionality
   - Ensure existing tests pass
   - Aim for high test coverage

5. **Follow code style**:
   ```bash
   # Format code
   black app/ tests/
   
   # Lint code
   ruff check app/ tests/
   
   # Type check
   mypy app/
   ```

6. **Commit your changes**:
   ```bash
   git commit -m "feat: add new feature"
   ```
   
   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Adding tests
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**:
   - Describe what changes you made
   - Reference any related issues
   - Ensure CI checks pass

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/inesusvet/virt-council-iaac.git
   cd virt-council-iaac
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

5. **Run tests**:
   ```bash
   pytest
   ```

## Architecture Guidelines

### Clean Architecture Layers

When adding new features, respect the layer boundaries:

```
Domain → Use Cases → Adapters → Infrastructure
(inner)                              (outer)
```

**Rules**:
- Inner layers never depend on outer layers
- Use dependency injection for loose coupling
- Define interfaces in inner layers, implement in outer layers

### Adding New Features

**Example: Adding a new message handler**

1. **Domain Layer** (if needed):
   ```python
   # app/domain/entities/your_entity.py
   class YourEntity:
       def __init__(self, ...):
           ...
   ```

2. **Use Case Layer**:
   ```python
   # app/use_cases/your_use_case.py
   class YourUseCase:
       def __init__(self, dependencies):
           self.dependencies = dependencies
       
       async def execute(self, params):
           # Implementation
           pass
   ```

3. **Adapter Layer**:
   ```python
   # app/adapters/your_adapter.py
   class YourAdapter:
       async def handle(self, ...):
           # Convert external data to domain
           use_case = YourUseCase(...)
           result = await use_case.execute(...)
           # Convert domain result to external format
   ```

4. **Wire it up** in `app/main.py`

### Testing Guidelines

**Unit Tests**:
- Test individual components in isolation
- Mock external dependencies
- Place in `tests/unit/`

**Integration Tests**:
- Test component interactions
- Use real database (test database)
- Place in `tests/integration/`

**Example Test**:
```python
import pytest
from app.domain.entities import Message

def test_message_creation():
    message = Message(
        content="Test",
        user_id="123",
        chat_id="456"
    )
    assert message.content == "Test"
    assert message.processed is False
```

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for public APIs

**Example**:
```python
from typing import Optional

async def process_message(
    message: str,
    user_id: str,
    project_id: Optional[str] = None
) -> MessageClassification:
    """Process a user message.
    
    Args:
        message: The message content
        user_id: User identifier
        project_id: Optional project to link to
    
    Returns:
        Classification result
    """
    # Implementation
```

### Naming Conventions

- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

## Documentation

- Update README.md if adding major features
- Add docstrings to public APIs
- Update ARCHITECTURE.md if changing architecture
- Add examples for new features

## Running Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_entities.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

## Continuous Integration

All pull requests must pass:
- Unit tests
- Code formatting (Black)
- Linting (Ruff)
- Type checking (mypy)
- Security checks (Bandit, Safety)

CI runs automatically on pull requests.

## Release Process

1. Update version in `app/__init__.py`
2. Update CHANGELOG.md
3. Create a git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release with notes

## Getting Help

- Open an issue for questions
- Join discussions for design decisions
- Tag maintainers for urgent issues

## Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Acknowledged in commits

Thank you for contributing! 🎉
