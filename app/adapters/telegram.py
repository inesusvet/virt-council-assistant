"""Telegram bot adapter for receiving and sending messages."""
import logging
from typing import Callable, Awaitable
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from app.domain.entities import Message
from app.domain.value_objects import MessageClassification

logger = logging.getLogger(__name__)


class TelegramBotAdapter:
    """Adapter for Telegram Bot API integration."""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self.message_handler: Callable[[Message], Awaitable[MessageClassification]] | None = None

    def set_message_handler(
        self, handler: Callable[[Message], Awaitable[MessageClassification]]
    ) -> None:
        """Set the handler for processing incoming messages."""
        self.message_handler = handler

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        await update.message.reply_text(
            "👋 Welcome to Virtual Council Assistant!\n\n"
            "I'm here to help you manage your projects and build your knowledge base.\n\n"
            "Just send me messages about your projects, and I'll:\n"
            "- Classify and organize your messages\n"
            "- Build a searchable knowledge base\n"
            "- Suggest next steps for your projects\n\n"
            "Available commands:\n"
            "/start - Show this welcome message\n"
            "/help - Show help information\n"
            "/projects - List active projects\n"
            "/nextsteps <project_name> - Get suggestions for a project\n\n"
            "Just send me any message to get started!"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        await update.message.reply_text(
            "📚 Virtual Council Assistant Help\n\n"
            "How to use:\n"
            "1. Send me messages about your work, ideas, or questions\n"
            "2. I'll analyze and categorize them\n"
            "3. Access your organized knowledge anytime\n\n"
            "Commands:\n"
            "/start - Welcome message\n"
            "/help - This help message\n"
            "/projects - List all active projects\n"
            "/nextsteps <project_name> - Get AI-powered suggestions\n\n"
            "Example:\n"
            "Send: 'Working on the new API design for authentication'\n"
            "I'll classify it, extract key info, and link it to relevant projects!"
        )

    async def projects_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /projects command."""
        # This would typically fetch from the repository
        # For now, return a placeholder message
        await update.message.reply_text(
            "📊 Active Projects:\n\n"
            "Use this command to see your active projects.\n"
            "Project listing will be implemented with the full integration."
        )

    async def nextsteps_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /nextsteps command."""
        if not context.args:
            await update.message.reply_text(
                "Please specify a project name:\n"
                "/nextsteps <project_name>"
            )
            return

        project_name = " ".join(context.args)
        await update.message.reply_text(
            f"🔍 Getting next steps for project: {project_name}\n\n"
            "This will provide AI-powered suggestions once fully integrated."
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming text messages."""
        if not update.message or not update.message.text:
            return

        user_id = str(update.message.from_user.id)
        chat_id = str(update.message.chat_id)
        message_id = update.message.message_id
        content = update.message.text

        logger.info(f"Received message from user {user_id}: {content[:50]}...")

        # Create domain entity
        message = Message(
            content=content,
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
        )

        try:
            # Process message if handler is set
            if self.message_handler:
                classification = await self.message_handler(message)

                # Send response based on classification
                response = (
                    f"✅ Message processed!\n\n"
                    f"Category: {classification.category}\n"
                    f"Confidence: {classification.confidence:.2f}\n"
                )

                if classification.summary:
                    response += f"\nSummary: {classification.summary}\n"

                if classification.tags:
                    response += f"\nTags: {', '.join(classification.tags)}\n"

                if classification.suggested_project_id:
                    response += f"\nLinked to project: {classification.suggested_project_id}\n"

                await update.message.reply_text(response)
            else:
                await update.message.reply_text(
                    "Message received! Processing is not yet fully configured."
                )

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await update.message.reply_text(
                "Sorry, I encountered an error processing your message. Please try again later."
            )

    def setup_handlers(self) -> None:
        """Set up command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("projects", self.projects_command))
        self.application.add_handler(CommandHandler("nextsteps", self.nextsteps_command))

        # Message handler for text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def start(self) -> None:
        """Start the Telegram bot."""
        logger.info("Starting Telegram bot...")
        self.setup_handlers()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        logger.info("Telegram bot started and polling for updates")

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        logger.info("Stopping Telegram bot...")
        if self.application.updater.running:
            await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
        logger.info("Telegram bot stopped")
