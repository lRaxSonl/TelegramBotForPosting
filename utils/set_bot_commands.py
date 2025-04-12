from aiogram import types

async def set_default_commands(bot):
    await bot.set_my_commands([
        types.BotCommand(command='start', description='Запустить бота'),
        types.BotCommand(command='newpost', description='Опубликовать пост'),
        types.BotCommand(command='panel', description="Вызвать админ панель")
    ])