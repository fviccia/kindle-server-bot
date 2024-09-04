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
from pocket_api import PocketWrapper

# Telegram bot token
load_dotenv()
TOKEN = os.getenv("TOKEN")
SAVE_PATH = os.getenv("SAVE_PATH")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("httpx")
# Initialize bot state storage
user_tokens = {}

# Pocket app details
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
REDIRECT_URI = os.getenv("REDIRECT_URI")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Start by authenticating to Pocket using /auth",
    )


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    pocket_client = PocketWrapper(CONSUMER_KEY, REDIRECT_URI)

    # Step 1: Initiate the Pocket authentication
    try:
        request_token = pocket_client.authenticate_start()
        auth_url = pocket_client.get_auth_url(request_token)

        # Store the request token temporarily for this user (could also store in-memory)
        context.user_data["request_token"] = request_token

        # Send the authorization URL to the user
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Please authorize the application by visiting this URL: {auth_url} and then run /complete_auth",
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text=f"Error during authentication: {e}"
        )


async def complete_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    pocket_client = PocketWrapper(CONSUMER_KEY, REDIRECT_URI)

    # Step 2: Complete the Pocket authentication
    try:
        request_token = context.user_data.get("request_token")
        if not request_token:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Please start the authentication process first by using /auth.",
            )
            return

        access_token = pocket_client.authenticate_complete(request_token)

        # Save the access token to file for persistence
        PocketWrapper.save_access_token(access_token)

        await context.bot.send_message(
            chat_id=chat_id,
            text="Authentication complete! You can now use the Pocket features.",
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text=f"Error completing authentication: {e}"
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Load the access token from file
    access_token = PocketWrapper.load_access_token()

    if not access_token:
        await context.bot.send_message(
            chat_id=chat_id, text="Please authenticate first using /auth."
        )
        return


async def pocket_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    pocket_client = PocketWrapper(CONSUMER_KEY, REDIRECT_URI)

    # Load the access token from file
    access_token = pocket_client.load_access_token()

    if not access_token:
        await context.bot.send_message(
            chat_id=chat_id, text="Please authenticate first using /auth."
        )
        return

    try:
        # Fetch the list of articles from Pocket
        articles = pocket_client.get_articles(access_token)
        # logger.info(f"Articles : {articles}")

        if articles:
            article_list = articles[0]
            formatted_articles = "\n".join(
                [
                    f"{index + 1}. {article['resolved_title'] or 'Untitled'} - {article['resolved_url']}"
                    for index, article in enumerate(article_list["list"].values())
                ]
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Your saved Pocket articles:\n\n{formatted_articles}",
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text="No articles found in your Pocket."
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Error retrieving articles: {e}",
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    auth_handler = CommandHandler("auth", auth)
    complete_auth_handler = CommandHandler("complete_auth", complete_auth)
    pocket_list_handler = CommandHandler("pocket_list", pocket_list)

    application.add_handler(start_handler)
    application.add_handler(auth_handler)
    application.add_handler(complete_auth_handler)
    application.add_handler(pocket_list_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    application.run_polling()
