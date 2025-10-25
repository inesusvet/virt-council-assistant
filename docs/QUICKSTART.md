# Quick Start Guide

## Get Your Bot Up and Running in 5 Minutes

### Step 1: Get a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get an LLM API Key

Choose one:

**Option A: OpenAI (Recommended)**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key

**Option B: Google Gemini**
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

### Step 3: Setup the Project

```bash
# Clone the repository
git clone https://github.com/inesusvet/virt-council-iaac.git
cd virt-council-iaac

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
```

### Step 4: Configure Your .env File

Edit `.env` file with your credentials:

```env
# Required: Your Telegram bot token
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Choose provider: openai or gemini
LLM_PROVIDER=openai

# If using OpenAI:
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# If using Gemini:
# GEMINI_API_KEY=AIza...
# GEMINI_MODEL=gemini-1.5-flash
```

### Step 5: Initialize Database

```bash
python setup.py
```

This will:
- Create the database
- Set up tables
- Add sample projects

### Step 6: Run the Bot

```bash
python -m app.main
```

You should see:
```
INFO - Starting application...
INFO - Database initialized
INFO - LLM provider initialized: openai
INFO - Telegram bot initialized
INFO - Application started successfully
```

### Step 7: Start Chatting!

1. Open Telegram
2. Search for your bot (use the username you set with BotFather)
3. Send `/start`
4. Try sending a message like:
   ```
   Working on implementing JWT authentication for the API
   ```

The bot will:
- Analyze your message
- Classify it
- Extract knowledge
- Link it to relevant projects
- Send you a summary!

## Common Commands

```bash
# Run tests
pytest

# Format code
black app/ tests/

# Run with make
make install  # Install dependencies
make setup    # Setup database
make run      # Run the bot
make test     # Run tests
```

## Troubleshooting

**Bot doesn't respond:**
- Check your TELEGRAM_BOT_TOKEN is correct
- Make sure the bot is running (`python -m app.main`)
- Check the console for error messages

**LLM errors:**
- Verify your API key is correct
- Check you have credits/quota available
- Make sure LLM_PROVIDER matches your API key (openai/gemini)

**Database errors:**
- Delete `data/` folder and run `python setup.py` again
- Check file permissions

## Next Steps

- Add more projects via the database or create a script
- Customize the AI prompts in `app/adapters/llm/__init__.py`
- Extend functionality by adding new use cases
- Deploy to a server for 24/7 operation

## Getting Help

- Check the main README.md for detailed documentation
- Review the code examples in the tests/ directory
- Open an issue on GitHub

Happy building! 🚀
