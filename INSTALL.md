# Installation Guide

## Quick Start

### 1. Install Poetry

```bash
# macOS / Linux / WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd youtube-statistics
```

### 3. Install Dependencies

```bash
poetry install
```

This will:
- Create a virtual environment
- Install all required dependencies
- Set up the project for development

### 4. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable these APIs:
   - YouTube Data API v3
   - YouTube Analytics API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download as `client_secrets.json`
   - Place in the project root directory

### 5. Configure Telegram Bot (Optional)

If you want to use the Telegram bot interface:

1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Create `.env` file in project root:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

## Running the Application

### Command Line Interface

```bash
# Activate Poetry shell (optional)
poetry shell

# Run YouTube statistics
poetry run youtube-stats

# With options
poetry run youtube-stats --range 2024-01-01:2024-12-31
poetry run youtube-stats --json
poetry run youtube-stats --skip-revenue
```

### Telegram Bot

```bash
# Start the bot
poetry run telegram-bot

# Or manually
poetry run python telegram_bot/bot.py
```

## Verification

Test that everything is installed correctly:

```bash
# Check Poetry installation
poetry --version

# Check Python version (should be 3.9+)
poetry run python --version

# List installed packages
poetry show

# Run a simple test
poetry run python -c "from domain import YouTubeChannel; print('✅ Installation successful!')"
```

## Updating Dependencies

```bash
# Update all dependencies
poetry update

# Update specific package
poetry update python-telegram-bot

# Add new dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name
```

## Troubleshooting

### Poetry Not Found

If `poetry` command is not found after installation:

```bash
# Add Poetry to PATH (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"

# Add to shell profile for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
```

### Permission Errors

```bash
# If you get permission errors during installation
poetry config virtualenvs.in-project true
poetry install
```

### Google API Issues

1. Verify `client_secrets.json` exists in project root
2. Check that required APIs are enabled in Google Cloud Console
3. First run will open browser for authentication - make sure to allow it

### Telegram Bot Issues

1. Verify bot token is correct in `.env`
2. Check that bot is not already running elsewhere
3. Ensure network connectivity to Telegram servers

## Development Setup

For contributors:

```bash
# Install with development dependencies
poetry install --with dev

# Run formatters
poetry run black .

# Run linters
poetry run flake8

# Run type checker
poetry run mypy .

# Run tests (when available)
poetry run pytest
```

## Virtual Environment

Poetry automatically manages virtual environments:

```bash
# Show virtual environment info
poetry env info

# List available environments
poetry env list

# Remove current environment
poetry env remove python

# Use specific Python version
poetry env use python3.9
```

## Deployment

For production deployment:

```bash
# Build distributable package
poetry build

# Install in production (without dev dependencies)
poetry install --without dev

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt --without-hashes
```