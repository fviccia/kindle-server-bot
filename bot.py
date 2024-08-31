import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import filters
from telegram.ext import MessageHandler
from utils import save_url_to_file

# Telegram bot token
load_dotenv()
TOKEN = os.getenv("TOKEN")
SAVE_PATH = os.getenv("SAVE_PATH")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Send and url to process."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Processing url: {url}"
    )
    save_url_to_file(url, SAVE_PATH)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Processing Finished"
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    application.run_polling()
