from aiogram import types
from aiogram.types import CallbackQuery
from loader import dp
from data.config import ADMINS_ID, CHANNEL_ID
from data.member_list import members, editors
from keyboards.inline.members_keyboard import inline_members_kb, inline_editors_kb, inline_confirmation_kb
from states.FSM_States import PostForm
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

#Определение функции для проверки администратора
def is_admin(user_id):
    return user_id in ADMINS_ID

@dp.message_handler(commands=['newpost'])
async def newpost(message: types.Message):
    if is_admin(message.from_user.id):
        #===========================================================================
        #Видео
        await message.answer("<b>Отправьте видео для загрузки</b>")
        await PostForm.video1.set()
        
        @dp.message_handler(content_types=types.ContentType.VIDEO, state=PostForm.video1)
        async def video1(message: types.Message, state: FSMContext):
            await state.update_data(video1=message.video.file_id)
            
            global video1
            video1 = await state.get_data() #Видео
            await message.answer("<b>Введите название, сезон и серию тайтла</b>")
            await PostForm.name.set()
        
        #===========================================================================
        #Название
        @dp.message_handler(content_types=types.ContentType.TEXT, state=PostForm.name)
        async def video1(message: types.Message, state: FSMContext):
            await state.update_data(name=message.text)
            
            global name
            name = await state.get_data() #Название тайтла
            await message.answer("<b>Введите жанры тайтла</b>")
            await PostForm.genres.set()
            
        #===========================================================================
        #Жанры
        @dp.message_handler(content_types=types.ContentType.TEXT, state=PostForm.genres)
        async def genres(message: types.Message, state: FSMContext):
            await state.update_data(genres=message.text)
            
            global genres
            genres = await state.get_data() #Жанр тайтла
            await message.answer("<b>Отправьте ссылку на тайтл на сайте Aniu.ru</b>")
            
            await PostForm.aniuRu_link.set()
            
        #===========================================================================
        #Ссылка на ресурсы
        @dp.message_handler(content_types=types.ContentType.TEXT, state=PostForm.aniuRu_link)
        async def aniuRu_link(message: types.Message, state: FSMContext):
            await state.update_data(aniuRu_link=message.text)
            
            global aniuRu_link
            aniuRu_link = await state.get_data() #Ссылка на Aniu.ru
            await message.answer("<b>Отправьте ссылку на тайтл на сайте Kodik</b>")
            
            await PostForm.kodik_link.set()
            
            
        @dp.message_handler(content_types=types.ContentType.TEXT, state=PostForm.kodik_link)
        async def kodik_link(message: types.Message, state: FSMContext):
            await state.update_data(kodik_link=message.text)
            
            global kodik_link
            kodik_link = await state.get_data() #Ссылка на Kodik
            await message.answer("<b>Выберете дабберов из списка ниже</b>", reply_markup=inline_members_kb)
            
            await PostForm.members.set()

    else:
        await message.answer(f"{message.from_user.full_name}, у вас нет доступа к этой команде")
        
        

#Список Дабберов
@dp.callback_query_handler(lambda c: c.data in members, state=PostForm.members)
async def add_members(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        data = await state.get_data() #Дабберы
        global members_arr
        members_arr = data.get("members_arr", [])
        selected_member = callback.data

        if selected_member not in members_arr:
            members_arr.append(selected_member)
            await state.update_data(members_arr=members_arr)
            await callback.answer("Даббер добавлен")
        else:
            await callback.answer("Даббер уже был добавлен")

@dp.callback_query_handler(text="next", state=PostForm.members)
async def next1(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        data = await state.get_data()
        members_arr = data.get("members_arr", [])
        #await callback.message.answer(f"{name['name']}, {genres['name']}")
        await callback.message.answer("Выбранные дабберы: " + ', '.join(members_arr))
        
        await callback.message.answer("Выберете <b>монтажёров</b> из списка ниже", reply_markup=inline_editors_kb)
        
        await dp.bot.delete_message(callback.from_user.id, callback.message.message_id)
        await PostForm.editors.set()
        
        
        
        
#Список Монтажёров
@dp.callback_query_handler(lambda c2: c2.data in editors, state=PostForm.editors)
async def add_members(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        data = await state.get_data() #Монтажёры
        global editors_arr
        editors_arr = data.get("editors_arr", [])
        selected_editor = callback.data

        if selected_editor not in editors_arr:
            editors_arr.append(selected_editor)
            await state.update_data(editors_arr=editors_arr)
            await callback.answer("Монтажёр добавлен")
        else:
            await callback.answer("Монтажёр уже был добавлен")
            

@dp.callback_query_handler(text="next2", state=PostForm.editors)
async def next1(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        data = await state.get_data()
        editors_arr = data.get("editors_arr", [])
        await callback.message.answer(f"{name['name']}, {genres['name']}")
        await callback.message.answer("Выбранные монтажёры: " + ', '.join(editors_arr))
        
        await dp.bot.delete_message(callback.from_user.id, callback.message.message_id)
        
        #Составление поста
        #=========================================================
        global post
        
        #Название тайтла
        post = f"{name['name']} <a href='https://vk.com/anileaguetv'>AniLeague.tv</a>\n\n"
        
        #Дабберы
        post += "Озвучивали:\n"
        for member in members_arr:
            member_link = members.get(member) #Ссылки для Дабберов
            if member_link:
                post += f"►<a href='{member_link}'>{member}</a>\n"
                
        #Монтажёры
        post += f"\nТайминг и работа со звуком: \n"
        for editor in editors_arr:
            editor_link = editors.get(editor) #Ссылки для Монтажёров
            if editor_link:
                post += f"►<a href='{editor_link}'>{editor}</a>\n"
        
        #Жанры 
        post += f"\nЖанры: {genres['genres']}\n\n"
        
        #Ссылки на сайты с аниме
        aniuRuLink = aniuRu_link['aniuRu_link']
        kodikLink = kodik_link['kodik_link']
        post += f"►<a href='{aniuRuLink}'>Aniu.ru</a>\n"
        post += f"►<a href='{kodikLink}'>Kodik</a>\n"
        #=========================================================
        
    
        await callback.message.answer("<b>Вы создали пост:</b>")
        await dp.bot.send_video(chat_id=callback.from_user.id, video=video1['video1'], caption=post)
        
        await callback.message.answer("Хотите его опубликовать?", reply_markup=inline_confirmation_kb)
        await state.finish()



@dp.callback_query_handler(Text(startswith='res_'))
async def public_content(callback: CallbackQuery):
    if is_admin(callback.from_user.id):
        if callback.data == 'res_yes':
            await dp.bot.send_video(chat_id=CHANNEL_ID, video=video1['video1'], caption=post)
            await callback.message.answer("✅<b>Пост опубликован</b>✅")
            await dp.bot.delete_message(callback.from_user.id, callback.message.message_id)
            
        elif callback.data == 'res_no':
            await callback.message.answer("<b>Публикация поста была отменёна</b>")
            await dp.bot.delete_message(callback.from_user.id, callback.message.message_id)