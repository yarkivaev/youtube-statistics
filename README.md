# YouTube Statistics

A comprehensive YouTube Analytics tool with Telegram Bot interface for fetching and analyzing channel statistics.

## Features

- 📊 Comprehensive YouTube channel analytics
- 🤖 Telegram bot interface for easy access
- 📈 30-day statistics tracking
- 💰 Revenue analytics (for owned channels)
- 🌍 Geographic distribution analysis
- 📱 Multiple channel support
- 🔐 Secure OAuth 2.0 authentication

## Project Structure

```
youtube-statistics/
├── domain/                 # Domain entities and business logic
│   ├── common/            # Platform-agnostic entities
│   └── youtube/           # YouTube-specific entities
├── youtube/               # YouTube API integration
├── report/                # Report generation modules
├── telegram_bot/          # Telegram bot interface
└── main.py               # CLI interface
```

## Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)
- Google Cloud project with YouTube APIs enabled
- Telegram Bot token (for bot interface)

### Setup with Poetry

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd youtube-statistics
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Configure Google OAuth**:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com)
   - Enable YouTube Data API v3 and YouTube Analytics API
   - Create OAuth 2.0 credentials
   - Download credentials as `client_secrets.json` and place in project root

5. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

## Usage

### Activate Poetry Environment

```bash
poetry shell
```

### Command Line Interface

Run YouTube analytics from the command line:

```bash
# Get analytics for the authenticated channel
poetry run youtube-stats

# Get analytics for a specific date range
poetry run youtube-stats --range 2024-01-01:2024-12-31

# Export to JSON
poetry run youtube-stats --json

# Skip revenue data
poetry run youtube-stats --skip-revenue
```

### Telegram Bot

Start the Telegram bot:

```bash
poetry run telegram-bot
```

Or directly:

```bash
poetry run python -m telegram_bot.bot
```

#### Bot Commands

- `/start` - Welcome message and instructions
- `/auth` - Connect your Google account
- `/stats` - Get your channel statistics
- `/stats @channel` - Get statistics for any channel
- `/help` - Show available commands

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black .
```

### Linting

```bash
poetry run flake8
```

### Type Checking

```bash
poetry run mypy .
```

## Configuration

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable APIs:
   - YouTube Data API v3
   - YouTube Analytics API
4. Create credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file as `client_secrets.json`

### Telegram Bot Setup

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Add token to `.env` file

## API Documentation

### Domain Layer

The domain layer contains platform-agnostic and YouTube-specific entities:

- **Common entities**: `DateRange`, `GeographicMetrics`
- **YouTube entities**: `YouTubeChannel`, `YouTubeDailyMetrics`, `YouTubeMetrics`, etc.

### YouTube API Integration

The `youtube/` module handles all YouTube API interactions:

- `YouTubeAPIClient`: Manages authentication and API services
- `YouTubeMetricsFactory`: Fetches and aggregates all metrics

### Telegram Bot

The bot provides a simple interface for accessing YouTube statistics via Telegram:

- Supports multiple users with individual authentication
- Caches credentials securely
- Provides formatted statistics in chat

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Poetry Installation Issues

If you encounter issues with Poetry:

```bash
# Update Poetry
poetry self update

# Clear cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

### Google API Errors

- Ensure APIs are enabled in Google Cloud Console
- Check that `client_secrets.json` is valid
- Verify OAuth scopes are correct

### Telegram Bot Not Responding

- Verify bot token in `.env` file
- Check bot is running: `poetry run telegram-bot`
- Ensure network connectivity

## Support

For issues or questions, please open an issue on GitHub.