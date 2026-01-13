#!/usr/bin/env python3
"""Create reminders and reminder_items tables in users.db
Run: python3 scripts/create_reminder_tables.py
"""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'users.db'

REMINDERS_SQL = '''
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL UNIQUE,
    message TEXT,
    created_at TEXT,
    updated_at TEXT
);
'''

REMINDER_ITEMS_SQL = '''
CREATE TABLE IF NOT EXISTS reminder_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    title TEXT,
    message TEXT,
    remind_at TEXT,
    is_recurring INTEGER DEFAULT 0,
    recurrence_rule TEXT,
    created_at TEXT,
    updated_at TEXT
);
'''


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(REMINDERS_SQL)
    cur.execute(REMINDER_ITEMS_SQL)
    conn.commit()
    conn.close()
    print(f"Ensured tables created in {DB_PATH}")


if __name__ == '__main__':
    main()
