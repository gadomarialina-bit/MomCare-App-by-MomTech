import sqlite3
import os

def migrate_reminder_items():
    """Add email_sent column to reminder_items table if it doesn't exist"""
    db_path = os.path.join(os.path.dirname(__file__), 'momcare.db')

    if not os.path.exists(db_path):
        print("Database file not found. Migration not needed.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Check if email_sent column exists
        cur.execute("PRAGMA table_info(reminder_items)")
        columns = [column[1] for column in cur.fetchall()]

        if 'email_sent' not in columns:
            print("Adding email_sent column to reminder_items table...")
            cur.execute("ALTER TABLE reminder_items ADD COLUMN email_sent INTEGER DEFAULT 0")
            conn.commit()
            print("Migration completed successfully.")
        else:
            print("email_sent column already exists. No migration needed.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_reminder_items()