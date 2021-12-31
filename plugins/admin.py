
# (c) @AbirHasan2005

import traceback
import os

from pyrogram import Client as Tellybots
from pyrogram import filters


from database.access import tellybots

@Tellybots.on_message(filters.private & filters.command('total'))
async def sts(c, m):
    if m.from_user.id != Config.OWNER_ID:
        return 
    total_users = await tellybots.total_users_count()
    await m.reply_text(text=f"Total user(s) {total_users}", quote=True)

