from pyrogram import Client
from database.access import tellybots
from pyrogram.types import Message


async def AddUser(bot: Client, update: Message):
    if not await tellybots.is_user_exist(update.from_user.id):
           await tellybots.add_user(update.from_user.id)

