import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

# ===== ВСТАВЬ СВОИ ДАННЫЕ =====
BOT_TOKEN = "8438014649:AAEFB_42u6_mAq1uViWmxPUkOi9AIgBVIYk"  # Сюда свой токен
GROUP_ID = -5296812258               # Сюда ID группы
# ===============================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    waiting_for_million = State()
    waiting_for_age = State()
    waiting_for_pc = State()
    waiting_for_kb = State()
    waiting_for_discord = State()

def get_yes_no_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="yes"),
         InlineKeyboardButton(text="❌ Нет", callback_data="no")]
    ])

def get_moderation_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}"),
         InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_{user_id}")]
    ])

user_answers = {}

@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await message.answer(
        "👋 <b>Приветствую!</b>\nДля вступления в клан необходимо заполнить анкету.\n\n"
        "💰 <b>Вопрос 1:</b> Имеешь ли ты 1 млн шекелей?\nВыбери вариант:",
        parse_mode="HTML", reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(Form.waiting_for_million)

@dp.callback_query(StateFilter(Form.waiting_for_million), F.data == "yes")
async def m_yes(call: CallbackQuery, state: FSMContext):
    user_answers[call.from_user.id] = {"million": "Да ✅"}
    await call.message.delete()
    await call.message.answer("🎂 <b>Вопрос 2:</b> Твой возраст?\nНапиши число (например: 25)", parse_mode="HTML")
    await state.set_state(Form.waiting_for_age)
    await call.answer()

@dp.callback_query(StateFilter(Form.waiting_for_million), F.data == "no")
async def m_no(call: CallbackQuery, state: FSMContext):
    user_answers[call.from_user.id] = {"million": "Нет ❌"}
    await call.message.delete()
    await call.message.answer("🎂 <b>Вопрос 2:</b> Твой возраст?\nНапиши число (например: 25)", parse_mode="HTML")
    await state.set_state(Form.waiting_for_age)
    await call.answer()

@dp.message(Form.waiting_for_age)
async def age(message: Message, state: FSMContext):
    try:
        int(message.text)
        if message.from_user.id not in user_answers: user_answers[message.from_user.id] = {}
        user_answers[message.from_user.id]["age"] = message.text
        await message.answer("💻 <b>Вопрос 3:</b> Имеешь ли ПК или облачный телефон?\nВыбери вариант:", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
        await state.set_state(Form.waiting_for_pc)
    except:
        await message.answer("❌ Напиши число!")

@dp.callback_query(StateFilter(Form.waiting_for_pc), F.data == "yes")
async def pc_yes(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in user_answers: user_answers[call.from_user.id] = {}
    user_answers[call.from_user.id]["pc"] = "Да ✅"
    await call.message.delete()
    await call.message.answer("⚔️ <b>Вопрос 4:</b> Будешь отыгрывать КБ?\nВыбери вариант:", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
    await state.set_state(Form.waiting_for_kb)
    await call.answer()

@dp.callback_query(StateFilter(Form.waiting_for_pc), F.data == "no")
async def pc_no(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in user_answers: user_answers[call.from_user.id] = {}
    user_answers[call.from_user.id]["pc"] = "Нет ❌"
    await call.message.delete()
    await call.message.answer("⚔️ <b>Вопрос 4:</b> Будешь отыгрывать КБ?\nВыбери вариант:", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
    await state.set_state(Form.waiting_for_kb)
    await call.answer()

@dp.callback_query(StateFilter(Form.waiting_for_kb), F.data == "yes")
async def kb_yes(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in user_answers: user_answers[call.from_user.id] = {}
    user_answers[call.from_user.id]["kb"] = "Да ✅"
    await call.message.delete()
    await call.message.answer("🎮 <b>Вопрос 5:</b> Имеешь ли Discord?\nВыбери вариант:", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
    await state.set_state(Form.waiting_for_discord)
    await call.answer()

@dp.callback_query(StateFilter(Form.waiting_for_kb), F.data == "no")
async def kb_no(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in user_answers: user_answers[call.from_user.id] = {}
    user_answers[call.from_user.id]["kb"] = "Нет ❌"
    await call.message.delete()
    await call.message.answer("🎮 <b>Вопрос 5:</b> Имеешь ли Discord?\nВыбери вариант:", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
    await state.set_state(Form.waiting_for_discord)
    await call.answer()

# ===== ГЛАВНОЕ: ОБРАБОТЧИК ДЛЯ DISCORD (РАБОТАЕТ) =====
@dp.callback_query(StateFilter(Form.waiting_for_discord), F.data == "yes")
async def disc_yes(call: CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid not in user_answers: user_answers[uid] = {}
    user_answers[uid]["discord"] = "Да ✅"
    
    # Формируем анкету
    a = user_answers[uid]
    text = (f"📋 <b>НОВАЯ АНКЕТА!</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Имя:</b> {call.from_user.full_name}\n"
            f"💰 <b>1 млн:</b> {a.get('million', '❌')}\n"
            f"🎂 <b>Возраст:</b> {a.get('age', '❌')} лет\n"
            f"💻 <b>ПК:</b> {a.get('pc', '❌')}\n"
            f"⚔️ <b>КБ:</b> {a.get('kb', '❌')}\n"
            f"🎮 <b>Discord:</b> {a.get('discord', '❌')}\n━━━━━━━━━━━━━━━━━━")
    
    # ОТПРАВЛЯЕМ В ГРУППУ
    await bot.send_message(GROUP_ID, text, parse_mode="HTML", reply_markup=get_moderation_keyboard(uid))
    
    await call.message.delete()
    await call.message.answer("✅ <b>Анкета отправлена!</b>\nОжидай решения.", parse_mode="HTML")
    
    del user_answers[uid]
    await state.clear()
    await call.answer("Готово!")

@dp.callback_query(StateFilter(Form.waiting_for_discord), F.data == "no")
async def disc_no(call: CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid not in user_answers: user_answers[uid] = {}
    user_answers[uid]["discord"] = "Нет ❌"
    
    a = user_answers[uid]
    text = (f"📋 <b>НОВАЯ АНКЕТА!</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Имя:</b> {call.from_user.full_name}\n"
            f"💰 <b>1 млн:</b> {a.get('million', '❌')}\n"
            f"🎂 <b>Возраст:</b> {a.get('age', '❌')} лет\n"
            f"💻 <b>ПК:</b> {a.get('pc', '❌')}\n"
            f"⚔️ <b>КБ:</b> {a.get('kb', '❌')}\n"
            f"🎮 <b>Discord:</b> {a.get('discord', '❌')}\n━━━━━━━━━━━━━━━━━━")
    
    # ОТПРАВЛЯЕМ В ГРУППУ
    await bot.send_message(GROUP_ID, text, parse_mode="HTML", reply_markup=get_moderation_keyboard(uid))
    
    await call.message.delete()
    await call.message.answer("✅ <b>Анкета отправлена!</b>\nОжидай решения.", parse_mode="HTML")
    
    del user_answers[uid]
    await state.clear()
    await call.answer("Готово!")

# Модерация
@dp.callback_query(F.data.startswith("accept_"))
async def accept(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.edit_text(call.message.html_text + "\n\n✅ <b>Принято!</b>", parse_mode="HTML")
    await bot.send_message(uid, "✅ <b>Вы приняты!</b>\nВступите в чат: https://t.me/+Sd8sTfPW7bc1MTcy", parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.edit_text(call.message.html_text + "\n\n❌ <b>Отказано!</b>", parse_mode="HTML")
    await bot.send_message(uid, "❌ <b>Вы не приняты</b>", parse_mode="HTML")
    await call.answer()

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
