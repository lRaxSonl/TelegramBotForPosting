import logging
from aiogram import Bot
from data.config import ADMINS_ID
from database.requests import get_all_admins

async def get_admins() -> list[int]:
    admins = []
    admins_entities = await get_all_admins()

    if not admins_entities:
        admins_entities = []

    for admin in admins_entities:
        admins.append(admin.tg_id)

    for id in ADMINS_ID:
        if id not in admins:
            admins.append(id)

    return admins


async def on_startup_notify(bot: Bot):
    admins = await get_admins()

    for admin in admins:
        try:
            await bot.send_message(chat_id = admin, text="Бот запущен")
        except Exception as err:
            logging.exception(err)
            
async def on_shutdown_notify(bot: Bot):
    admins = await get_admins()

    for admin in admins:
        try:
            await bot.send_message(chat_id = admin, text="Бот выключен")
        except Exception as err:
            logging.exception(err)