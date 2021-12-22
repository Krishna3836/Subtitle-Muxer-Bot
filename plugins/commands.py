import os
if bool(os.environ.get("WEBHOOK", False)):
    from config import Config
else:
    from config import Config
from script import Script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.adduser import AddUser

@Client.on_message(filters.command(["start"]) & filters.private)
async def start(bot, update):
    await AddUser(bot, update)
    await update.reply_text(
        text=Script.START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=Script.START_BUTTONS
    )
