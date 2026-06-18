from aiogram import Bot, Dispatcher, types
import asyncio

# Твой токен
TOKEN = "8438014649:AAEFB_42u6_mAq1uViWmxPUkOi9AIgBVIYk" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(message: types.Message):
    # Этот код выведет ID чата в консоль, когда ты напишешь что-то в группе
    print(f"ID этого чата: {message.chat.id}")
    await message.answer(f"ID этого чата: {message.chat.id}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
