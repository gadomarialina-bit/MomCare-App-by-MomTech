import urllib.request
import urllib.parse
import sqlite3
import datetime
import json
import http.cookiejar
from werkzeug.security import generate_password_hash

# Config
BASE_URL = "http://127.0.0.1:5002"
DB_PATH = "users.db"
TEST_EMAIL = "test_budget_sync@example.com"
TEST_PASS = "password123"

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Create/Reset test user
    cur.execute("DELETE FROM users WHERE email = ?", (TEST_EMAIL,))
    cur.execute("DELETE FROM monthly_budgets WHERE user_email = ?", (TEST_EMAIL,))
    cur.execute("DELETE FROM expenses WHERE user_email = ?", (TEST_EMAIL,))
    
    # Simple migration for verification script
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN month_iso TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN category TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN description TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN expense_date TEXT")
    except Exception:
        pass


    cur.execute("INSERT INTO users (first, last, email, birthdate, password_hash) VALUES (?, ?, ?, ?, ?)",
                ("Test", "User", TEST_EMAIL, "2000-01-01", generate_password_hash(TEST_PASS)))
    conn.commit()
    
    month_iso = datetime.datetime.now().strftime('%Y-%m')

    # 1. Set Budget
    cur.execute("INSERT INTO monthly_budgets (user_email, month_iso, income, budget_limit) VALUES (?, ?, ?, ?)",
                (TEST_EMAIL, month_iso, 2000, 1000))
                
    # 2. Add Expenses
    # Food: 200
    cur.execute("INSERT INTO expenses (user_email, month_iso, category, amount, description, expense_date) VALUES (?, ?, ?, ?, ?, ?)",
                (TEST_EMAIL, month_iso, "Food", 200, "Grcoeries", datetime.datetime.now().strftime('%Y-%m-%d')))
    # Travel: 100
    cur.execute("INSERT INTO expenses (user_email, month_iso, category, amount, description, expense_date) VALUES (?, ?, ?, ?, ?, ?)",
                (TEST_EMAIL, month_iso, "Travel", 100, "Taxi", datetime.datetime.now().strftime('%Y-%m-%d')))
                
    # Total Spent should be 300
    # Top Category should be Food
    
    conn.commit()
    conn.close()
    print("Database setup complete.")

def verify():
    # Setup cookie jar for session
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    # Login
    print("Logging in...")
    login_data = urllib.parse.urlencode({'email': TEST_EMAIL, 'password': TEST_PASS}).encode()
    try:
        r = opener.open(f"{BASE_URL}/login", data=login_data)
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 1. Check Dashboard
    print("Checking Dashboard...")
    try:
        r = opener.open(f"{BASE_URL}/dashboard")
        content = r.read().decode('utf-8')
        
        # We look for formatted values. simpler is to look for raw numbers if possible or substring matches
        if "1,000" in content or "1000" in content:
            print("PASS: Dashboard shows correct Budget Limit (1000).")
        else:
            print("FAIL: Dashboard missing Budget Limit.")
            
        if "300" in content:
             print("PASS: Dashboard shows correct Total Spent (300).")
        else:
             print("FAIL: Dashboard missing Total Spent.")
             
        if "Food" in content:
             print("PASS: Dashboard shows correct Top Category (Food).")
        else:
             print("FAIL: Dashboard missing Top Category.")
             
    except Exception as e:
        print(f"Dashboard Access failed: {e}")

    # 2. Check Budget Page
    print("Checking Budget Page...")
    try:
        r = opener.open(f"{BASE_URL}/budgetexpenses")
        content = r.read().decode('utf-8')
        
        # This page usually has input fields with values or spans
        if "2000" in content:
             print("PASS: Budget Page shows Income (2000).")
        else:
             print("FAIL: Budget Page missing Income.")
             
        if "1000" in content:
             print("PASS: Budget Page shows Budget Limit (1000).")
        else:
             print("FAIL: Budget Page missing Budget Limit.")
             
        if "300" in content:
             print("PASS: Budget Page shows Total Spent (300).")
        else:
             print("FAIL: Budget Page missing Total Spent.")

    except Exception as e:
        print(f"Budget Page Access failed: {e}")

if __name__ == "__main__":
    setup_db()
    verify()
