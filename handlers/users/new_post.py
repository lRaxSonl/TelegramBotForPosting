from aiogram import types, F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from data.config import CHANNEL_ID
from database.requests import *
from keyboards.inline.members_keyboard import create_members_keyboard, create_editors_keyboard, \
    create_confirmation_keyboard, inline_confirmation_kb, create_tags_keyboard
from states.FSM_States import PostForm
from loader import bot

router = Router()

async def has_access(tg_id):
    return await is_admin(tg_id) or await is_moderator(tg_id)


async def get_entities_by_names(names, entity_type):
    """
    Получает данные о сущностях (дабберы или редакторы) из базы данных по их именам.

    :param names: Список имен сущностей.
    :param entity_type: Тип сущности ('voice_actor' или 'editor').
    :return: Список словарей с данными о сущностях.
    """
    entities = []
    for name in names:
        try:
            if entity_type == "editors":
                entity = await get_editor_by_name(name)
            elif entity_type == "members":
                entity = await get_voice_actor_by_name(name)
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")

            if entity:
                entities.append(entity)
            else:
                logger.warning(f"Entity '{name}' not found.")
        except Exception as e:
            logger.error(f"Error fetching {entity_type} '{name}': {e}")
    return entities


#Новый пост
#=============================Забираем видео======================================
@router.message(Command("newpost"))
async def newpost(message: types.Message, state: FSMContext):
    if not await has_access(message.from_user.id):
        await message.answer(f"{message.from_user.full_name}, у вас нет доступа к этой команде")
        return

    await message.answer("<b>Отправьте видео для загрузки</b>")
    await state.set_state(PostForm.video1)



#=============================Забираем название======================================
@router.message(PostForm.video1, F.content_type == "video")
async def get_video(message: types.Message, state: FSMContext):
    await state.update_data(video1=message.video.file_id)
    await message.answer("<b>Введите название, сезон и серию тайтла</b>")
    await state.set_state(PostForm.name)




#=============================Забираем жанры======================================
@router.message(StateFilter(PostForm.name), F.text)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("<b>Введите жанры тайтла</b>")
    await state.set_state(PostForm.genres)




#=============================Забираем ссылки======================================
@router.message(StateFilter(PostForm.genres), F.text)
async def get_genres(message: types.Message, state: FSMContext):
    await state.update_data(genres=message.text)
    await message.answer("<b>Отправьте ссылку на тайтл на сайте Aniu.ru</b>")
    await state.set_state(PostForm.aniuRu_link)



@router.message(StateFilter(PostForm.aniuRu_link), F.text)
async def get_aniu_link(message: types.Message, state: FSMContext):
    await state.update_data(aniuRu_link=message.text)
    await message.answer("<b>Отправьте ссылку на тайтл на сайте Kodik</b>")
    await state.set_state(PostForm.kodik_link)

@router.message(StateFilter(PostForm.kodik_link), F.text)
async def get_kodik_link(message: types.Message, state: FSMContext):

    inline_members_kb = await create_members_keyboard()
    await state.update_data(kodik_link=message.text)
    await message.answer("<b>Выберете дабберов из списка ниже</b>", reply_markup=inline_members_kb)
    await state.set_state(PostForm.members)

#=============================Дабберы======================================
@router.callback_query(StateFilter(PostForm.members))
async def select_member(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    members_arr = data.get("members_arr", [])
    selected_member = callback.data

    if selected_member == "next":
        await next_to_editors(callback, state)
        return

    if not callback.data.startswith("member_"):
        return

    selected_member = selected_member.replace("member_", "")

    if selected_member not in members_arr:
        members_arr.append(selected_member)
        await state.update_data(members_arr=members_arr)
        await callback.answer("Даббер добавлен")
    else:
        await callback.answer("Даббер уже был добавлен")


@router.callback_query(StateFilter(PostForm.members), lambda c: c.data == "next")
async def next_to_editors(callback: CallbackQuery, state: FSMContext):
    inline_editors_kb = await create_editors_keyboard()

    data = await state.get_data()
    members_arr = data.get("members_arr", [])


    #Удаляем список дабберов
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)



    await callback.message.answer("Выбранные дабберы: " + ', '.join(members_arr))
    await callback.message.answer("<b>Выберете монтажёров из списка ниже</b>", reply_markup=inline_editors_kb)

    await state.set_state(PostForm.editors)


#=============================Монтажёры======================================
@router.callback_query(StateFilter(PostForm.editors))
async def select_editor(callback: CallbackQuery, state: FSMContext):
    inline_editors_kb = await create_editors_keyboard()

    data = await state.get_data()
    editors_arr = data.get("editors_arr", [])
    selected_editor = callback.data

    if selected_editor == "next2":
        await select_tags(callback, state)
        return

    if not callback.data.startswith("editor_"):
        return

    selected_editor = selected_editor.replace("editor_", "")

    if selected_editor not in editors_arr:
        editors_arr.append(selected_editor)
        await state.update_data(editors_arr=editors_arr)
        await callback.answer("Монтажёр добавлен")
    else:
        await callback.answer("Монтажёр уже был добавлен")


#=============================Теги======================================
@router.callback_query(StateFilter(PostForm.editors), lambda c: c.data == "next2")
async def select_tags(callback: CallbackQuery, state: FSMContext):

    tag_keyboard = await create_tags_keyboard()

    data = await state.get_data()

    #Удаляем список монтажёров
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.message.answer("<b>Теперь выберите теги:</b>", reply_markup=tag_keyboard)
    await state.set_state(PostForm.tags)



@router.callback_query(StateFilter(PostForm.tags))
async def select_tag_second_step(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("res_"):
        await handle_publication(callback, state)
        return

    if callback.data == "next3":
        await finalize_post(callback, state)
        return

    if not callback.data.startswith("tag|"):
        return

    data = await state.get_data()
    tags_arr = data.get("tags_arr", [])

    selected_tag = callback.data
    selected_tag = selected_tag.replace("tag|", "")



    #Если тег еще не добавлен
    if selected_tag not in tags_arr:
        tags_arr.append(selected_tag)
        await state.update_data(tags_arr=tags_arr)
        await callback.answer(f"Тег #{selected_tag} добавлен")
    else:
        await callback.answer(f"Тег #{selected_tag} уже был добавлен")


@router.callback_query(StateFilter(PostForm.tags), lambda c: c.data == "next3")
async def finalize_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    #Удаляем список тегов
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    global video_id
    #Извлекаем данные
    video_id = data.get("video1")
    name = data.get("name")
    genres = data.get("genres")
    aniu_link = data.get("aniuRu_link")
    kodik_link = data.get("kodik_link")
    members_arr = data.get("members_arr", [])
    editors_arr = data.get("editors_arr", [])
    tags_arr = data.get("tags_arr", [])  # Получаем выбранные теги

    if not members_arr or not editors_arr:
        await callback.message.answer("<b>Необходимо выбрать дабберов и монтажёров</b>")
        return

    members = await get_entities_by_names(members_arr, "members")

    members_list = "\n".join(
        f"► <a href='{member.link}'>{member.name}</a>"
        for member in members
    )

    editors = await get_entities_by_names(editors_arr, "editors")

    editors_list = "\n".join(
        f"► <a href='{editor.link}'>{editor.name}</a>"
        for editor in editors if editor is not None and editor.link and editor.name
    )

    # Формирование поста с добавленными тегами
    global post
    post_template = (
        "{name} <a href='https://vk.com/anileaguetv'>AniLeague.tv</a>\n\n"
        "Озвучивали:\n{members}\n\n"
        "Тайминг и работа со звуком:\n{editors}\n\n"
        "Жанры: {genres}\n\n"
        "► <a href='{aniu_link}'>Aniu.ru</a>\n"
        "► <a href='{kodik_link}'>Kodik</a>\n\n"
        "{tags}"  # Добавляем строку для тегов
    )

    tags = " ".join([f"#{tag}" for tag in tags_arr]) if tags_arr else ""

    post = post_template.format(
        name=name,
        members=members_list,
        editors=editors_list,
        genres=genres,
        aniu_link=aniu_link,
        kodik_link=kodik_link,
        tags=tags  # Вставляем теги в пост
    )

    await state.clear()
    await callback.message.answer("<b>Вы создали пост:</b>")
    await bot.send_video(chat_id=callback.from_user.id, video=video_id, caption=post)
    await callback.message.answer("Хотите его опубликовать?", reply_markup=inline_confirmation_kb)

#=============================Запрос на публикацию======================================
@router.callback_query(F.data.startswith("res_"))
async def handle_publication(callback: CallbackQuery):
    if callback.data == "res_yes":
        await bot.send_video(chat_id=CHANNEL_ID, video=video_id, caption=post)
        await callback.message.answer("✅<b>Пост опубликован</b>✅")

        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data == "res_no":
        await callback.message.answer("<b>Публикация поста была отменена</b>")

        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
