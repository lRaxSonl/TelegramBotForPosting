from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import is_admin, get_all_moderators, add_moderator, delete_moderator_by_id
from loader import bot
from keyboards.inline.admin_panel_keyboard import create_manage_moderator_inline_keyboard
from states.FSM_States import ModeratorFSM


router = Router()

@router.callback_query(lambda c: c.data=="panel_moderators")
async def panel(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer("Выберете пункт из админ панели: ", reply_markup=create_manage_moderator_inline_keyboard())



@router.callback_query(lambda c: c.data=="panel_moderator_list")
async def moderator_list(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


    moderators = await get_all_moderators()

    if not moderators:
        await callback.message.answer("Список модераторов пуст.")
        return

    text = "📜 **Список модераторов:**\n\n"
    for moderator in moderators:
        text += f"👮 {moderator.tg_username} — tg_id: {moderator.tg_id}\n"
    await callback.message.answer(text)



'''===============================Добавление модератора===================================='''
@router.callback_query(lambda c: c.data=="panel_moderator_add")
async def moderator_add(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.message.answer("Введите телеграм ид пользователя:")
    await state.set_state(ModeratorFSM.tg_id)


@router.message(StateFilter(ModeratorFSM.tg_id))
async def process_moderator_id(message: types.Message, state: FSMContext):
    tg_id = message.text.strip()

    if not tg_id.isdigit():
        await message.answer("Пожалуйста, введите корректный Telegram ID.")
        return

    tg_id = int(tg_id)

    #Проверяем, существует ли такой пользователь
    try:
        user = await bot.get_chat(tg_id)
    except Exception as e:
        await message.answer(f"Ошибка при получении информации о пользователе: {e}")
        return

    #Добавляем в базу данных
    success = await add_moderator(tg_id=tg_id)

    if success:
        await message.answer(f"Модератор {user.username} c id {tg_id} был успешно добавлен!")
    else:
        await message.answer(f"Ошибка: пользователь с таким Telegram ID не найден или уже является модератором.")

    await state.clear()


'''===============================Удаление модератора===================================='''

@router.callback_query(lambda c: c.data == "panel_moderator_del")
async def moderator_delete(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    moderators = await get_all_moderators()

    if not moderators:
        await callback.message.answer("Список модераторов пуст.")
        return


    keyboard = InlineKeyboardBuilder()
    for moderator in moderators:
        keyboard.add(InlineKeyboardButton(text=moderator.tg_username, callback_data=f"deleteModerator_{moderator.id}"))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    keyboard.adjust(3)

    await callback.message.answer("Выберите модератора, которого хотите удалить", reply_markup=keyboard.as_markup())


@router.callback_query(lambda c: c.data.startswith("deleteModerator_"))
async def delete_moderator_callback(callback: types.CallbackQuery):
    moderator_id = int(callback.data.split("_")[1])

    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)

        await delete_moderator_by_id(moderator_id)
        await callback.message.answer(f"Модератора был успешно удалён.")
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при удалении модератора: {e}")

