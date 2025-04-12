from aiogram import Router, types

router = Router()


@router.message()
async def error_handler(message: types.Message):
    await message.answer("Я не знаю такое команды.")