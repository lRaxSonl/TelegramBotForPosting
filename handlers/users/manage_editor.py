from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.inline.admin_panel_keyboard import create_manage_editor_inline_keyboard
from database.requests import is_admin, is_moderator, get_all_editors, add_editor, delete_editor_by_id
from loader import bot
from states.FSM_States import EditorFSM

router = Router()

async def has_access(tg_id):
    return await is_admin(tg_id) or await is_moderator(tg_id)

@router.callback_query(lambda c: c.data=="panel_editors")
async def panel(callback: types.CallbackQuery):
    if not await has_access(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer("Выберете пункт из админ панели: ", reply_markup=create_manage_editor_inline_keyboard())


#Список монтажёров
@router.callback_query(lambda c: c.data == "panel_editor_list")
async def editor_list(callback: types.CallbackQuery):
    if not await has_access(callback.from_user.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    editors = await get_all_editors()

    if not editors:
        await callback.message.answer("Список монтажёров пуст.")
        return

    text = "📜 **Список монтажёров:**\n\n"
    for editor in editors:
        text += f"🎬 {editor.name} — {editor.link}\n"

    await callback.message.answer(text)


'''===============================Добавление монтажёра===================================='''
@router.callback_query(lambda c: c.data == "panel_editor_add")
async def editor_add(callback: types.CallbackQuery, state: FSMContext):
    if not await has_access(callback.from_user.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.message.answer("Введите имя монтажёра:")
    await state.set_state(EditorFSM.name)


@router.message(StateFilter(EditorFSM.name))
async def process_editor_name(message: types.Message, state: FSMContext):
    editor_name = message.text.strip()

    if not editor_name:
        await message.answer("Имя монтажёра не может быть пустым. Попробуйте снова.")
        return

    # Сохраняем имя во временное хранилище
    await state.update_data(editor_name=editor_name)

    # Переход к следующему шагу для ввода ссылки
    await message.answer("Введите ссылку на монтажёра:")
    await state.set_state(EditorFSM.link)


@router.message(StateFilter(EditorFSM.link))
async def process_editor_link(message: types.Message, state: FSMContext):
    editor_link = message.text.strip()

    #Получаем данные из состояния
    data = await state.get_data()
    editor_name = data.get("editor_name")

    #Сохраняем данные в базу
    try:
        success = await add_editor(name=editor_name, link=editor_link)
        if not success:
            await message.answer(f"Ошибка: монтажёра с именем '{editor_name}' уже существует.")
            return

        await message.answer(f"Монтажёр '{editor_name}' успешно добавлен!")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении монтажёра: {e}")

    #Завершаем состояние
    await state.clear()



'''===============================Удаление монтажёра===================================='''

@router.callback_query(lambda c: c.data == "panel_editor_del")
async def editor_delete(callback: types.CallbackQuery):
    if not await has_access(callback.from_user.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    editors = await get_all_editors()

    if not editors:
        await callback.message.answer("Список монтажёров пуст.")
        return


    keyboard = InlineKeyboardBuilder()
    for editor in editors:
        keyboard.add(InlineKeyboardButton(text=editor.name, callback_data=f"delete_{editor.id}"))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    keyboard.adjust(3)

    await callback.message.answer("Выберите монтажёра, которого хотите удалить", reply_markup=keyboard.as_markup())


@router.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_editor_callback(callback: types.CallbackQuery):
    editor_id = int(callback.data.split("_")[1])

    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)

        await delete_editor_by_id(editor_id)
        await callback.message.answer(f"Монтажёр был успешно удалён.")
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при удалении монтажёра: {e}")