import asyncio

from loader import bot, dp
from utils.notify_admins import on_startup_notify, on_shutdown_notify
from utils.set_bot_commands import set_default_commands
from handlers.users import router as user_router
from database.models import async_main


async def main():
    dp.include_router(user_router)

    await set_default_commands(bot)
    await on_startup_notify(bot)

    await async_main()

    try:
        await dp.start_polling(bot)

    finally:
        await on_shutdown_notify(bot)
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот был остановлен!")