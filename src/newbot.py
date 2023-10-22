#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""

from scholarly import scholarly, ProxyGenerator # pip install scholarly
pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)
import logging
from decouple import config
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def search_author_by_id(id):
    print("author id: ", id)
    try:
        search_results = scholarly.search_author_id(id)
        if search_results:
            return search_results
        else:
            return "No author found for the given id."
    except Exception as e:
        print(e)
        print("An error occurred while searching for the author on Google Scholar.")

async def search_authors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = context.args
    if not query:
        await update.message.reply_text("Please provide a query to search for the author.")
        return

    query = " ".join(query)
    await update.message.reply_text('Searching for the author...')

    author_info = scholarly.search_author(query)
    cnt = 0
    authors = []
    while(cnt<10):
        cnt += 1
        try: 
            authors.append(next(author_info))
        except:
            print("error")
    print(authors)
    for author in authors:
        print(author)
        await update.message.reply_text(author)
    keyboard = list(map(lambda author: [InlineKeyboardButton(author['name'], callback_data=f"id:{author['scholar_id']}")], authors))
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    # await update.message.reply_text(author_info)
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    cmd = query.data.split(":")[0]
    if cmd:
        if cmd == "id":
            author_id = query.data.split(":")[1]
            author = await search_author_by_id(author_id)
            keyboards = []
            for key in author:
                keyboards.append([InlineKeyboardButton(f"key: {author[key]}", callback_data=f"{key}")])
            reply_markup = InlineKeyboardMarkup(keyboards)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup)
            await query.answer()
            await query.edit_message_text(json.dumps(author, indent = 4)  )
    else:
        text=f"Selected option: {query.data}"
        await query.answer()
        await query.edit_message_text(text=f"Selected option: {query.data}")
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config('BOT_TOKEN')).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search_author", search_authors))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()