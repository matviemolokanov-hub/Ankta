import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ТВОЙ ТОКЕН БОТА (получить у @BotFather)
BOT_TOKEN = "8438014649:AAEFB_42u6_mAq1uViWmxPUkOi9AIgBVIYk"

# ID ГРУППЫ, КУДА БУДУТ ПРИХОДИТЬ АНКЕТЫ (можно узнать у @userinfobot)
GROUP_ID = -5296812258

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для анкеты
class Form(StatesGroup):
    waiting_for_shekels = State()
    waiting_for_age = State()
    waiting_for_pc = State()
    waiting_for_kb = State()
    waiting_for_discord = State()

# Клавиатура с вариантами ответов "Да / Нет"
def get_yes_no_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="yes"),
         InlineKeyboardButton(text="❌ Нет", callback_data="no")]
    ])

# Клавиатура для модераторов (в группе)
def get_moderation_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}"),
         InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_{user_id}")]
    ])

# Хранилище для временных данных анкеты
user_answers = {}

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await message.answer(
        "Приветствую 👋\nДля вступления в клан необходимо заполнить анкету.\n\n"
        "1) Сколько у тебя шекелей?\n"
        "Напиши число (например: 5000)"
    )
    await state.set_state(Form.waiting_for_shekels)

# Шаг 1: Шекели
@dp.message(Form.waiting_for_shekels)
async def process_shekels(message: Message, state: FSMContext):
    try:
        int(message.text)
        user_answers[message.from_user.id] = {"shekels": message.text}
        await message.answer("2) Твой возраст?\nНапиши число (например: 25)")
        await state.set_state(Form.waiting_for_age)
    except ValueError:
        await message.answer("❌ Пожалуйста, напиши число!")

# Шаг 2: Возраст
@dp.message(Form.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        int(message.text)
        user_answers[message.from_user.id]["age"] = message.text
        await message.answer(
            "3) Имеешь ли ПК или облачный телефон по типу UgPhone?\n"
            "Выбери вариант:",
            reply_markup=get_yes_no_keyboard()
        )
        await state.set_state(Form.waiting_for_pc)
    except ValueError:
        await message.answer("❌ Пожалуйста, напиши число!")

# Шаг 3: ПК/облачный телефон
@dp.callback_query(StateFilter(Form.waiting_for_pc), F.data.in_(["yes", "no"]))
async def process_pc(callback: CallbackQuery, state: FSMContext):
    user_answers[callback.from_user.id]["pc"] = "Да ✅" if callback.data == "yes" else "Нет ❌"
    await callback.message.delete()
    await callback.message.answer(
        "4) Будешь ли ты отыгрывать КБ и вкладывать по необходимости шекели для клановой битвы?\n"
        "Выбери вариант:",
        reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(Form.waiting_for_kb)
    await callback.answer()

# Шаг 4: Клановая битва
@dp.callback_query(StateFilter(Form.waiting_for_kb), F.data.in_(["yes", "no"]))
async def process_kb(callback: CallbackQuery, state: FSMContext):
    user_answers[callback.from_user.id]["kb"] = "Да ✅" if callback.data == "yes" else "Нет ❌"
    await callback.message.delete()
    await callback.message.answer(
        "5) Имеешь ли Discord?\n"
        "Выбери вариант:",
        reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(Form.waiting_for_discord)
    await callback.answer()

# Шаг 5: Discord
@dp.callback_query(StateFilter(Form.waiting_for_discord), F.data.in_(["yes", "no"]))
async def process_discord(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.full_name
    user_answers[user_id]["discord"] = "Да ✅" if callback.data == "yes" else "Нет ❌"
    
    answers = user_answers[user_id]
    
    profile_text = (
        f"📋 <b>Новая анкета!</b>\n"
        f"👤 <b>Имя:</b> {username}\n"
        f"💰 <b>Шекели:</b> {answers['shekels']}\n"
        f"🎂 <b>Возраст:</b> {answers['age']}\n"
        f"💻 <b>ПК/Облачный телефон:</b> {answers['pc']}\n"
        f"⚔️ <b>Отыгрывать КБ:</b> {answers['kb']}\n"
        f"🎮 <b>Discord:</b> {answers['discord']}"
    )
    
    await bot.send_message(
        chat_id=GROUP_ID,
        text=profile_text,
        parse_mode="HTML",
        reply_markup=get_moderation_keyboard(user_id)
    )
    
    await callback.message.delete()
    
    await callback.message.answer(
        "✅ Анкета отправлена! Ожидай решения модераторов."
    )
    
    await state.clear()
    await callback.answer()

# Обработка нажатий модераторов
@dp.callback_query(F.data.startswith("accept_"))
async def accept_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        callback.message.html_text + "\n\n✅ <b>Принято модератором!</b>",
        parse_mode="HTML"
    )
    
    await bot.send_message(
        user_id,
        "✅ Вы были приняты в клан! Вступите в наш чат: https://t.me/+Sd8sTfPW7bc1MTcy"
    )
    
    await callback.answer("✅ Пользователь принят!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        callback.message.html_text + "\n\n❌ <b>Отказано модератором!</b>",
        parse_mode="HTML"
    )
    
    await bot.send_message(
        user_id,
        "❌ Вы были не приняты в клан"
    )
    
    await callback.answer("❌ Пользователь отклонён!")

# Запуск бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())