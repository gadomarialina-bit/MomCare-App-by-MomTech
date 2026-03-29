import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('SELECT id, user_email, title, remind_at, email_sent FROM reminder_items')
reminders = cur.fetchall()
print('All scheduled reminders:')
for reminder in reminders:
    print(f'ID: {reminder[0]}, Email: {reminder[1]}, Title: {reminder[2]}, Remind At: {reminder[3]}, Email Sent: {reminder[4]}')
conn.close()