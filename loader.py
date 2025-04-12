from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from data import config

default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True)

bot = Bot(token=config.API, default=default_properties)

storage = MemoryStorage()

dp = Dispatcher(storage=storage)