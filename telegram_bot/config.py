"""Configuration for Telegram bot."""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Google OAuth configuration
CLIENT_SECRETS_FILE = 'client_secrets.json'
SCOPES = [
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/youtube.readonly'
]

# Token storage
TOKEN_DIR = 'telegram_bot/tokens'

# Ensure token directory exists
os.makedirs(TOKEN_DIR, exist_ok=True)