import sqlite3
from datetime import datetime
import smtplib
import sys

DB_PATH = 'users.db'
output = []

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check columns
cur.execute("PRAGMA table_info(tasks)")
cols = cur.fetchall()
output.append("=== tasks columns ===")
for c in cols:
    output.append(str(c))

# Check today's tasks
today_iso = datetime.now().strftime('%Y-%m-%d')
output.append(f"\n=== tasks for today ({today_iso}) ===")
cur.execute("SELECT id, user_email, title, task_date, start_time, completed, notified FROM tasks WHERE task_date = ?", (today_iso,))
rows = cur.fetchall()
if rows:
    for r in rows:
        output.append(str(r))
else:
    output.append("NO TASKS FOR TODAY")

output.append(f"\n=== ALL tasks (last 15) ===")
cur.execute("SELECT id, user_email, title, task_date, start_time, completed, notified FROM tasks ORDER BY id DESC LIMIT 15")
rows = cur.fetchall()
for r in rows:
    output.append(str(r))

conn.close()

# Test SMTP
output.append("\n=== Testing SMTP connection ===")
try:
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    server.starttls()
    server.login("kimmy.guiriba46@gmail.com", "jvuabrvpvkxwknlh")
    output.append("SMTP LOGIN SUCCESS")
    server.quit()
except Exception as e:
    output.append(f"SMTP ERROR: {e}")

result = "\n".join(output)
with open("debug_output.txt", "w") as f:
    f.write(result)
print(result)
