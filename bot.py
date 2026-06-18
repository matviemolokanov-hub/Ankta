import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

# ===== ДАННЫЕ =====
BOT_TOKEN = "8438014649:AAEFB_42u6_mAq1uViWmxPUkOi9AIgBVIYk"
GROUP_ID = -5296812258 
# ==================

# Настройка бота с автоматическим парсингом HTML
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

banned_users = set()

class Form(StatesGroup):
    waiting_for_million = State()
    waiting_for_age = State()
    waiting_for_kb = State()
    waiting_for_discord = State()
    waiting_for_roblox = State()
    waiting_for_proof = State()

# --- Клавиатуры ---
def get_yes_no_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="yes"),
         InlineKeyboardButton(text="❌ Нет", callback_data="no")]
    ])

def get_moderation_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}"),
         InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_{user_id}")],
        [InlineKeyboardButton(text="🚫 Забанить", callback_data=f"ban_{user_id}")]
    ])

# --- Хендлеры ---

@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    if message.from_user.id in banned_users:
        await message.answer("⛔️ Вы заблокированы.")
        return
        
    start_text = (
        "👋 <b>Приветствую!</b>\n\n"
        "<b>Что вы получите от нас ⁉️</b>\n"
        "🦝 Личный бот клана с уведомлениями о погоде и стоках\n"
        "🐙 Дружеский состав\n"
        "🐝 Розыгрыши\n"
        "🦊 Гарантированные призовые места\n\n"
        "<b>Что требуется от вас ⁉️</b>\n"
        "🦌 Возможность отыгрывать клановую битву\n"
        "🧚 1M шекелей\n"
        "🐼 Возможность отыгрывать клановую битву\n"
        "🙏 12 лет 🙏\n\n"
        "Мы не играем эту клановую битву, но мы активно начнем играть со следующей недели\n\n"
        "Вступай в ряды Ч и Манки 🐵\n\n"
        "🆘 <i>Если возникли вопросы, пиши в поддержку:</i> @t.me/dfafdafa\n\n"
        "💰 <b>Вопрос 1: Имеешь ли ты 1 млн шекелей?</b>"
    )
    
    await message.answer(start_text, reply_markup=get_yes_no_keyboard())
    await state.set_state(Form.waiting_for_million)

@dp.callback_query(F.data.in_({"yes", "no"}), StateFilter(Form.waiting_for_million, Form.waiting_for_kb, Form.waiting_for_discord))
async def process_answers(call: CallbackQuery, state: FSMContext):
    if call.from_user.id in banned_users:
        await call.message.edit_text("⛔️ Вы были заблокированы.")
        await state.clear()
        return

    current_state = await state.get_state()
    answer_text = "Да ✅" if call.data == "yes" else "Нет ❌"
    
    if current_state == Form.waiting_for_million:
        await state.update_data(million=answer_text)
        await call.message.edit_text("🎂 <b>Вопрос 2: Твой возраст?</b>")
        await state.set_state(Form.waiting_for_age)
        
    elif current_state == Form.waiting_for_kb:
        await state.update_data(kb=answer_text)
        await call.message.edit_text("🎮 <b>Вопрос 4: Имеешь ли Discord?</b>", reply_markup=get_yes_no_keyboard())
        await state.set_state(Form.waiting_for_discord)
        
    elif current_state == Form.waiting_for_discord:
        await state.update_data(discord=answer_text)
        await call.message.edit_text("🕹️ <b>Вопрос 5: Напишите свой ник в Roblox</b>")
        await state.set_state(Form.waiting_for_roblox)

    await call.answer()

@dp.message(Form.waiting_for_age)
async def age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи число!")
        return
    await state.update_data(age=message.text)
    await message.answer("⚔️ <b>Вопрос 3: Будешь отыгрывать КБ?</b>", reply_markup=get_yes_no_keyboard())
    await state.set_state(Form.waiting_for_kb)

@dp.message(Form.waiting_for_roblox)
async def roblox_nick(message: Message, state: FSMContext):
    if not message.text or len(message.text) > 50:
        await message.answer("❌ Пожалуйста, напишите ваш ник в Roblox!")
        return
        
    await state.update_data(roblox=message.text)
    
    proof_text = (
        "📸 <b>ФИНАЛЬНЫЙ ЭТАП: ПОДТВЕРЖДЕНИЕ</b>\n\n"
        "1. Зайди в игру, напиши на табличке <b>Worz</b> и сделай скриншот <b>без обрезаний</b>.\n\n"
        "👉 <b>Пришлите своё фото в ответ на это сообщение:</b>"
    )
    await message.answer(proof_text)
    await state.set_state(Form.waiting_for_proof)

@dp.message(Form.waiting_for_proof, F.photo)
async def handle_proof(message: Message, state: FSMContext):
    data = await state.get_data()
    file_id = message.photo[-1].file_id
    
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет"
    
    caption = (f"📋 <b>НОВАЯ АНКЕТА!</b>\n\n"
               f"👤 <b>Имя:</b> {message.from_user.full_name}\n"
               f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
               f"🔗 <b>Юзер:</b> {username}\n"
               f"💰 <b>1 млн:</b> {data.get('million')}\n"
               f"🎂 <b>Возраст:</b> {data.get('age')}\n"
               f"⚔️ <b>КБ:</b> {data.get('kb')}\n"
               f"🎮 <b>Discord:</b> {data.get('discord')}\n"
               f"🕹️ <b>Roblox:</b> {data.get('roblox')}\n\n"
               f"📸 <i>Доказательство от пользователя:</i>")
    
    try:
        await bot.send_photo(GROUP_ID, photo=file_id, caption=caption, reply_markup=get_moderation_keyboard(message.from_user.id))
        await message.answer("✅ <b>Анкета успешно отправлена!</b>\nОжидай решения администрации.")
    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")
        await message.answer("❌ Ошибка отправки анкеты.")
    await state.clear()

@dp.message(Form.waiting_for_proof)
async def wrong_proof(message: Message):
    await message.answer("❌ Пожалуйста, пришлите именно фото!")

# --- Модерация ---
@dp.callback_query(F.data.startswith("accept_"))
async def accept(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.message.edit_caption(caption=call.message.caption + "\n\n✅ <b>Принято!</b>", reply_markup=None)
    try: 
        await bot.send_message(uid, "✅ <b>Вы приняты в клан!</b>\nПожалуйста вступите в группу: https://t.me/+Sd8sTfPW7bc1MTcy")
    except: pass
    await call.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.message.edit_caption(caption=call.message.caption + "\n\n❌ <b>Отказано!</b>", reply_markup=None)
    try: await bot.send_message(uid, "❌ <b>Вы не приняты</b>")
    except: pass
    await call.answer()

@dp.callback_query(F.data.startswith("ban_"))
async def ban_user(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    banned_users.add(uid)
    await call.message.edit_caption(caption=call.message.caption + "\n\n🚫 <b>Пользователь забанен!</b>", reply_markup=None)
    try: await bot.send_message(uid, "🚫 <b>Вы забанены в боте.</b>")
    except: pass
    await call.answer("Пользователь заблокирован!")

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
