from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.member_list import members, editors

#Клавиатура с дабберами
inline_members_kb = InlineKeyboardMarkup(row_width=3)

for member in members:
    inline_members_kb.insert(InlineKeyboardButton(text=member, callback_data=member))

inline_members_kb.insert(InlineKeyboardButton(text="Далее ⬆️", callback_data="next"))


#Клавиатура с монтажёрами
inline_editors_kb = InlineKeyboardMarkup(row_width=3)

for editor in editors:
    inline_editors_kb.insert(InlineKeyboardButton(text=editor, callback_data=editor))
    
inline_editors_kb.insert(InlineKeyboardButton(text="Далее ⬆️", callback_data="next2"))


inline_confirmation_kb = InlineKeyboardMarkup(row_width=2)

inline_confirmation_kb.insert(InlineKeyboardButton(text='Да ✅', callback_data='res_yes'))
inline_confirmation_kb.insert(InlineKeyboardButton(text='Нет ❌', callback_data='res_no'))