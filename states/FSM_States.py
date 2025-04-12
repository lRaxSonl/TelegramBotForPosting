from aiogram.fsm.state import State, StatesGroup

class PostForm(StatesGroup):
    video1 = State()
    name = State()
    genres = State()
    aniuRu_link = State()
    kodik_link = State()
    members = State()
    editors = State()
    tags = State()


class ActorFSM(StatesGroup):
    name = State()
    link = State()

class EditorFSM(StatesGroup):
    name = State()
    link = State()

class TagFSM(StatesGroup):
    name = State()


class ModeratorFSM(StatesGroup):
    tg_id = State()

class AdminFSM(StatesGroup):
    tg_id = State()