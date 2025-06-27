import sqlite3

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    phone TEXT NOT NULL,
    full_name TEXT NOT NULL
)
''')

conn.commit()
conn.close()
