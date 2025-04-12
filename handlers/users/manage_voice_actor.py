from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states.FSM_States import ActorFSM
from database.requests import get_all_voice_actors, add_voice_actor, delete_voice_actor_by_id
from keyboards.inline.admin_panel_keyboard import create_manage_actor_inline_keyboard
from database.requests import is_admin, is_moderator
from loader import bot

router = Router()

async def has_access(tg_id):
    return await is_admin(tg_id) or await is_moderator(tg_id)

@router.callback_query(lambda c: c.data=="panel_actors")
async def panel(callback: types.CallbackQuery):
    if not await has_access(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer("Выберете пункт из админ панели: ", reply_markup=create_manage_actor_inline_keyboard())



@router.callback_query(lambda c: c.data=="panel_actor_list")
async def actor_list(callback: types.CallbackQuery):
    if not await has_access(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


    actors = await get_all_voice_actors()

    if not actors:
        await callback.message.answer("Список актёров пуст.")
        return

    text = "📜 **Список актёров:**\n\n"
    for actor in actors:
        text += f"🎭 {actor.name} — {actor.link}\n"
    await callback.message.answer(text)


'''===============================Добавление актёра===================================='''
@router.callback_query(lambda c: c.data=="panel_actor_add")
async def actor_add(callback: types.CallbackQuery, state: FSMContext):
    if not await has_access(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


    await callback.message.answer("Введите имя актёра:")
    await state.set_state(ActorFSM.name)


@router.message(StateFilter(ActorFSM.name))
async def process_actor_name(message: types.Message, state: FSMContext):
    actor_name = message.text.strip()

    if not actor_name:
        await message.answer("Имя актёра не может быть пустым. Попробуйте снова.")
        return

    #Сохраняем имя во временное хранилище
    await state.update_data(actor_name=actor_name)

    #Переход в состояние для ввода ссылки
    await message.answer("Введите ссылку на актёра:")
    await state.set_state(ActorFSM.link)


@router.message(StateFilter(ActorFSM.link))
async def process_actor_link(message: types.Message, state: FSMContext):
    actor_link = message.text.strip()

    #Получаем данные из состояния
    data = await state.get_data()
    actor_name = data.get("actor_name")

    #Сохраняем данные в базу
    try:
        success = await add_voice_actor(name=actor_name, link=actor_link)
        if not success:
            await message.answer(f"Ошибка: актёр с именем '{actor_name}' уже существует.")
            return

        await message.answer(f"Актёра '{actor_name}' успешно добавлен!")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении актёра: {e}")

    # Завершаем состояние
    await state.clear()





'''===============================Удаление актёра===================================='''

@router.callback_query(lambda c: c.data == "panel_actor_del")
async def actor_delete(callback: types.CallbackQuery):
    if not await has_access(callback.message.chat.id):
        await callback.message.answer(f"{callback.from_user.username}, у вас нет доступа к этой команде")
        return

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    actors = await get_all_voice_actors()

    #Проверяем, есть ли актёры
    if not actors:
        await callback.message.answer("Список актёров пуст.")
        return

    # Создаём клавиатуру с актёрами
    keyboard = InlineKeyboardBuilder()
    for actor in actors:
        keyboard.add(InlineKeyboardButton(text=actor.name, callback_data=f"delete_actor:{actor.id}"))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    keyboard.adjust(3)

    await callback.message.answer("Выберите актёра, которого хотите удалить:", reply_markup=keyboard.as_markup())


@router.callback_query(lambda c: c.data.startswith("delete_actor:"))
async def confirm_delete_actor(callback: types.CallbackQuery):
    """Удаление выбранного актёра."""
    actor_id = callback.data.split(":")[1]

    try:
        # Удаляем актёра из базы
        await delete_voice_actor_by_id(actor_id)

        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.message.answer("Актёр успешно удалён.")
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при удалении актёра: {e}")




