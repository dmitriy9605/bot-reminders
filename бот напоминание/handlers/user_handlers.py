import asyncio

from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.keyboards import list_reminder_mark
from lexicon.lexicon_ru import LEXICON_RU
from shopping_reminders.shopping_list import shopping_lists
from shopping_reminders.reminders import reminders
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()

class Form(StatesGroup):
    new_shop = State()
    proc_reminder = State()

@router.message(CommandStart())
async def command_start(message: Message):
    await message.answer(LEXICON_RU['/start'], reply_markup=list_reminder_mark)


@router.message(F.text == LEXICON_RU['new_list'])
async def new_shopping_list(message:Message, state: FSMContext):
     await message.answer(
         text='Введи продукты которые нужно купить, разделяя их запятой\n'
             'Например: <b>Молоко, Хлеб, Яйца, Сыр</b>'
     )
     await state.set_state(Form.new_shop)
@router.message(Form.new_shop)
async def process_product(message:Message, state: FSMContext):
    user_id = message.from_user.id
    products = [p.strip() for p in message.text.split(',') if p.strip()]
    if products:
        shopping_lists[user_id] = products
        response = '<b>Твой список покупок:</b>\n' + '\n'.join([f'* {product} ' for product in products])
        await message.answer(text='Подготавливаю для тебя список продуктов...🖌')
        await asyncio.sleep(1)
        await message.answer(text='Готово! загружаю список...🗒')
        await message.answer(response)
        await message.answer(text='<b>А теперь установи напоминание</b> ⬇️')
    else:
        await message.answer('Ты ввел ни одного продукта. Попробуй еще раз')
    await state.clear()
@router.message(F.text == LEXICON_RU['install_reminder'])
async def set_reminder(message:Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in shopping_lists or not shopping_lists[user_id]:
        await message.answer(text='Сначала создай список покупок')
        return
    await message.answer(text='Через сколько минут тебе напомнить о покупках? ⏳')
    await state.set_state(Form.proc_reminder)

@router.message(Form.proc_reminder)
async def process_reminder_time(message:Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        minutes= int(message.text)
        if minutes <= 0:
            raise ValueError

        reminders[user_id] = {
            'products': shopping_lists[user_id].copy()
        }

        await message.answer(f'Хорошо, напомню тебе о покупках через <b>{minutes}</b> минут❗️ ')

        await asyncio.sleep(minutes * 60)

        if user_id in reminders:
            await message.answer(text =
                                 f'<b>Напоминание о покупках:</b> 🔔\n''Отметь продукты из списка ↙️' + '\n',
                                 reply_markup=inline_button(user_id)
                                )


    except ValueError:
            await message.answer('Пожалуйста, введи корректное число минут')

    await state.clear()

# Создание инлайн кнопок со списком продуктов которые ввели в функции "Новый список"
def inline_button(user_id) -> InlineKeyboardMarkup:
    products = shopping_lists[user_id]
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.row(InlineKeyboardButton(text=f'☑️{product}', callback_data=f'productList_{product}'))
    return builder.as_markup()


@router.callback_query(F.data.startswith('productList_'))
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    product = callback.data.split('_')[1]
    if user_id in shopping_lists and product in shopping_lists[user_id]:
        shopping_lists[user_id].remove(product)
        await callback.message.edit_text(
            text=f'✅{product} - отмечено как купленное!\n\n' + callback.message.text, reply_markup= inline_button(user_id))
        if not shopping_lists[user_id]:
            await callback.message.answer(text='<b>Ты отметил все продукты из списка!</b>\n\n\n'
                                               '<u><i>Были рады помочь вам!</i></u>')




