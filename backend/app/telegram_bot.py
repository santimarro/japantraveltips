import asyncio
import logging

import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.chat_history import ChatHistory

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Define your FastAPI endpoint
FASTAPI_ENDPOINT = "http://localhost:8000/api/chat/request"

# Initialize chat history handler
chat_history = ChatHistory()


def clean_message(message: str) -> str:
    """Clean message by removing markdown tags.

    Args:
        message: Message text to clean

    Returns:
        Cleaned message text
    """
    import re

    # Remove all markdown tags
    cleaned_message = re.sub(
        r"(\*\*|__|~~|`|#|\*|_|>|-|\+|=|!|\[|\]|\(|\))", "", message
    )
    return cleaned_message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome! I'm a bot here to help you with anything related to your trip to Japan. From historical info via Wikipedia to hidden gems from r/JapanTravelTips, I've got you covered! 😊",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user_message = update.message.text
    chat_id = str(update.effective_chat.id)  # Convert to string for chat history

    # Add user message to chat history
    chat_history.save_message(chat_id, "user", user_message)

    # Get full chat history
    messages = chat_history.load_history(chat_id)

    # Send the message to the FastAPI endpoint
    async with aiohttp.ClientSession() as session:
        async with session.post(
            FASTAPI_ENDPOINT, json={"messages": messages}
        ) as response:
            if response.status == 200:
                data = await response.json()
                bot_response = data.get("result", {}).get(
                    "content", "Sorry, I didn't understand that."
                )
            else:
                bot_response = "Sorry, there was an error processing your request."

    # Add bot response to chat history
    chat_history.save_message(chat_id, "assistant", bot_response)

    # Send the response back to the user with MarkdownV2 parsing
    await context.bot.send_message(
        chat_id=chat_id,
        text=clean_message(bot_response),
    )


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /caps command."""
    text_caps = " ".join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


async def start_telegram_bot(TELEGRAM_BOT_TOKEN: str) -> None:
    """Initialize and start the telegram bot.

    Args:
        TELEGRAM_BOT_TOKEN: Bot authentication token
    """
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    start_handler = CommandHandler("start", start)
    caps_handler = CommandHandler("caps", caps)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    application.add_handler(message_handler)
    application.add_handler(unknown_handler)

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Run the bot until you hit Ctrl-C
    await application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(start_telegram_bot())
