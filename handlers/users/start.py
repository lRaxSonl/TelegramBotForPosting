from  aiogram import types
from loader import dp
from data.config import ADMINS_ID

@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    if message.from_user.id in ADMINS_ID:
        await message.answer(f"{message.from_user.full_name}, вы можете опубликовать контент коммандой /newpost")
    else:
        await message.answer(f"{message.from_user.full_name}, Привет! Если тебе интересно аниме, подпишись на соц. сети нашей студии озвучки \
            \n\n<b>Телеграм</b> - <a href='https://t.me/AniLeagueTV'>AniLeague.tv</a>\n \
            \n<b>ВК</b> - <a href='https://vk.com/anileaguetv'>AniLeague.tv</a>\n \
            \n<b>Этим вы нас очень сильно поддержите!</b>")