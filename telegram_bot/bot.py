"""Simple Telegram bot for YouTube channel statistics."""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram_bot.config import BOT_TOKEN
from telegram_bot.auth import (
    has_credentials,
    get_auth_url,
    save_credentials,
    delete_credentials
)
from telegram_bot.youtube_stats import get_channel_statistics

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome {user.first_name}!\n\n"
        "I'm a YouTube Analytics Bot. I can help you get statistics for YouTube channels.\n\n"
        "🔧 *Commands:*\n"
        "/auth - Connect your Google account\n"
        "/stats - Get your channel statistics\n"
        "/help - Show this help message\n\n"
        "To get started, use /auth to connect your Google account."
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "📚 *Available Commands:*\n\n"
        "/start - Welcome message\n"
        "/auth - Authenticate with Google\n"
        "/code - Complete authentication\n"
        "/stats - Get your channel statistics\n"
        "/reset - Clear authentication\n"
        "/help - Show this help\n\n"
        "*Examples:*\n"
        "`/stats` - Last 30 days\n"
        "`/stats 2024-01` - January 2024\n"
        "`/stats 2024-02` - February 2024\n\n"
        "*Month Format:* YYYY-MM (e.g., 2024-01 for January 2024)"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /auth command - start authentication process."""
    user_id = update.effective_user.id
    
    # Check if already authenticated
    if has_credentials(user_id):
        await update.message.reply_text(
            "✅ You're already authenticated!\n"
            "Use /stats to get channel statistics."
        )
        return
    
    # Generate auth URL
    auth_url = get_auth_url(user_id)
    
    # Send URL as a clickable link
    message = (
        "🔐 *Google Authentication*\n\n"
        "1. Click the link below to authenticate with Google:\n\n"
    )
    await update.message.reply_text(message, parse_mode='Markdown')
    
    # Send URL separately to ensure it's clickable
    await update.message.reply_text(auth_url)
    
    instructions = (
        "\n2. After authorizing, Google will show you a code\n"
        "3. Send me the code using:\n"
        "`/code YOUR_AUTH_CODE`\n\n"
        "_This is a one-time setup. Your credentials will be saved securely._"
    )
    await update.message.reply_text(instructions, parse_mode='Markdown')


async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /code command - save authentication code."""
    user_id = update.effective_user.id
    
    # Check if already authenticated
    if has_credentials(user_id):
        await update.message.reply_text("✅ You're already authenticated!")
        return
    
    # Check for auth code
    if not context.args:
        await update.message.reply_text(
            "Please provide the authentication code:\n"
            "`/code YOUR_AUTH_CODE`",
            parse_mode='Markdown'
        )
        return
    
    auth_code = context.args[0]
    
    # Save credentials
    await update.message.reply_text("🔄 Saving your credentials...")
    
    if save_credentials(user_id, auth_code):
        await update.message.reply_text(
            "✅ *Authentication successful!*\n\n"
            "You can now use /stats to get channel statistics.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ *Authentication failed*\n\n"
            "The code might be invalid or expired. Please try /auth again.",
            parse_mode='Markdown'
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command - get channel statistics.
    
    Usage:
        /stats - Your channel, last 30 days
        /stats 2024-01 - Your channel, January 2024
    """
    user_id = update.effective_user.id
    
    # Check authentication
    if not has_credentials(user_id):
        await update.message.reply_text(
            "🔐 Authentication required!\n\n"
            "Please use /auth to connect your Google account first."
        )
        return
    
    # Send loading message
    loading_msg = await update.message.reply_text("🔄 Fetching statistics...")
    
    # Parse arguments for month only
    month_query = None
    
    if context.args:
        # Check if any arg looks like a month (YYYY-MM format)
        for arg in context.args:
            if len(arg) == 7 and arg[4] == '-' and arg[:4].isdigit() and arg[5:].isdigit():
                month_query = arg
                break  # Take the first valid month format
    
    # Get statistics (always for user's own channel)
    try:
        stats_text = get_channel_statistics(user_id, None, month_query)
        
        # Edit the loading message with results
        await loading_msg.edit_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        await loading_msg.edit_text(
            f"❌ Error fetching statistics\n\n"
            f"Error: {str(e)}\n\n"
            f"Please try again later or contact support."
        )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reset command - clear authentication."""
    user_id = update.effective_user.id
    
    if delete_credentials(user_id):
        await update.message.reply_text(
            "🔄 *Authentication reset!*\n\n"
            "Your credentials have been cleared.\n"
            "Use /auth to authenticate again.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "ℹ️ No credentials found to reset.\n"
            "Use /auth to authenticate."
        )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "❓ Unknown command.\n"
        "Use /help to see available commands."
    )


def main() -> None:
    """Start the bot."""
    # Check if bot token is configured
    if not BOT_TOKEN or BOT_TOKEN == 'your_telegram_bot_token_here':
        print("❌ Error: TELEGRAM_BOT_TOKEN not configured in .env file")
        print("Please add your bot token to the .env file")
        return
    
    # Create the Application with longer timeouts for network issues
    application = Application.builder().token(BOT_TOKEN).connect_timeout(30).read_timeout(30).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("code", code_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Handle unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Run the bot until user presses Ctrl-C
    print("🤖 Bot is starting...")
    print("Press Ctrl-C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()