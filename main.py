import asyncio; import sys; import logging

from aiogram import Bot, Dispatcher, types; from aiogram.enums import ParseMode
from aiogram.filters import CommandStart; from aiogram.fsm.context import FSMContext

from token_data import TOKEN; from questions import QUESTIONS
from quiz_handler import router, Quiz

dp = Dispatcher()
dp.include_router(router)

bot = Bot(token=TOKEN)

#Старт, приветствие
@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext):
    await state.set_state(Quiz.quest.state)

    kb = [[types.KeyboardButton(text='Начать')]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True)
    await message.answer(f'Привет {message.from_user.first_name}{message.from_user.last_name}! \nДавайте выясним какое у, Вас, тотемное животное!', reply_markup=keyboard)

    await state.set_data(
        {'quiz_rezult': {
            'reptile': 0,
            'mammal': 0,
            'bird': 0},
            'questions': QUESTIONS.copy()
        }
    )

async def main() -> None:
    await dp.start_polling(bot)

#Конец
if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())