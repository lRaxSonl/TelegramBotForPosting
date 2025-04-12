from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import is_admin, get_all_admins, add_admin, delete_admin_by_id
from loader import bot
from keyboards.inline.admin_panel_keyboard import create_manage_admin_inline_keyboard
from states.FSM_States import AdminFSM  # Предположим, что у вас есть такой класс FSM для админов

router = Router()

# Панель администрирования
@router.callback_query(lambda c: c.data == "panel_admins")
async def panel(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer("Выберите пункт из админ панели: ", reply_markup=create_manage_admin_inline_keyboard())


# Список админов
@router.callback_query(lambda c: c.data == "panel_admin_list")
async def admin_list(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    admins = await get_all_admins()

    if not admins:
        await callback.message.answer("Список администраторов пуст.")
        return

    text = "📜 **Список администраторов:**\n\n"
    for admin in admins:
        text += f"🕵️ {admin.tg_username} — tg_id: {admin.tg_id}\n"
    await callback.message.answer(text)


'''===============================Добавление администратора===================================='''

@router.callback_query(lambda c: c.data == "panel_admin_add")
async def admin_add(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.message.answer("Введите Telegram ID пользователя:")
    await state.set_state(AdminFSM.tg_id)


@router.message(StateFilter(AdminFSM.tg_id))
async def process_admin_id(message: types.Message, state: FSMContext):
    tg_id = message.text.strip()

    if not tg_id.isdigit():
        await message.answer("Пожалуйста, введите корректный Telegram ID.")
        return

    tg_id = int(tg_id)

    try:
        user = await bot.get_chat(tg_id)
    except Exception as e:
        await message.answer(f"Ошибка при получении информации о пользователе: {e}")
        return

    # Добавляем в базу данных
    success = await add_admin(tg_id=tg_id)

    if success:
        await message.answer(f"Администратор {user.username} c id {tg_id} был успешно добавлен!")
    else:
        await message.answer(f"Ошибка: пользователь с таким Telegram ID не найден или уже является администратором.")

    await state.clear()


'''===============================Удаление администратора===================================='''

@router.callback_query(lambda c: c.data == "panel_admin_del")
async def admin_delete(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    admins = await get_all_admins()

    if not admins:
        await callback.message.answer("Список администраторов пуст.")
        return

    keyboard = InlineKeyboardBuilder()
    for admin in admins:
        keyboard.add(InlineKeyboardButton(text=admin.tg_username, callback_data=f"deleteAdmin_{admin.id}"))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    keyboard.adjust(3)

    await callback.message.answer("Выберите администратора, которого хотите удалить", reply_markup=keyboard.as_markup())


@router.callback_query(lambda c: c.data.startswith("deleteAdmin_"))
async def delete_admin_callback(callback: types.CallbackQuery):
    admin_id = int(callback.data.split("_")[1])

    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)

        await delete_admin_by_id(admin_id)
        await callback.message.answer(f"Администратор был успешно удалён.")
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при удалении администратора: {e}")
