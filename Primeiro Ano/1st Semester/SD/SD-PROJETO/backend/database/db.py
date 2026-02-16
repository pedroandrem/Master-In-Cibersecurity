import sqlite3
from sqlite3 import Connection, Cursor

conn: Connection = sqlite3.connect("database.db")
cursor: Cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    pubkey TEXT NOT NULL,
    cert TEXT NOT NULL
)
""")

conn.commit()
conn.close()
