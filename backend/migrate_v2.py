import sqlite3
import os

def migrate():
    db_path = "database/expenses.db"
    if not os.path.exists(db_path):
        print("Database not found, no migration needed.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Running v2 migration...")
    
    # 1. Update users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        print("Added email to users")
    except sqlite3.OperationalError: pass
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN membership_status TEXT DEFAULT 'Free'")
        print("Added membership_status to users")
    except sqlite3.OperationalError: pass

    # 2. Update goals table
    try:
        cursor.execute("ALTER TABLE goals ADD COLUMN emoji TEXT DEFAULT '💰'")
        print("Added emoji to goals")
    except sqlite3.OperationalError: pass

    # 3. Create user_settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id INTEGER PRIMARY KEY,
        dark_mode INTEGER DEFAULT 0,
        currency TEXT DEFAULT 'INR',
        budget_alerts INTEGER DEFAULT 1,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    print("Created user_settings table")
    
    conn.commit()
    conn.close()
    print("Migration v2 complete.")

if __name__ == "__main__":
    migrate()
