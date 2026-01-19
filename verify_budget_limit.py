import urllib.request
import urllib.parse
import json
import http.cookiejar
from datetime import datetime

# Config
BASE_URL = "http://127.0.0.1:5002"
TEST_EMAIL = "test_budget_limit@example.com"
TEST_PASS = "password123"

def verify():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    # 1. Signup/Login
    login_data = urllib.parse.urlencode({'email': TEST_EMAIL, 'password': TEST_PASS}).encode()
    signup_data = urllib.parse.urlencode({'first': 'Test', 'last': 'User', 'email': TEST_EMAIL, 'password': TEST_PASS, 'birthdate': '1990-01-01'}).encode()
    
    try:
        opener.open(f"{BASE_URL}/signup", data=signup_data)
    except Exception:
        pass

    try:
        opener.open(f"{BASE_URL}/login", data=login_data)
        print("Logged in.")
    except Exception as e:
        print("Login failed:", e)
        return

    # 2. Set Budget Limit via API (Simulate Frontend AJAX)
    today_iso = datetime.now().strftime('%Y-%m')
    settings_data = {
        "month_iso": today_iso,
        "income": 25000,
        "budget_limit": 12500
    }
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/budget-settings", 
        data=json.dumps(settings_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        resp = opener.open(req)
        print("Budget Settings Saved:", resp.getcode())
    except Exception as e:
        print("Failed to save budget settings:", e)
        return

    # 3. Check Dashboard
    try:
        resp = opener.open(f"{BASE_URL}/dashboard")
        content = resp.read().decode('utf-8')
        
        # We look for 12,500 or 12500
        if "12,500" in content or "12500" in content:
            print("PASS: Dashboard shows correct Budget Limit (12,500).")
        else:
            print("FAIL: Dashboard missing Budget Limit.")
            
    except Exception as e:
        print("Failed to access dashboard:", e)

if __name__ == "__main__":
    verify()
