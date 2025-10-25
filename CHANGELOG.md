# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-24

### Added
- Initial project bootstrap with Clean Architecture
- Core domain entities (Message, Project, KnowledgeEntry)
- Value objects (MessageClassification, ResearchSuggestion, ProjectStatus)
- Repository interfaces for data persistence
- Use cases for message processing, next steps suggestions, and knowledge search
- Telegram bot adapter with command handlers (/start, /help, /projects, /nextsteps)
- LLM provider adapter supporting OpenAI and Google Gemini via Pydantic AI
- SQLAlchemy storage adapters for all repositories
- Database models and session management
- Configuration management with environment variables
- Main application entry point with async/await support
- Unit tests for entities, value objects, and configuration
- Comprehensive documentation:
  - README.md with architecture overview and usage
  - QUICKSTART.md for easy setup
  - ARCHITECTURE.md with detailed architecture diagrams
  - DEPLOYMENT.md with deployment guides for various platforms
  - CONTRIBUTING.md with contribution guidelines
- Docker support (Dockerfile and docker-compose.yml)
- CI/CD workflow with GitHub Actions
- Setup script for database initialization
- Makefile for common development tasks
- Example scripts for project management

### Features
- AI-powered message classification
- Knowledge extraction from messages
- Project-based organization
- Research suggestions based on context
- Async/await throughout for performance
- Type hints and protocols for type safety
- Clean separation of concerns following Clean Architecture

### Technical Details
- Python 3.11+ support
- Pydantic AI for LLM integration
- python-telegram-bot for Telegram API
- SQLAlchemy 2.0 with async support
- SQLite/PostgreSQL database support
- pytest for testing
- Black for code formatting
- Ruff for linting
- mypy for type checking

[0.1.0]: https://github.com/inesusvet/virt-council-iaac/releases/tag/v0.1.0
