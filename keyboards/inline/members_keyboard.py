from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from database.requests import get_all_voice_actors, get_all_editors, get_all_tags


#Клавиатура с дабберами
async def create_members_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    members = await get_all_voice_actors()

    for member in members:
        builder.button(text=member.name, callback_data=f"member_{member.name}")

    builder.button(text="Далее ⬆️", callback_data="next")
    builder.adjust(3)
    return builder.as_markup()


#Клавиатура с монтажёрами
async def create_editors_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    editors = await get_all_editors()

    for editor in editors:
        builder.button(text=editor.name, callback_data=f"editor_{editor.name}")

    builder.button(text="Далее ⬆️", callback_data="next2")
    builder.adjust(3)
    return builder.as_markup()


async def create_tags_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    tags = await get_all_tags()

    for tag in tags:
        builder.button(text=tag.name, callback_data=f"tag|{tag.name}")

    builder.button(text="Далее ⬆️", callback_data="next3")
    builder.adjust(3)
    return builder.as_markup()


#Клавиатура подтверждения публикации
def create_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да ✅", callback_data="res_yes")
    builder.button(text="Нет ❌", callback_data="res_no")
    builder.adjust(2)
    return builder.as_markup()


inline_confirmation_kb = create_confirmation_keyboard()