from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_admin_inline_keyboard():
    builder = InlineKeyboardBuilder()


    builder.button(text="🎙 Актёры", callback_data="panel_actors")
    builder.button(text="🎞 Монтажёры", callback_data="panel_editors")
    builder.button(text="🧷 Теги", callback_data="panel_tags")

    builder.button(text="👮 Модераторы", callback_data="panel_moderators")
    builder.button(text="🕵️ Админы", callback_data="panel_admins")

    builder.adjust(2)
    return builder.as_markup()




#Actor keyboard
def create_manage_actor_inline_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="📃 Список актёров", callback_data="panel_actor_list")
    builder.button(text="✅ Добавить актёра", callback_data="panel_actor_add")
    builder.button(text="❌ Удалить актёра", callback_data="panel_actor_del")

    builder.button(text="⬅️ Назад", callback_data="back")

    builder.adjust(3)
    return builder.as_markup()



#Editor keyboard
def create_manage_editor_inline_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="📃 Список монтажёров", callback_data="panel_editor_list")
    builder.button(text="✅ Добавить монтажёра", callback_data="panel_editor_add")
    builder.button(text="❌ Удалить монтажёра", callback_data="panel_editor_del")

    builder.button(text="⬅️ Назад", callback_data="back")

    builder.adjust(3)
    return builder.as_markup()


#Tag keyboard
def create_manage_tag_inline_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="📃 Список тегов", callback_data="panel_tag_list")
    builder.button(text="✅ Добавить тег", callback_data="panel_tag_add")
    builder.button(text="❌ Удалить тег", callback_data="panel_tag_del")

    builder.button(text="⬅️ Назад", callback_data="back")

    builder.adjust(3)
    return builder.as_markup()


#Moderator keyboard
def create_manage_moderator_inline_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="📃 Список модераторов", callback_data="panel_moderator_list")
    builder.button(text="✅ Добавить модератора", callback_data="panel_moderator_add")
    builder.button(text="❌ Удалить модератора", callback_data="panel_moderator_del")

    builder.button(text="⬅️ Назад", callback_data="back")

    builder.adjust(3)
    return builder.as_markup()


#Admin keyboard
def create_manage_admin_inline_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="📃 Список админов", callback_data="panel_admin_list")
    builder.button(text="✅ Добавить админа", callback_data="panel_admin_add")
    builder.button(text="❌ Удалить админа", callback_data="panel_admin_del")

    builder.button(text="⬅️ Назад", callback_data="back")

    builder.adjust(3)
    return builder.as_markup()