import sqlite3
import os

db_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\users.db'

def inspect():
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("--- Monthly Budgets ---")
    cur.execute("SELECT * FROM monthly_budgets")
    for r in cur.fetchall():
        print(dict(r))
        
    print("\n--- Last 5 Expenses ---")
    cur.execute("SELECT * FROM expenses ORDER BY id DESC LIMIT 5")
    for r in cur.fetchall():
        print(dict(r))
        
    print("\n--- Last 5 Groceries ---")
    cur.execute("SELECT * FROM grocery_items ORDER BY id DESC LIMIT 5")
    for r in cur.fetchall():
        print(dict(r))
        
    conn.close()

if __name__ == "__main__":
    inspect()
