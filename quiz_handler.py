import json

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram import F

from aiogram.fsm.context import FSMContext; from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types; from random import sample

from questions import QUESTIONS, ANIMALS

router = Router()

class Quiz(StatesGroup):
    quest = State()
    feadback = State()
    text_to_stuff = State()

    quiz_rezult = State()
    questions = State()

#Обработчик ошибок
@router.message(Quiz.quest)
async def make_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quiz_rezult, questions = data['quiz_rezult'], data['questions']

    if message.text.strip().lower() not in ['1', '2', '3', 'начать']:
        await message.answer(f'Ошибка \n Ответ должен содержать только цифры: 1, 2, 3')
        return

    if message.text in ['1', '2', '3']:
        if message.text == '1':
            quiz_rezult['reptile'] += 1
        elif message.text == '2':
            quiz_rezult['mammal'] += 1
        elif message.text == '3':
            quiz_rezult['bird'] += 1
        await state.update_data({'quiz_rezult': quiz_rezult})

#Дополнительная информация
    if not questions:
        await state.clear()
        win_category = max(quiz_rezult, key=quiz_rezult.get)
        for category, animals in ANIMALS.items():
            if category == win_category:
                win_animal = sample(animals, 1)[0]

                rezult_message = f' Вы можете стать опекуном этого животного и войти в семью Московского Зоопарка\n' \
                                 f' Ваш возможный "питомец": <a href="{win_animal["url"]}">{win_animal["name"]}</a> 🐾 \n\n' \
                                 f' Подробнее об опекунстве: ' \
                                 f'<a href="https://moscowzoo.ru/about/guardianship">«Клуб друзей зоопарка»</a>'

                await state.set_data({'rezult_name': win_animal['name']})
                kb = [
                        [InlineKeyboardButton(text='Попробуем ещё раз?', callback_data='replay')],
                        [InlineKeyboardButton(text='Связаться с сотрудником Зоопарка', callback_data='contact')],
                        [InlineKeyboardButton(text='Поделиться в VK', callback_data='replay',
                                              url=f'https://vk.com/share.php?url={win_animal["url"]}'
                                                  f'&title=@totem_zoo_bot\nВаше тотемное животное: {win_animal["name"]}'
                                                  f'&image={win_animal["photo"]}',)],
                        [InlineKeyboardButton(text='Оставить отзыв', callback_data='feadback')]
                ]
                inlinekb = InlineKeyboardMarkup(inline_keyboard=kb)

#Окончание викторины
                await message.answer(f'Вы завершили викторину \n'
                                     f'Ваше тотемное животное: {win_animal["name"]}',
                                     reply_markup=types.ReplyKeyboardRemove())
                await message.answer_photo(photo=win_animal['photo'])

                await message.answer(rezult_message, parse_mode='HTML', reply_markup=inlinekb)

                return

    question = sample(questions, 1)[0]
    questions.pop(questions.index(question))
    answers = question['answers']
    await state. update_data({'questions': questions})
    builder = ReplyKeyboardBuilder()
    num = ['1', '2', '3']
    for _ in num:
        builder.add(types.KeyboardButton(text=_))
    builder.adjust(4)

    await message.answer(
        f"{question['question']} \n"
        f"1) {answers[0]}\n"
        f"2) {answers[1]}\n"
        f"3) {answers[2]}\n",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

#Повтор викторины
@router.callback_query(F.data == 'replay')
async def replay(callback: types.CallbackQuery, state: FSMContext):
    await state.set_data(
        {'quiz_rezult': {
            'reptile': 0,
            'mammal': 0,
            'bird': 0},
            'questions': QUESTIONS.copy()
        }
    )

#Старт викторины
    await state.set_state(Quiz.quest.state)
    kb = [[types.KeyboardButton(text='Начать')]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await callback.message.answer(f'Начнём?', reply_markup=keyboard)
    await callback.answer()

#Контакты и обратная связь
@router.callback_query(F.data == 'contact')
async def contact(callback: types.CallbackQuery, state: FSMContext):
    feadback = await state.get_data()
    buttons = [[types.KeyboardButton(text=f'Связь с сотрудником \n Результат опроса: \n{feadback}')]]
    kb = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    await callback.message.answer(f'Узнайте про программу опекунства, '
                                  f'Вы можете связаться с нами: \n\n'
                                  f' Telegram: @Moscowzoo_official\n'
                                  f' E-mail: mail@spbzoo.ru \n'
                                  f' телефон: тут должен быть номер', reply_markup=kb)
    await state.set_state(Quiz.text_to_stuff.state)
    await callback.answer()

@router.message(Quiz.text_to_stuff)
async def text_to_stuff(message: types.Message, state: FSMContext):
    await message.copy_to(chat_id=1875707606, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

#Отзыв
@router.callback_query(F.data == 'feadback')
async def feadback_state(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Quiz.feadback.state)
    await callback.message.answer(
        f'Оставьте отзыв о нашем боте. \n\n'
        f'Мы учтём ваши пожелания')
    await callback.answer()

@router.message(Quiz.feadback)
async def feadback_add(message: types.Message, state: FSMContext):
    with open('feadbacks.json', 'r', encoding='utf8') as fb_file:
        fb = json.load(fb_file)
        with open('feadbacks.json', 'w', encoding='utf8') as new_fb_file:
            new = {
                'feadback': message.text,
                'user': message.from_user.username
            }
            fb.append(new)
            new_data = json.dumps(fb, indent=4, ensure_ascii=False)
            new_fb_file.write(new_data)

    await message.answer(f'Спасибо!')
    await state.clear()