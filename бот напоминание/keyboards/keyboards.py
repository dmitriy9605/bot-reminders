

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_RU

nlist = KeyboardButton(text=LEXICON_RU['new_list'])
insReminder = KeyboardButton(text=LEXICON_RU['install_reminder'])


# list_reminder_mark = ReplyKeyboardMarkup(
#     keyboard=[[nlist],
#               [insReminder,mark_pur]], resize_keyboard=True)


list_reminder_mark_builder = ReplyKeyboardBuilder()
list_reminder_mark_builder.row(nlist, insReminder, width=1)

list_reminder_mark: ReplyKeyboardMarkup = list_reminder_mark_builder.as_markup(resize_keyboard=True)








