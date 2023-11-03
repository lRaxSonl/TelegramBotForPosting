import logging
from aiogram import dispatcher
from data.config import ADMINS_ID

async def on_startup_notify(dp: dispatcher):
    for admin in ADMINS_ID:
        try:
            await dp.bot.send_message(chat_id = admin, text="Бот запущен")
        except Exception as err:
            logging.exception(err)
            
async def on_shutdown_notify(dp: dispatcher):
    for admin in ADMINS_ID:
        try:
            await dp.bot.send_message(chat_id = admin, text="Бот выключен")
        except Exception as err:
            logging.exception(err)