from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client as Tellybots, filters

from plugins.translation import Translation
from config import Config
import os
import logging
logger = logging.getLogger(__name__)


################## Saving thumbnail 🖼 ##################

@Tellybots.on_message(filters.photo & filters.incoming & filters.private)
async def save_photo(c, m):

    download_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"
    await update_thumb(m.from_user.id, m.message_id)
    await m.download(file_name=download_location)

    await m.reply_text(
        text=Translation.SAVED_CUSTOM_THUMBNAIL,
        quote=True
    )


################## Deleting permanent thumbnail 🗑 ##################

@Tellybots.on_message(filters.command("deletethumbnail") & filters.incoming & filters.private)
async def delete_thumbnail(c, m):


    
    download_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"
    thumbnail = (await get_data(m.from_user.id)).thumb_id

    if not thumbnail:
        text = Translation.NO_CUSTOM_THUMB_NAIL_FOUND
    else:
        await update_thumb(m.from_user.id, None)
        text = Translation.DELETED_CUSTOM_THUMBNAIL

    try:
        os.remove(download_location)
    except:
        pass

    await m.reply_text(
        text=text,
        quote=True
    )


################## Sending permanent thumbnail 🕶 ##################

@Tellybots.on_message(filters.command("showthumbnail") & filters.incoming & filters.private)
async def show_thumbnail(c, m):
 
    thumbnail = (await get_data(m.from_user.id)).thumb_id

    if not thumbnail:
        await m.reply_text(
            text=Translation.NO_CUSTOM_THUMB_NAIL_FOUND,
            quote=True
        )
    else:
        download_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"

        if not os.path.exists(download_location):
            thumb_nail = await c.get_messages(m.chat.id, thumbnail)
            try:
                download_location = await thumb_nail.download(file_name=download_location)
            except:
                await update_thumb(m.from_user.id, None)
                return await m.reply_text(text=Translation.NO_CUSTOM_THUMB_NAIL_FOUND, quote=True)

        await m.reply_photo(
            photo=download_location,
            caption=Translation.THUMBNAIL_CAPTION,
            parse_mode="markdown",
            quote=True
        )


################## THE END 🛑 ##################
