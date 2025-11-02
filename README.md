# Virtual Council Assistant

AI-powered assistant for project management and knowledge base building via Telegram, built with Python and Pydantic AI.

## Overview

The Virtual Council Assistant is an intelligent bot that helps you manage projects and build a knowledge base through Telegram conversations. It uses LLM AI (OpenAI or Google Gemini) to:

- **Classify incoming messages** into relevant project categories
- **Extract and structure knowledge** from your conversations
- **Build a searchable knowledge base** for future reference
- **Suggest next steps** based on project context and accumulated knowledge

## Architecture

This application follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── domain/              # Enterprise Business Rules
│   ├── entities/        # Core business objects (Message, Project, KnowledgeEntry)
│   ├── value_objects/   # Immutable value objects (MessageClassification, etc.)
│   └── repositories/    # Repository interfaces (abstractions)
│
├── use_cases/          # Application Business Rules
│   └── __init__.py     # Use case implementations (ProcessMessage, GetNextSteps, etc.)
│
├── adapters/           # Interface Adapters
│   ├── telegram/       # Telegram Bot API integration
│   ├── llm/           # LLM provider adapters (OpenAI, Gemini)
│   └── storage/       # Repository implementations (SQLAlchemy)
│
├── infrastructure/     # Frameworks & Drivers
│   ├── database/      # Database models and connection management
│   └── config/        # Configuration management
│
└── main.py           # Application entry point
```

### Clean Architecture Layers

1. **Domain Layer** (innermost): Contains core business logic, independent of external frameworks
2. **Use Cases Layer**: Orchestrates domain objects to implement business workflows
3. **Interface Adapters**: Converts data between use cases and external services
4. **Frameworks & Drivers** (outermost): External tools, databases, and frameworks

## Features

- ✅ **Telegram Integration**: Receive and process messages via Telegram Bot API
- ✅ **AI-Powered Classification**: Automatically categorize messages using LLM
- ✅ **Knowledge Extraction**: Extract structured insights from conversations
- ✅ **Project Management**: Link messages and knowledge to active projects
- ✅ **Project Creation**: Create new projects with name and description via Telegram
- ✅ **Next Steps Suggestions**: Get AI-powered recommendations for research and actions
- ✅ **Flexible Storage**: Support for both SQLAlchemy (SQLite/PostgreSQL) and MongoDB
- ✅ **Dataclass Entities**: Clean, immutable domain entities using Python dataclasses
- ✅ **Clean Architecture**: Maintainable, testable, and extensible codebase

## Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key OR Google Gemini API Key
- Database: SQLite (default), PostgreSQL, or MongoDB

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/inesusvet/virt-council-iaac.git
cd virt-council-iaac
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# LLM Provider (choose: openai or gemini)
LLM_PROVIDER=openai

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# OR Google Gemini Configuration (if using Gemini)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Storage Backend (choose: sqlalchemy or mongodb)
STORAGE_BACKEND=sqlalchemy

# SQLAlchemy Database Configuration (if using sqlalchemy)
DATABASE_URL=sqlite+aiosqlite:///./data/virt_council.db

# MongoDB Configuration (if using mongodb)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=virt_council
```

### Storage Backend Options

The application supports two storage backends:

#### SQLAlchemy (Default)
- Supports SQLite (default), PostgreSQL, MySQL
- Good for development and small to medium deployments
- Configuration: Set `STORAGE_BACKEND=sqlalchemy` and configure `DATABASE_URL`
- **SQLite**: `DATABASE_URL=sqlite+aiosqlite:///./data/virt_council.db`
- **PostgreSQL** (async with aiopg): `DATABASE_URL=postgresql+aiopg://user:password@localhost:5432/virt_council`

#### MongoDB
- NoSQL document database
- Better for large-scale deployments with flexible schema
- Configuration: Set `STORAGE_BACKEND=mongodb` and configure `MONGODB_URL` and `MONGODB_DATABASE`
- Requires MongoDB server running locally or accessible via connection string

## Usage

### Starting the Bot

Run the application:

```bash
python -m app.main
```

The bot will:
1. Initialize the database
2. Connect to the Telegram API
3. Start listening for messages

### Interacting with the Bot

Open Telegram and start a chat with your bot:

1. **Start the bot**: `/start`
2. **Get help**: `/help`
3. **Create a project**: `/createproject <name> - <description>`
4. **Send a message**: Just type any message about your work or projects
5. **List projects**: `/projects` (to be enhanced)
6. **Get suggestions**: `/nextsteps <project_name>`

### Example Workflows

#### Creating a Project
```
User: /createproject Auth System - Building secure authentication API with JWT

Bot: ✅ Project created successfully!
     📁 Name: Auth System
     📝 Description: Building secure authentication API with JWT
     🆔 ID: 123e4567-e89b-12d3-a456-426614174000
     📅 Created: 2024-01-15 10:30:00
```

#### Processing a Message
```
User: Working on the new authentication API. Need to implement JWT tokens.

Bot: ✅ Message processed!
     Category: feature_request
     Confidence: 0.92
     Summary: Implementation task for JWT token authentication in API
     Tags: authentication, api, jwt, security
     Linked to project: authentication-system
```

## Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=app --cov-report=html
```

### Code Formatting

Format code with Black:

```bash
black app/ tests/
```

Lint with Ruff:

```bash
ruff check app/ tests/
```

Type checking with mypy:

```bash
mypy app/
```

### Project Structure

```
virt-council-iaac/
├── app/                    # Application code
│   ├── domain/            # Domain layer
│   ├── use_cases/         # Use cases layer
│   ├── adapters/          # Adapters layer
│   ├── infrastructure/    # Infrastructure layer
│   └── main.py           # Entry point
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── data/                  # Database files (gitignored)
├── .env                   # Environment configuration (gitignored)
├── .env.example          # Example environment file
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Adding Projects

To add projects to the system, you can create a simple script or use the database directly. Example:

```python
from app.domain.entities import Project
from app.infrastructure.database import Database
from app.adapters.storage import SQLAlchemyProjectRepository

async def add_project():
    db = Database("sqlite+aiosqlite:///./data/virt_council.db")
    async with await db.get_session() as session:
        repo = SQLAlchemyProjectRepository(session)
        project = Project(
            name="Authentication System",
            description="Building a secure authentication system with JWT",
            status="active"
        )
        await repo.save(project)
```

## Extending the Application

### Adding New LLM Providers

1. Implement the `LLMProvider` protocol in `app/use_cases/__init__.py`
2. Add your provider to `app/adapters/llm/__init__.py`
3. Update configuration in `app/infrastructure/config/__init__.py`

### Adding New Message Channels

1. Create a new adapter in `app/adapters/`
2. Implement message receiving and sending
3. Connect to the use cases layer
4. Register in `app/main.py`

### Custom Use Cases

Create new use cases in `app/use_cases/` following the existing pattern:

```python
class MyCustomUseCase:
    def __init__(self, dependencies):
        self.dependencies = dependencies
    
    async def execute(self, params):
        # Implementation
        pass
```

## Technology Stack

- **Python 3.11+**: Core language with dataclass support
- **Pydantic AI**: AI framework with type safety
- **python-telegram-bot**: Telegram Bot API wrapper
- **SQLAlchemy**: ORM for relational database operations
- **Motor**: Async MongoDB driver for Python
- **pymongo**: MongoDB Python driver
- **SQLite/PostgreSQL/MongoDB**: Data persistence options
- **OpenAI/Gemini**: LLM providers
- **pytest**: Testing framework

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes following Clean Architecture principles
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review the code comments

## Roadmap

- [ ] Enhanced project management UI
- [ ] Vector database integration for semantic search
- [ ] Multi-user support with permissions
- [ ] Web interface for knowledge base browsing
- [ ] Export functionality (Markdown, PDF)
- [ ] Integration with other platforms (Slack, Discord)
- [ ] Advanced analytics and insights