import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логов
logging.basicConfig(level=logging.INFO)

# ===== ВСТАВЬ СВОИ ДАННЫЕ =====
BOT_TOKEN = "8438014649:AAEFB_42u6_mAq1uViWmxPUkOi9AIgBVIYk"
GROUP_ID = -1005296812258  # ОБЯЗАТЕЛЬНО начни с -100
# ===============================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния
class Form(StatesGroup):
    waiting_for_million = State()
    waiting_for_age = State()
    waiting_for_pc = State()
    waiting_for_kb = State()
    waiting_for_discord = State()

# Клавиатуры
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

# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await message.answer(
        "👋 <b>Приветствую!</b>\nДля вступления в клан необходимо заполнить анкету.\n\n"
        "💰 <b>Вопрос 1:</b> Имеешь ли ты 1 млн шекелей?",
        parse_mode="HTML", reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(Form.waiting_for_million)

# Обработка ответов (Да/Нет)
@dp.callback_query(F.data.in_({"yes", "no"}), StateFilter(Form.waiting_for_million, Form.waiting_for_pc, Form.waiting_for_kb, Form.waiting_for_discord))
async def process_answers(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    answer_text = "Да ✅" if call.data == "yes" else "Нет ❌"
    
    # Сохраняем ответ в память FSM
    if current_state == Form.waiting_for_million:
        await state.update_data(million=answer_text)
        await call.message.edit_text("🎂 <b>Вопрос 2:</b> Твой возраст?\nНапиши число (например: 25)", parse_mode="HTML")
        await state.set_state(Form.waiting_for_age)
        
    elif current_state == Form.waiting_for_pc:
        await state.update_data(pc=answer_text)
        await call.message.edit_text("⚔️ <b>Вопрос 4:</b> Будешь отыгрывать КБ?", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
        await state.set_state(Form.waiting_for_kb)
        
    elif current_state == Form.waiting_for_kb:
        await state.update_data(kb=answer_text)
        await call.message.edit_text("🎮 <b>Вопрос 5:</b> Имеешь ли Discord?", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
        await state.set_state(Form.waiting_for_discord)
        
    elif current_state == Form.waiting_for_discord:
        await state.update_data(discord=answer_text)
        
        # Финал: собираем данные и шлем в группу
        data = await state.get_data()
        
        text = (f"📋 <b>НОВАЯ АНКЕТА!</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Имя:</b> {call.from_user.full_name}\n"
                f"💰 <b>1 млн:</b> {data.get('million')}\n"
                f"🎂 <b>Возраст:</b> {data.get('age')} лет\n"
                f"💻 <b>ПК:</b> {data.get('pc')}\n"
                f"⚔️ <b>КБ:</b> {data.get('kb')}\n"
                f"🎮 <b>Discord:</b> {answer_text}\n━━━━━━━━━━━━━━━━━━")
        
        try:
            await bot.send_message(GROUP_ID, text, parse_mode="HTML", reply_markup=get_moderation_keyboard(call.from_user.id))
            await call.message.edit_text("✅ <b>Анкета отправлена!</b>\nОжидай решения.", parse_mode="HTML")
        except Exception as e:
            logging.error(f"Ошибка отправки: {e}")
            await call.message.edit_text("❌ Произошла ошибка при отправке анкеты. Бот не в группе или нет доступа.")
        
        await state.clear()
        
    await call.answer()

@dp.message(Form.waiting_for_age)
async def age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи число!")
        return
    await state.update_data(age=message.text)
    await message.answer("💻 <b>Вопрос 3:</b> Имеешь ли ПК или облачный телефон?", parse_mode="HTML", reply_markup=get_yes_no_keyboard())
    await state.set_state(Form.waiting_for_pc)

# Модерация
@dp.callback_query(F.data.startswith("accept_"))
async def accept(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.edit_text(call.message.html_text + "\n\n✅ <b>Принято!</b>", parse_mode="HTML")
    try:
        await bot.send_message(uid, "✅ <b>Вы приняты!</b>\nВступите в чат: https://t.me/+Sd8sTfPW7bc1MTcy", parse_mode="HTML")
    except:
        pass
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.edit_text(call.message.html_text + "\n\n❌ <b>Отказано!</b>", parse_mode="HTML")
    try:
        await bot.send_message(uid, "❌ <b>Вы не приняты</b>", parse_mode="HTML")
    except:
        pass
    await call.answer()

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
