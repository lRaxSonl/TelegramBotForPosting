from  aiogram import types, Router
from aiogram.filters import CommandStart
from database.requests import is_admin, add_user, is_moderator

router = Router()

@router.message(CommandStart())
async def command_start(message: types.Message):
    if (await is_admin(message.from_user.id) or await is_moderator(message.from_user.id)):
        await message.answer(f"{message.from_user.username}, вы можете опубликовать контент коммандой /newpost")
    else:
        await add_user(tg_id=message.from_user.id, tg_username=message.from_user.username)
        await message.answer(f"{message.from_user.username}, Привет! Если тебе интересно аниме, подпишись на соц. сети нашей студии озвучки \
            \n\n<b>Телеграм</b> - <a href='https://t.me/AniLeagueTV'>AniLeague.tv</a>\n \
            \n<b>ВК</b> - <a href='https://vk.com/anileaguetv'>AniLeague.tv</a>\n \
            \n<b>Этим вы нас очень сильно поддержите!</b>")