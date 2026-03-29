import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('users.db')
cur = conn.cursor()

# Create a test user if not exists
cur.execute('INSERT OR IGNORE INTO users (first, last, email, password_hash) VALUES (?, ?, ?, ?)',
           ('Test', 'User', 'test@example.com', 'dummy'))

# Create a test scheduled reminder for 1 minute from now
remind_time = (datetime.now() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
cur.execute('INSERT INTO reminder_items (user_email, title, message, remind_at, created_at) VALUES (?, ?, ?, ?, ?)',
           ('test@example.com', 'Test Reminder', 'This is a test scheduled reminder', remind_time, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

conn.commit()
conn.close()
print('Test scheduled reminder created for 1 minute from now')