from aiogram.dispatcher.filters.state import StatesGroup, State

class PostForm(StatesGroup):
    video1 = State()
    name = State()
    genres = State()
    aniuRu_link = State()
    kodik_link = State()
    members = State()
    editors = State()