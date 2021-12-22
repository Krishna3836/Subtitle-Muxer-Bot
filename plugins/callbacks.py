import os

if bool(os.environ.get("WEBHOOK", False)):
    from config import Config
else:
    from config import Config

from script import Script
from pyrogram import Client as Bot
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import InlineKeyboardButton


@Bot.on_callback_query()
async def button(bot, update):
    if update.data == "home":
        await update.message.edit_text(
            text=Script.START_TEXT.format(update.from_user.mention),
            reply_markup=Script.START_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=Script.HELP_TEXT,
            reply_markup=Script.HELP_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=Script.ABOUT_TEXT.format((await bot.get_me()).username),
            reply_markup=Script.ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    else:
        await update.message.delete()
