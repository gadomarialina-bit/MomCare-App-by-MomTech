import sqlite3
from werkzeug.security import check_password_hash

# Connect to the database
conn = sqlite3.connect('users.db')
cur = conn.cursor()

# Get the first user
cur.execute('SELECT email, password_hash FROM users LIMIT 1')
row = cur.fetchone()
email, password_hash = row

print(f"Email: {email}")
print(f"Password Hash: {password_hash}")

# Test with various passwords
test_passwords = ['test', 'password', '123456', 'test123']

for pwd in test_passwords:
    result = check_password_hash(password_hash, pwd)
    print(f"Test '{pwd}': {result}")

conn.close()
