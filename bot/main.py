import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("أهلا أدمن ✅\nاستخدم /help لعرض الأوامر.")
    else:
        await message.answer("أهلا بك 👋\nأنت بحاجة إلى مفتاح تفعيل لاستخدام البوت.")


@dp.message(Command("help"))
async def help_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "📌 أوامر الأدمن:\n"
            "/gen_keys <عدد> - إنشاء مفاتيح تفعيل\n"
            "/help - عرض هذه القائمة"
        )
    else:
        await message.answer("🚫 هذا الأمر مخصص للأدمن فقط.")


async def main():
    print("✅ البوت اشتغل وينتظر أوامر...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
