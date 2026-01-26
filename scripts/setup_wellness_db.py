#!/usr/bin/env python3
"""
Setup script for Mood & Wellness database tables.
Ensures daily_moods and daily_wellness tables are created in users.db.
"""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'users.db'

DAILY_MOODS_SQL = '''
CREATE TABLE IF NOT EXISTS daily_moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    date TEXT NOT NULL,
    mood TEXT,
    mood_score INTEGER,
    created_at TEXT,
    UNIQUE(user_email, date)
);
'''

DAILY_WELLNESS_SQL = '''
CREATE TABLE IF NOT EXISTS daily_wellness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    date TEXT NOT NULL,
    sleep TEXT,
    water TEXT,
    activity TEXT,
    stress INTEGER,
    created_at TEXT,
    UNIQUE(user_email, date)
);
'''

def main():
    print(f"Connecting to database at: {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Creating daily_moods table...")
    cur.execute(DAILY_MOODS_SQL)
    
    print("Creating daily_wellness table...")
    cur.execute(DAILY_WELLNESS_SQL)
    
    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == '__main__':
    main()
