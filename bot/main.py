
    import os
    import asyncio
    import logging
    from aiogram import Bot, Dispatcher, F
    from aiogram.types import Message
    from aiogram.filters import Command
    from bot.db import DB
    from bot.worker import Worker

    API_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    DB_PATH = os.getenv("DB_PATH", "data/bot.db")

    if not API_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set in environment variables")

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    db = DB(DB_PATH)
    worker = Worker(DB_PATH)

    # -------- Helpers --------
    async def is_activated(user_id: int) -> bool:
        row = await db.fetchone("SELECT key_used FROM users WHERE tg_id=?", (user_id,))
        return bool(row and row[0] == 1)

    # -------- Commands --------
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        # سجل المستخدم إن لم يكن موجودًا
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER UNIQUE, key_used INTEGER DEFAULT 0)")
        await db.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE, used INTEGER DEFAULT 0)")
        await db.execute("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, owner_tg_id INTEGER, status TEXT DEFAULT 'pending')")
        await db.execute("INSERT OR IGNORE INTO users (tg_id, key_used) VALUES (?, 0)", (message.from_user.id,))

        user = await db.fetchone("SELECT * FROM users WHERE tg_id=?", (message.from_user.id,))
        if user and user[2] == 1:
            await message.answer("✅ مفتاحك مُفعّل. أرسل يوزر الحساب المبند (بدون @).")
        else:
            await message.answer("👋 أهلاً! هذا البوت يتطلب مفتاح تفعيل.
"
                                 "أرسل مفتاح التفعيل الذي استلمته من الأدمن للبدء.")

    @dp.message(Command("help"))
    async def help_cmd(message: Message):
        if message.from_user.id != ADMIN_ID:
            return await message.answer("🚫 هذا الأمر مخصص للإدمن فقط.")
        await message.answer(
            "🛠 أوامر الأدمن:
"
            "/panel — عرض اللوحة
"
            "/gen_keys N — توليد N مفاتيح (استخدام مرّة واحدة)
"
            "/whoami — عرض معلوماتك
"
            "
👤 أوامر المستخدم:
"
            "/start — بدء الاستخدام
"
            "أرسل مفتاح التفعيل كنصّ، وبعد التفعيل أرسل يوزر الحساب المبند."
        )

    @dp.message(Command("whoami"))
    async def whoami(message: Message):
        await message.answer(f"📌 ID: {message.from_user.id}\n👤 Username: @{message.from_user.username or '—'}")

    @dp.message(Command("panel"))
    async def admin_panel(message: Message):
        if message.from_user.id != ADMIN_ID:
            return await message.answer("🚫 غير مسموح!")
        users_count = await db.fetchone("SELECT COUNT(*) FROM users")
        pending = await db.fetchone("SELECT COUNT(*) FROM accounts WHERE status='pending'")
        done = await db.fetchone("SELECT COUNT(*) FROM accounts WHERE status='done'")
        await message.answer(
            f"📊 لوحة التحكم:
"
            f"👥 المستخدمون: {users_count[0] if users_count else 0}
"
            f"⏳ طلبات قيد الانتظار: {pending[0] if pending else 0}
"
            f"✅ مكتمل: {done[0] if done else 0}"
        )

    @dp.message(Command("gen_keys"))
    async def generate_keys(message: Message):
        if message.from_user.id != ADMIN_ID:
            return await message.answer("🚫 غير مسموح!")
        parts = message.text.split()
        if len(parts) < 2:
            return await message.answer("استخدم: /gen_keys 5")
        try:
            count = int(parts[1])
        except ValueError:
            return await message.answer("استخدم رقمًا صالحًا: /gen_keys 5")

        keys = []
        for i in range(count):
            key = f"KEY-{message.message_id}-{i+1}"
            try:
                await db.execute("INSERT INTO keys (key, used) VALUES (?, 0)", (key,))
                keys.append(key)
            except Exception:
                # تجاهل أي تكرار نادر
                pass

        if keys:
            await message.answer("🔑 المفاتيح الجديدة (استخدام مرة واحدة فقط):\n" + "\n".join(keys))
        else:
            await message.answer("⚠️ لم أتمكن من توليد مفاتيح جديدة الآن.")

    # -------- Text handler --------
    @dp.message(F.text)
    async def text_handler(message: Message):
        text = (message.text or "").strip()

        # تجاهل الأوامر (تبدأ بـ /)
        if text.startswith("/"):
            return

        # إذا المستخدم غير مفعّل، اعتبر رسالته محاولة إدخال مفتاح
        if not await is_activated(message.from_user.id):
            valid_key = await db.fetchone("SELECT id FROM keys WHERE key=? AND used=0", (text,))
            if valid_key:
                await db.execute("UPDATE users SET key_used=1 WHERE tg_id=?", (message.from_user.id,))
                await db.execute("UPDATE keys SET used=1 WHERE key=?", (text,))
                return await message.answer("✅ تم تفعيل المفتاح! الآن أرسل يوزر الحساب المبند (بدون @).")
            else:
                return await message.answer("❌ مفتاح غير صالح أو مستخدم من قبل.
أعد المحاولة أو تواصل مع الأدمن.")

        # مستخدم مفعّل: اعتبر النص يوزرنيم للحساب المبند
        username = text.lstrip("@").strip()
        if not username or " " in username or len(username) > 32:
            return await message.answer("⚠️ اكتب يوزر صحيح بدون مسافات، مثل: username")

        await db.execute(
            "INSERT INTO accounts (username, owner_tg_id, status) VALUES (?, ?, 'pending')",
            (username, message.from_user.id)
        )
        await message.answer("✅ تم استلام طلبك. سيقوم الأدمن بمراجعته.")
        # إشعار الأدمن
        try:
            await bot.send_message(
                ADMIN_ID,
                f"🆕 طلب جديد من {message.from_user.id}\n"
                f"يوزر: @{username}"
            )
        except Exception:
            pass

    # -------- Main --------
    async def main():
        logging.basicConfig(level=logging.INFO)
        # شغّل الـ worker بالخلفية
        asyncio.create_task(worker.run(bot))
        await dp.start_polling(bot)

    if __name__ == "__main__":
        asyncio.run(main())
