import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "data/bot.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# جدول المستخدمين
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNIQUE,
    key_used INTEGER DEFAULT 0
)
""")

# جدول المفاتيح
cursor.execute("""
CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    used INTEGER DEFAULT 0
)
""")

# جدول الحسابات المبندة
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    status TEXT DEFAULT 'pending'
)
""")

conn.commit()
conn.close()
print("✅ Database migration completed successfully.")
