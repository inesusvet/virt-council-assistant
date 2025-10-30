"""Unit tests for configuration."""

import pytest

from app.infrastructure.config import Config


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading configuration from environment."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///test.db")

    config = Config.from_env()

    assert config.telegram_bot_token == "test-token"
    assert config.llm_provider == "openai"
    assert config.openai_api_key == "test-openai-key"
    assert config.openai_model == "gpt-4"
    assert config.database_url == "sqlite+aiosqlite:///test.db"


def test_config_validation_missing_telegram_token() -> None:
    """Test validation fails when Telegram token is missing."""
    config = Config(
        telegram_bot_token="",
        llm_provider="openai",
        openai_api_key="test-key",
        openai_model="gpt-4",
        gemini_api_key="",
        gemini_model="",
        database_url="sqlite:///test.db",
        storage_backend="sqlalchemy",
        mongodb_url="",
        mongodb_database="",
        log_level="INFO",
        debug=False,
    )

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
        config.validate()


def test_config_validation_missing_openai_key() -> None:
    """Test validation fails when OpenAI key is missing for OpenAI provider."""
    config = Config(
        telegram_bot_token="test-token",
        llm_provider="openai",
        openai_api_key="",
        openai_model="gpt-4",
        gemini_api_key="",
        gemini_model="",
        database_url="sqlite:///test.db",
        storage_backend="sqlalchemy",
        mongodb_url="",
        mongodb_database="",
        log_level="INFO",
        debug=False,
    )

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        config.validate()


def test_config_validation_missing_gemini_key() -> None:
    """Test validation fails when Gemini key is missing for Gemini provider."""
    config = Config(
        telegram_bot_token="test-token",
        llm_provider="gemini",
        openai_api_key="",
        openai_model="",
        gemini_api_key="",
        gemini_model="gemini-1.5-flash",
        database_url="sqlite:///test.db",
        storage_backend="sqlalchemy",
        mongodb_url="",
        mongodb_database="",
        log_level="INFO",
        debug=False,
    )

    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        config.validate()


def test_config_validation_success() -> None:
    """Test successful validation."""
    config = Config(
        telegram_bot_token="test-token",
        llm_provider="openai",
        openai_api_key="test-key",
        openai_model="gpt-4",
        gemini_api_key="",
        gemini_model="",
        database_url="sqlite:///test.db",
        storage_backend="sqlalchemy",
        mongodb_url="",
        mongodb_database="",
        log_level="INFO",
        debug=False,
    )

    # Should not raise any exception
    config.validate()
