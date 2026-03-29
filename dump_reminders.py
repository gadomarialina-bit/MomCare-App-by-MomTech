import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('SELECT id,user_email,title,remind_at,email_sent FROM reminder_items ORDER BY id DESC LIMIT 5')
for row in cur.fetchall():
    print(row)
conn.close()