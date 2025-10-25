# Architecture Documentation

## Clean Architecture Overview

The Virtual Council Assistant is built following Clean Architecture principles, ensuring maintainability, testability, and flexibility.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     External Interfaces                      │
│                   (Telegram, OpenAI, DB)                     │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│              Frameworks & Drivers Layer                      │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │  Telegram  │  │    LLM     │  │     Database         │  │
│  │   Client   │  │   Client   │  │  (SQLAlchemy ORM)    │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│              Interface Adapters Layer                        │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │  Telegram  │  │    LLM     │  │  Storage Adapters    │  │
│  │  Adapter   │  │  Adapter   │  │  (Repositories)      │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Use Cases Layer                            │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │ ProcessMessage   │  │  GetNextSteps                  │  │
│  │  UseCase         │  │   UseCase                      │  │
│  └──────────────────┘  └────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         SearchKnowledge UseCase                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Entities   │  │  Value       │  │  Repository      │   │
│  │  - Message  │  │  Objects     │  │  Interfaces      │   │
│  │  - Project  │  │  - Status    │  │  - Message       │   │
│  │  - Knowledge│  │  - Class.    │  │  - Project       │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Message Processing Flow

```
Telegram User
     │
     ▼
TelegramBotAdapter (receives message)
     │
     ▼
ProcessMessageUseCase
     │
     ├──► MessageRepository (save message)
     │
     ├──► ProjectRepository (get active projects)
     │
     ├──► LLMProvider (classify message)
     │
     ├──► LLMProvider (extract knowledge)
     │
     ├──► KnowledgeRepository (save knowledge)
     │
     └──► MessageRepository (mark as processed)
     │
     ▼
TelegramBotAdapter (send response)
     │
     ▼
Telegram User
```

### 2. Next Steps Suggestion Flow

```
Telegram User (/nextsteps command)
     │
     ▼
TelegramBotAdapter
     │
     ▼
GetNextStepsUseCase
     │
     ├──► ProjectRepository (get project)
     │
     ├──► KnowledgeRepository (get knowledge entries)
     │
     └──► LLMProvider (suggest next steps)
     │
     ▼
TelegramBotAdapter (send suggestions)
     │
     ▼
Telegram User
```

## Component Responsibilities

### Domain Layer
- **Entities**: Core business objects with identity
  - `Message`: User messages from Telegram
  - `Project`: Projects to organize work
  - `KnowledgeEntry`: Extracted knowledge items

- **Value Objects**: Immutable objects without identity
  - `MessageClassification`: Classification results
  - `ResearchSuggestion`: AI-generated suggestions
  - `ProjectStatus`: Enumeration of project states

- **Repository Interfaces**: Contracts for data persistence
  - Define what operations are needed
  - Independent of implementation details

### Use Cases Layer
- **ProcessMessageUseCase**: Orchestrates message processing
- **GetNextStepsUseCase**: Generates project suggestions
- **SearchKnowledgeUseCase**: Searches the knowledge base

### Interface Adapters Layer
- **TelegramBotAdapter**: Converts between Telegram API and domain
- **PydanticAILLMProvider**: Converts between LLM APIs and domain
- **Repository Implementations**: Converts between database and domain

### Frameworks & Drivers Layer
- **Database Models**: SQLAlchemy ORM models
- **Database Connection**: Session management
- **Configuration**: Environment variable handling

## Dependency Rule

Dependencies only point inward. Inner layers know nothing about outer layers:

- Domain Layer: No dependencies on outer layers
- Use Cases: Depends only on Domain Layer
- Adapters: Depends on Use Cases and Domain
- Frameworks: Depends on all inner layers

## Testing Strategy

### Unit Tests
- Domain entities and value objects (no dependencies)
- Use cases (with mocked repositories)
- Individual adapters (with mocked external services)

### Integration Tests
- Database repositories with actual database
- LLM provider with actual API (or mocked)
- Telegram adapter with test bot

### End-to-End Tests
- Full flow from Telegram to database and back
- Real external services or test doubles

## Extension Points

### Adding New Message Sources
1. Create new adapter implementing message receiving
2. Convert to domain `Message` entity
3. Use existing `ProcessMessageUseCase`

### Adding New LLM Providers
1. Implement `LLMProvider` protocol
2. Add configuration for new provider
3. Register in application setup

### Adding New Storage Backends
1. Implement repository interfaces
2. Add database models if needed
3. Configure in environment

## Design Patterns Used

- **Repository Pattern**: Abstract data access
- **Adapter Pattern**: Convert between external APIs and domain
- **Dependency Injection**: Pass dependencies to use cases
- **Protocol/Interface Segregation**: Define clear contracts
- **Factory Pattern**: Create objects with complex setup
- **Strategy Pattern**: Switch between LLM providers

## Benefits of This Architecture

1. **Testability**: Easy to test with mocks and test doubles
2. **Maintainability**: Clear separation of concerns
3. **Flexibility**: Easy to swap implementations
4. **Independence**: Domain logic independent of frameworks
5. **Scalability**: Easy to add new features
6. **Understandability**: Clear structure and dependencies
