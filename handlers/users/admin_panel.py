from aiogram import Router, types
from aiogram.filters import Command
from keyboards.inline.admin_panel_keyboard import create_admin_inline_keyboard
from database.requests import is_admin, is_moderator
from loader import bot

router = Router()

async def has_access(tg_id):
    return await is_admin(tg_id) or await is_moderator(tg_id)

@router.message(Command("panel"))
async def panel(message: types.Message):
    if not await has_access(message.from_user.id):
        await message.answer(f"{message.from_user.full_name}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer("Выберете пункт из админ панели: ", reply_markup=create_admin_inline_keyboard())




@router.callback_query(lambda c: c.data == "back")
async def back(callback: types.CallbackQuery):
    if not has_access(callback.message.from_user.id):
        await callback.message.answer(f"{callback.message.from_user.full_name}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer("Выберете пункт из админ панели: ", reply_markup=create_admin_inline_keyboard())

