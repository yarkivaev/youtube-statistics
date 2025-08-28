# Telegram Bot for YouTube Statistics

A simple Telegram bot that provides YouTube channel statistics directly in chat.

## Features

- 🔐 Google OAuth authentication
- 📊 Channel statistics (subscribers, views, watch time)
- 💰 Revenue data (for your own channel)
- 🌍 Geographic distribution
- 📈 30-day metrics
- 🔍 Search channels by @handle, name, or ID

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Save the bot token you receive

### 2. Configure Google OAuth

You already have `client_secrets.json` configured for YouTube API access.

### 3. Install Dependencies

Using Poetry (recommended):
```bash
poetry install
```

Or using pip:
```bash
pip install python-telegram-bot python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4. Configure Environment

Edit the `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Replace `your_bot_token_here` with your actual bot token from BotFather.

### 5. Run the Bot

Using Poetry:
```bash
poetry run telegram-bot
```

Or directly:
```bash
poetry run python telegram_bot/bot.py
```

## Usage

### Commands

- `/start` - Welcome message and instructions
- `/auth` - Connect your Google account
- `/code <auth_code>` - Complete authentication
- `/stats` - Get your channel statistics
- `/stats @channel` - Get statistics for any channel
- `/help` - Show available commands

### Examples

```
/stats
# Shows your authenticated channel's statistics

/stats @mkbhd
# Shows statistics for MKBHD's channel

/stats LinusTechTips
# Searches for LinusTechTips channel

/stats UCXuqSBlHAE6Xw-yeJA0Tunw
# Direct lookup by channel ID
```

## Authentication Flow

1. User sends `/auth`
2. Bot provides Google OAuth URL
3. User clicks URL and authorizes access
4. Google shows an authorization code
5. User sends `/code YOUR_CODE` to bot
6. Bot saves credentials for future use

## Statistics Provided

- 👥 Subscriber count and changes
- 👁 Total views and breakdown by content type
- ⏱ Watch time in hours
- 📈 New vs lost subscribers
- 💰 Revenue (own channel only)
- 🌍 Top countries by views

## Security

- Credentials are stored locally in `telegram_bot/tokens/`
- Each user has separate credentials
- Tokens are automatically refreshed when expired
- No database or external storage required

## Troubleshooting

### Bot doesn't respond
- Check that the bot token is correctly set in `.env`
- Ensure the bot is running (`python telegram_bot/bot.py`)

### Authentication fails
- Make sure `client_secrets.json` exists and is valid
- Check that YouTube Data API v3 and YouTube Analytics API are enabled in Google Cloud Console

### Statistics not loading
- Verify the channel exists and is accessible
- Check that authentication was successful
- Try re-authenticating with `/auth`

## File Structure

```
telegram_bot/
├── bot.py              # Main bot logic
├── auth.py             # Google OAuth handling
├── youtube_stats.py    # Statistics fetcher
├── config.py           # Configuration
├── tokens/             # User credentials (created automatically)
└── requirements.txt    # Python dependencies
```

## Notes

- First-time setup requires Google authentication
- Credentials are cached, so authentication is one-time only
- Revenue data is only available for your own channel
- The bot reuses existing YouTube analytics code from the main project