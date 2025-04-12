from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.inline.admin_panel_keyboard import create_manage_tag_inline_keyboard
from database.requests import is_admin, is_moderator, add_tag, get_all_tags, delete_tag_by_id
from loader import bot
from states.FSM_States import TagFSM

router = Router()

async def has_access(tg_id):
    return await is_admin(tg_id) or await is_moderator(tg_id)


@router.callback_query(lambda c: c.data=="panel_tags")
async def panel(callback: types.CallbackQuery):
    if not await has_access(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer("Выберете пункт из админ панели: ", reply_markup=create_manage_tag_inline_keyboard())



@router.callback_query(lambda c: c.data=="panel_tag_list")
async def tag_list(callback: types.CallbackQuery):
    if not await has_access(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


    tags = await get_all_tags()

    if not tags:
        await callback.message.answer("Список тегов пуст.")
        return

    text = "📜 **Список актёров:**\n\n"
    for tag in tags:
        text += f"🧷 #{tag.name}\n"
    await callback.message.answer(text)


'''===============================Создание тега===================================='''
@router.callback_query(lambda c: c.data == "panel_tag_add")
async def tag_add(callback: CallbackQuery, state: FSMContext):
    if not await has_access(callback.from_user.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    # Переход к состоянию для ввода имени тега
    await callback.message.answer("Введите имя нового тега:")
    await state.set_state(TagFSM.name)




@router.message(StateFilter(TagFSM.name))
async def process_tag_name(message: types.Message, state: FSMContext):
    tag_name = message.text.strip()

    if not tag_name:
        await message.answer("Имя тега не может быть пустым. Попробуйте снова.")
        return

    try:
        success = await add_tag(name=tag_name)

        if not success:
            await message.answer(f"Ошибка: такой тег уже существует.")
            return

        await message.answer(f"Вы успешно создали тег: {tag_name}!")
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании тега: {e}")



'''===============================Удаление тега===================================='''

@router.callback_query(lambda c: c.data == "panel_tag_del")
async def tag_delete(callback: types.CallbackQuery):
    if not await has_access(callback.from_user.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    tags = await get_all_tags()

    if not tags:
        await callback.message.answer("Список монтажёров пуст.")
        return


    keyboard = InlineKeyboardBuilder()
    for tag in tags:
        keyboard.add(InlineKeyboardButton(text=tag.name, callback_data=f"deleteTag_{tag.id}"))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    keyboard.adjust(3)

    await callback.message.answer("Выберите тег, который хотите удалить", reply_markup=keyboard.as_markup())


@router.callback_query(lambda c: c.data.startswith("deleteTag_"))
async def delete_tag_callback(callback: types.CallbackQuery):
    tag_id = int(callback.data.split("_")[1])

    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)

        await delete_tag_by_id(tag_id)
        await callback.message.answer(f"Тег был успешно удалён.")
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при удалении Тега: {e}")