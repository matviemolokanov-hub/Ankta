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

# ТВОЙ ТОКЕН БОТА
BOT_TOKEN = "8438014649:AAEFB_42u6_mAq1uViWmxPUkOi9AIgBVIYk"  # ← ВСТАВЬ СВОЙ ТОКЕН!

# ID ГРУППЫ
GROUP_ID = -5296812258

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для анкеты
class Form(StatesGroup):
    waiting_for_million = State()      # 1 млн шекелей
    waiting_for_age = State()          # Возраст
    waiting_for_pc = State()           # ПК/облачный телефон
    waiting_for_kb = State()           # Клановая битва
    waiting_for_discord = State()      # Discord

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
        "👋 <b>Приветствую!</b>\n"
        "Для вступления в клан необходимо заполнить анкету.\n\n"
        "💰 <b>Вопрос 1:</b> Имеешь ли ты 1 млн шекелей?\n"
        "Выбери вариант:",
        parse_mode="HTML",
        reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(Form.waiting_for_million)

# Шаг 1: 1 млн шекелей (ДА/НЕТ)
@dp.callback_query(StateFilter(Form.waiting_for_million), F.data.in_(["yes", "no"]))
async def process_million(callback: CallbackQuery, state: FSMContext):
    user_answers[callback.from_user.id] = {
        "million": "Да ✅" if callback.data == "yes" else "Нет ❌"
    }
    await callback.message.delete()
    await callback.message.answer(
        "🎂 <b>Вопрос 2:</b> Твой возраст?\n"
        "Напиши число (например: 25)",
        parse_mode="HTML"
    )
    await state.set_state(Form.waiting_for_age)
    await callback.answer()

# Шаг 2: Возраст
@dp.message(Form.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        int(message.text)
        user_answers[message.from_user.id]["age"] = message.text
        await message.answer(
            "💻 <b>Вопрос 3:</b> Имеешь ли ПК или облачный телефон по типу UgPhone?\n"
            "Выбери вариант:",
            parse_mode="HTML",
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
        "⚔️ <b>Вопрос 4:</b> Будешь ли ты отыгрывать КБ и вкладывать по необходимости шекели для клановой битвы?\n"
        "Выбери вариант:",
        parse_mode="HTML",
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
        "🎮 <b>Вопрос 5:</b> Имеешь ли Discord?\n"
        "Выбери вариант:",
        parse_mode="HTML",
        reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(Form.waiting_for_discord)
    await callback.answer()

# Шаг 5: Discord (завершение анкеты)
@dp.callback_query(StateFilter(Form.waiting_for_discord), F.data.in_(["yes", "no"]))
async def process_discord(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.full_name
    user_answers[user_id]["discord"] = "Да ✅" if callback.data == "yes" else "Нет ❌"
    
    answers = user_answers[user_id]
    
    # Формируем красивую анкету
    profile_text = (
        f"📋 <b>НОВАЯ АНКЕТА!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Имя:</b> {username}\n"
        f"💰 <b>1 млн шекелей:</b> {answers['million']}\n"
        f"🎂 <b>Возраст:</b> {answers['age']} лет\n"
        f"💻 <b>ПК/Облачный телефон:</b> {answers['pc']}\n"
        f"⚔️ <b>Отыгрывать КБ:</b> {answers['kb']}\n"
        f"🎮 <b>Discord:</b> {answers['discord']}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    # Отправляем в группу с кнопками для модерации
    await bot.send_message(
        chat_id=GROUP_ID,
        text=profile_text,
        parse_mode="HTML",
        reply_markup=get_moderation_keyboard(user_id)
    )
    
    await callback.message.delete()
    
    await callback.message.answer(
        "✅ <b>Анкета отправлена!</b>\n"
        "Ожидай решения модераторов.",
        parse_mode="HTML"
    )
    
    # Очищаем состояние
    await state.clear()
    await callback.answer()

# Обработка нажатий модераторов (в группе)
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
        "✅ <b>Вы были приняты в клан!</b>\n"
        "Вступите в наш чат: https://t.me/+Sd8sTfPW7bc1MTcy",
        parse_mode="HTML"
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
        "❌ <b>Вы были не приняты в клан</b>",
        parse_mode="HTML"
    )
    
    await callback.answer("❌ Пользователь отклонён!")

# Запуск бота
async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
